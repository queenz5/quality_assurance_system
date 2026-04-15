import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 数据查询 API
export const dataAPI = {
  getRequirements: (module = null) => 
    api.get('/api/data/requirements', { params: module ? { module } : {} }),
  getTestCases: (params = {}) => 
    api.get('/api/data/test-cases', { params }),
  getBugs: (params = {}) => 
    api.get('/api/data/bugs', { params }),
  getModules: () => 
    api.get('/api/data/modules'),
  getStatistics: () => 
    api.get('/api/data/statistics'),
};

// 质量分析 API
export const qualityAPI = {
  getAnalysis: () => 
    api.get('/api/quality/analysis'),
  getBugTrend: (days = 7) => 
    api.get('/api/quality/bug-trend', { params: { days } }),
  getBugPrediction: () => 
    api.get('/api/quality/bug-prediction'),
};

// AI 辅助测试 API
export const aiAPI = {
  analyzeBug: (bugId) =>
    api.get('/api/ai/bug-analysis', { params: { bug_id: bugId } }),
  recommendTestCases: (codeFiles, module = null) =>
    api.get('/api/ai/recommend-test-cases', {
      params: { code_files: codeFiles, ...(module ? { module } : {}) }
    }),
  analyzeRequirementImpact: (requirementContent, module = null) =>
    api.post('/api/ai/requirement-impact-analysis', {
      requirement_content: requirementContent,
      ...(module ? { module } : {})
    }),
};

// 知识管理 API
export const knowledgeAPI = {
  getTrainingMaterials: () => 
    api.get('/api/knowledge/training'),
  getHistoricalBugs: (limit = 20) => 
    api.get('/api/knowledge/historical-bugs', { params: { limit } }),
  search: (query) => 
    api.get('/api/knowledge/search', { params: { query } }),
  getQAPairs: () => 
    api.get('/api/knowledge/qa'),
};

// 智能报告 API
export const reportAPI = {
  getProjectReport: () =>
    api.get('/api/report/project'),
  getModuleReport: (module) =>
    api.get('/api/report/module', { params: { module } }),
  getAllModuleReports: () =>
    api.get('/api/report/all-modules'),
};

// 需求拆解 API
export const requirementAPI = {
  // Markdown分析 API (新)
  analyzeToMarkdown: (content, sourceName = '手动输入') =>
    api.post('/api/requirements/analyze-to-markdown', {
      content,
      source_name: sourceName
    }, {
      timeout: 180000, // 3 分钟
    }),
  getDraftMarkdown: (draftId) =>
    api.get(`/api/requirements/draft/${draftId}/markdown`),
  saveDraftMarkdown: (draftId, markdown) =>
    api.put(`/api/requirements/draft/${draftId}/markdown`, {
      markdown
    }),
  // 草稿管理 API
  getDrafts: (module = null) =>
    api.get('/api/requirements/drafts', { params: module ? { module } : {} }),
  getDraftDetail: (draftId) =>
    api.get(`/api/requirements/draft/${draftId}`),
  updateDraft: (draftId, requirements, comment = '') =>
    api.put(`/api/requirements/draft/${draftId}`, {
      requirements,
      comment
    }),
  deleteDraft: (draftId) =>
    api.delete(`/api/requirements/draft/${draftId}`),
  publishDraft: (draftId, targetDir = null) =>
    api.post(`/api/requirements/draft/${draftId}/publish`, {
      target_dir: targetDir
    }),
  // 正式需求管理 API
  getFormalRequirements: (module = null) =>
    api.get('/api/requirements/formal', { params: module ? { module } : {} }),
  getFormalRequirement: (module, fileName) =>
    api.get(`/api/requirements/formal/${module}/${fileName}`),
  updateFormalRequirement: (module, fileName, content) =>
    api.put(`/api/requirements/formal/${module}/${fileName}`, { content }),
  deleteFormalRequirement: (module, fileName) =>
    api.delete(`/api/requirements/formal/${module}/${fileName}`),
  // 旧版 API (保持向后兼容)
  getIndex: () =>
    api.get('/api/requirements/index'),
  getList: (module = null) =>
    api.get('/api/requirements/list', { params: module ? { module } : {} }),
  getDetail: (module, reqId) =>
    api.get(`/api/requirements/detail/${module}/${reqId}`),
  update: (module, reqId, content) =>
    api.put(`/api/requirements/${module}/${reqId}`, { content }),
  delete: (module, reqId) =>
    api.delete(`/api/requirements/${module}/${reqId}`),
  saveConfirmed: (requirements, saveAsDraft = true) =>
    api.post('/api/requirements/save-confirmed', {
      requirements,
      save_as_draft: saveAsDraft
    }),
  convertToFormal: (module, reqId) =>
    api.put(`/api/requirements/${module}/${reqId}/convert-to-formal`),
};

// 测试用例生成 API
export const testcaseAPI = {
  generate: (requirements, module) =>
    api.post('/api/testcases/generate', {
      requirements,
      module
    }, {
      timeout: 300000, // 5 分钟
    }),
  save: (module, testCases) =>
    api.post('/api/testcases/save', {
      module,
      test_cases: testCases
    }),
  getModules: () =>
    api.get('/api/testcases/modules'),
  // 用例草稿管理 API
  generateAndCreateDraft: (sourceType, inputText, module, selectedRequirements = []) =>
    api.post('/api/testcases/generate-and-create-draft', {
      source_type: sourceType,
      input_text: inputText,
      module,
      selected_requirements: selectedRequirements
    }, {
      timeout: 300000, // 5 分钟
    }),
  getDrafts: (module = null) =>
    api.get('/api/testcases/drafts', { params: module ? { module } : {} }),
  getDraftDetail: (draftId) =>
    api.get(`/api/testcases/draft/${draftId}`),
  getDraftTestCases: (draftId) =>
    api.get(`/api/testcases/draft/${draftId}/testcases`),
  saveDraftTestCases: (draftId, testCases) =>
    api.put(`/api/testcases/draft/${draftId}/testcases`, { test_cases: testCases }),
  deleteDraft: (draftId) =>
    api.delete(`/api/testcases/draft/${draftId}`),
  publishDraft: (draftId, module = null, submodule = null) =>
    api.post(`/api/testcases/draft/${draftId}/publish`, {
      module,
      submodule
    }),
  getModuleIndex: (module) =>
    api.get(`/api/testcases/module-index/${module}`),
  getSubmodules: (module) =>
    api.get(`/api/testcases/modules/${module}/submodules`),
  getTestCasesBySubmodule: (module, submodule) =>
    api.get(`/api/testcases/modules/${module}/submodules/${encodeURIComponent(submodule)}`),
  getTestCaseDetail: (module, submodule, caseId) =>
    api.get(`/api/testcases/cases/${module}/${encodeURIComponent(submodule)}/${caseId}`),
  updateTestCase: (module, submodule, caseId, testCase) =>
    api.put(`/api/testcases/cases/${module}/${encodeURIComponent(submodule)}/${caseId}`, { test_case: testCase }),
  deleteTestCase: (module, submodule, caseId) =>
    api.delete(`/api/testcases/cases/${module}/${encodeURIComponent(submodule)}/${caseId}`),
};

export default api;
