"""
RAG 检索模块
实现混合检索（FAISS 向量 + BM25 关键词）
用于需求影响分析和测试用例推荐
"""
import os
from typing import List, Dict, Optional
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from data.file_provider import get_data_provider
from config.llm_config import get_embeddings


class QARetriever:
    """质量保证系统 RAG 检索器"""

    def __init__(self):
        self._data_provider = get_data_provider()
        self._bm25_retriever = None
        self._faiss_retriever = None
        self._documents = []
        self._is_built = False

    def build_index(self):
        """构建检索索引"""
        self._documents = self._prepare_documents()
        
        if not self._documents:
            return

        # 1. BM25 关键词检索
        self._bm25_retriever = BM25Retriever.from_documents(
            self._documents,
            k=10
        )
        self._bm25_retriever.k = 10

        # 2. FAISS 向量检索
        # 当设置了OpenAI环境变量时启用，否则回退到仅使用BM25
        # 支持混合检索策略，结合关键词和向量检索的优势
        try:
            embeddings = get_embeddings()
            if embeddings:
                self._faiss_retriever = FAISS.from_documents(
                    self._documents,
                    embeddings
                ).as_retriever(search_kwargs={"k": 10})
                print("✅ FAISS 向量检索已启用")
        except Exception as e:
            print(f"⚠️ FAISS 初始化失败: {e}")
            print("   将仅使用 BM25 关键词检索")

        self._is_built = True

    def _prepare_documents(self) -> List[Document]:
        """准备检索文档"""
        docs = []

        # 1. 需求文档
        for req in self._data_provider.get_all_requirements():
            content = f"""需求ID: {req.id}
标题: {req.title}
模块: {req.module}
优先级: {req.priority.value}
描述: {req.description}
标签: {', '.join(req.tags)}"""
            
            docs.append(Document(
                page_content=content,
                metadata={
                    "type": "requirement",
                    "id": req.id,
                    "module": req.module,
                    "title": req.title
                }
            ))

        # 2. 测试用例
        for tc in self._data_provider.get_all_test_cases():
            content = f"""测试用例ID: {tc.id}
标题: {tc.title}
模块: {tc.module}
关联需求: {tc.requirement_id}
优先级: {tc.priority.value}
类型: {tc.status.value}
描述: {tc.description}
步骤: {'; '.join(tc.steps)}
预期结果: {tc.expected_result}"""
            
            docs.append(Document(
                page_content=content,
                metadata={
                    "type": "test_case",
                    "id": tc.id,
                    "module": tc.module,
                    "requirement_id": tc.requirement_id,
                    "title": tc.title
                }
            ))

        # 3. BUG 数据
        for bug in self._data_provider.get_all_bugs():
            content = f"""BUG ID: {bug.id}
标题: {bug.title}
模块: {bug.module}
关联需求: {bug.requirement_id}
关联用例: {bug.test_case_id or '无'}
严重程度: {bug.severity.value}
状态: {bug.status.value}
描述: {bug.description}
根因: {bug.root_cause or '未分析'}
修复方案: {bug.fix_solution or '未修复'}"""
            
            docs.append(Document(
                page_content=content,
                metadata={
                    "type": "bug",
                    "id": bug.id,
                    "module": bug.module,
                    "requirement_id": bug.requirement_id,
                    "test_case_id": bug.test_case_id,
                    "title": bug.title
                }
            ))

        return docs

    def search(self, query: str, top_k: int = 5, filter_module: Optional[str] = None) -> List[Dict]:
        """
        混合检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            filter_module: 模块过滤（可选）
            
        Returns:
            检索结果列表
        """
        if not self._is_built:
            self.build_index()

        results = []

        # 1. BM25 检索
        if self._bm25_retriever:
            bm25_docs = self._bm25_retriever.invoke(query)
            results.extend(self._format_results(bm25_docs, "bm25"))

        # 2. FAISS 向量检索
        if self._faiss_retriever:
            faiss_docs = self._faiss_retriever.invoke(query)
            results.extend(self._format_results(faiss_docs, "faiss"))

        # 3. 融合去重（RRF 算法简化版）
        return self._merge_and_deduplicate(results, top_k, filter_module)

    def _format_results(self, docs: List[Document], source: str) -> List[Dict]:
        """格式化检索结果"""
        formatted = []
        for doc in docs:
            formatted.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "source": source,
                "score": 1.0  # BM25/FAISS 分数需要进一步处理
            })
        return formatted

    def _merge_and_deduplicate(
        self, 
        results: List[Dict], 
        top_k: int,
        filter_module: Optional[str] = None
    ) -> List[Dict]:
        """融合并去重结果"""
        # 模块过滤
        if filter_module:
            results = [r for r in results if r["metadata"].get("module") == filter_module]

        # 按 ID 去重，保留最高分数
        seen = {}
        for r in results:
            doc_id = r["metadata"]["id"]
            if doc_id not in seen or r["score"] > seen[doc_id]["score"]:
                seen[doc_id] = r

        # 排序并返回 top_k
        sorted_results = sorted(seen.values(), key=lambda x: x["score"], reverse=True)
        return sorted_results[:top_k]

    def get_context_for_llm(self, query: str, top_k: int = 5) -> str:
        """
        为 LLM 生成上下文文本
        
        Args:
            query: 查询文本
            top_k: 相关文档数量
            
        Returns:
            格式化的上下文文本
        """
        results = self.search(query, top_k)
        
        if not results:
            return "未找到相关的历史数据。"

        context_parts = []
        for i, r in enumerate(results, 1):
            meta = r["metadata"]
            doc_type = meta.get("type", "unknown")
            
            if doc_type == "requirement":
                context_parts.append(f"""[历史需求 {i}]
ID: {meta['id']}
模块: {meta['module']}
标题: {meta['title']}
内容:
{r['content']}
---""")
            elif doc_type == "test_case":
                context_parts.append(f"""[历史测试用例 {i}]
ID: {meta['id']}
模块: {meta['module']}
关联需求: {meta.get('requirement_id', '未知')}
标题: {meta['title']}
内容:
{r['content']}
---""")
            elif doc_type == "bug":
                context_parts.append(f"""[历史 BUG {i}]
ID: {meta['id']}
模块: {meta['module']}
关联需求: {meta.get('requirement_id', '未知')}
严重程度: {meta.get('severity', '未知')}
内容:
{r['content']}
---""")

        return "\n\n".join(context_parts)


# 全局单例
_retriever = None

def get_retriever() -> QARetriever:
    """获取检索器实例"""
    global _retriever
    if _retriever is None:
        _retriever = QARetriever()
    return _retriever
