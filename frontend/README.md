# 质量保障系统 - 前端

基于 React + Material-UI + Recharts 的现代化前端界面。

## 🚀 快速开始

### 1. 启动后端 API

```bash
cd ../qa_system
./start.sh
```

### 2. 启动前端

```bash
./start.sh
# 或
npm install
npm run dev
```

### 3. 访问应用

打开浏览器访问: http://localhost:3000

## 📁 项目结构

```
src/
├── services/
│   └── api.js                 # API 服务封装
├── components/
│   └── Layout.jsx             # 主布局组件
├── pages/
│   ├── Dashboard.jsx          # 数据概览仪表盘
│   ├── QualityAnalysis.jsx    # 质量分析页面
│   ├── AITesting.jsx         # AI辅助测试页面
│   ├── ProcessOptimization.jsx # 流程优化页面
│   ├── KnowledgeManagement.jsx # 知识管理页面
│   ├── SmartReport.jsx        # 智能报告页面
│   └── DataManagement.jsx     # 数据管理页面
├── App.jsx                    # 应用入口
├── main.jsx                   # React 入口
└── index.css                  # 全局样式
```

## 🎨 技术栈

- **React 19** - UI 框架
- **Material-UI** - 组件库
- **Recharts** - 图表库
- **React Router 7** - 路由管理
- **Axios** - HTTP 客户端
- **Vite** - 构建工具

## 📊 页面功能

### 1. 数据概览仪表盘
- 统计卡片（模块、需求、用例、BUG）
- 质量指标展示
- 模块质量对比图表
- BUG趋势预测图表
- 模块质量详情表格

### 2. 质量分析
- 缺陷密度和覆盖率可视化
- 模块质量详细指标
- BUG趋势预测折线图
- 模块BUG预测柱状图
- 改进建议展示

### 3. AI辅助测试
- 智能用例生成（输入需求ID）
- BUG根因分析（输入BUG ID）
- 用例推荐（输入代码文件）
- 结果可视化展示

### 4. 流程优化
- 需求变更影响分析
- 测试优先级排序
- 低效用例识别
- 资源分配建议

### 5. 知识管理
- 智能搜索
- 培训材料展示
- 历史BUG案例库
- 常见问答

### 6. 智能报告
- 执行摘要
- 质量得分可视化
- 测试执行摘要
- BUG统计图表
- 高风险模块报告
- 所有模块报告

### 7. 数据管理
- 需求/用例/BUG列表
- 搜索和筛选功能
- 状态和严重程度标识

## 🔧 开发

```bash
# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 代码检查
npm run lint
```

## 🌐 API 代理

开发模式下，Vite 配置了 API 代理：
- 前端: http://localhost:3000
- 后端: http://localhost:8000
- `/api` 请求自动代理到后端

## 📱 响应式设计

- 桌面端：完整功能
- 平板端：优化布局
- 移动端：侧边栏抽屉

## 🎯 后续优化

- [ ] 添加数据导出功能
- [ ] 实时更新支持
- [ ] 国际化
- [ ] 主题切换（深色/浅色）
- [ ] 更多图表类型
- [ ] 数据编辑功能
