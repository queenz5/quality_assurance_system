"""
LLM 配置模块
提供统一的 LLM 和 Embeddings 初始化接口
兼容所有支持 OpenAI 接口协议的 LLM（通义千问、智谱、DeepSeek、Ollama 等）
"""
import os
from typing import Optional


def get_llm():
    """
    获取 LLM 实例
    """
    from langchain_openai import ChatOpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL_NAME")

    missing = []
    if not api_key:
        missing.append("OPENAI_API_KEY")
    if not base_url:
        missing.append("OPENAI_BASE_URL")
    if not model:
        missing.append("OPENAI_MODEL_NAME")

    if missing:
        raise ValueError(
            f"缺少环境变量配置: {', '.join(missing)}。请在 .env 文件中设置。"
        )

    llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.1")),
    )

    return llm


def get_embeddings():
    """
    获取 Embeddings 实例
    用于 FAISS 向量检索
    """
    try:
        from langchain_openai import OpenAIEmbeddings

        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        model = os.getenv("EMBEDDING_MODEL_NAME")

        if not api_key:
            return None
        if not base_url:
            return None
        if not model:
            return None

        embeddings = OpenAIEmbeddings(
            model=model,
            api_key=api_key,
            base_url=base_url,
        )

        return embeddings
    except Exception as e:
        print(f"⚠️ 初始化 Embeddings 失败: {e}")
        return None
