import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Alert,
  AlertTitle,
  Chip,
  CircularProgress,
  IconButton,
  Tooltip,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Save as SaveIcon,
  Publish as PublishIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Close as CloseIcon,
  Description as DocIcon,
  Folder as FolderIcon,
  Check as CheckIcon,
  AutoFixHigh as AIGenerateIcon,
  ExpandMore as ExpandMoreIcon,
  ChevronRight as ChevronRightIcon,
  Visibility as ViewIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
} from '@mui/icons-material';
import { testcaseAPI, dataAPI } from '../services/api';

export default function TestCaseGeneration() {
  // 视图模式: 'generate' | 'editor' | 'drafts' | 'formal'
  const [viewMode, setViewMode] = useState('generate');

  // 输入相关（生成模式）
  const [inputMode, setInputMode] = useState('requirement'); // 'text' | 'requirement'
  const [textContent, setTextContent] = useState('');
  const [sourceName, setSourceName] = useState('');

  // 需求选择相关（单选）
  const [modules, setModules] = useState([]);
  const [selectedModule, setSelectedModule] = useState('');
  const [requirements, setRequirements] = useState([]);
  const [selectedReqId, setSelectedReqId] = useState('');

  // 生成相关
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 测试用例数据（编辑器模式）
  const [testCases, setTestCases] = useState([]);
  const [draftId, setDraftId] = useState(null);
  const [draftInfo, setDraftInfo] = useState(null);

  // 草稿列表
  const [drafts, setDrafts] = useState([]);

  // 正式用例列表
  const [formalCases, setFormalCases] = useState([]);

  // 发布相关
  const [publishModule, setPublishModule] = useState('');
  const [publishSubmodule, setPublishSubmodule] = useState('');
  const [newSubmoduleInput, setNewSubmoduleInput] = useState('');
  const [publishDialogOpen, setPublishDialogOpen] = useState(false);
  const [newModuleInput, setNewModuleInput] = useState('');
  const [submodules, setSubmodules] = useState([]);

  // 用例管理相关状态
  const [expandedModules, setExpandedModules] = useState({});
  const [expandedSubmodules, setExpandedSubmodules] = useState({});
  const [moduleSubmodules, setModuleSubmodules] = useState({});
  const [submoduleCases, setSubmoduleCases] = useState({});
  const [selectedTestCase, setSelectedTestCase] = useState(null);
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingTestCase, setEditingTestCase] = useState(null);
  const [editingTestCaseIndex, setEditingTestCaseIndex] = useState(null);
  const [editMode, setEditMode] = useState(null);
  const [loadingCases, setLoadingCases] = useState(false);

  // 页面加载时获取数据
  useEffect(() => {
    loadModules();
    loadDrafts();
    loadFormalCases();
  }, []);

  const loadModules = async () => {
    try {
      const response = await dataAPI.getModules();
      setModules(response.data.modules || []);
    } catch (err) {
      console.error('加载模块失败:', err);
    }
  };

  const loadDrafts = async () => {
    try {
      const response = await testcaseAPI.getDrafts();
      setDrafts(response.data.drafts || []);
    } catch (err) {
      console.error('加载草稿列表失败:', err);
    }
  };

  const loadFormalCases = async () => {
    try {
      const response = await testcaseAPI.getModules();
      setFormalCases(response.data.modules || []);
    } catch (err) {
      console.error('加载正式用例失败:', err);
    }
  };

  // 加载模块下的需求
  const loadRequirements = async (module) => {
    if (!module) {
      setRequirements([]);
      return;
    }

    try {
      const response = await dataAPI.getRequirements(module);
      setRequirements(response.data.data || []);
      setSelectedReqId('');
    } catch (err) {
      console.error('加载需求失败:', err);
      setError('加载需求失败');
    }
  };

  const handleModuleChange = (event) => {
    const module = event.target.value;
    setSelectedModule(module);
    loadRequirements(module);
  };

  const loadSubmodules = async (module) => {
    if (!module) {
      setSubmodules([]);
      return;
    }
    try {
      // 从后端获取模块索引，提取子模块列表
      const response = await testcaseAPI.getModuleIndex(module);
      const moduleIndex = response.data.index || {};
      const submoduleList = Object.keys(moduleIndex.submodules || {});
      setSubmodules(submoduleList);
    } catch (err) {
      console.error('加载子模块失败:', err);
      setSubmodules([]);
    }
  };

  const handlePublishModuleChange = (event) => {
    const module = event.target.value;
    setPublishModule(module);
    setPublishSubmodule('');  // 清空子模块选择
    if (module !== '_new') {
      loadSubmodules(module);
    }
  };

  // 判断是否可以发布（一级和二级模块都已选择）
  const canPublish = (() => {
    // 一级模块必须选择
    if (!publishModule || publishModule === '_new') {
      if (publishModule === '_new' && !newModuleInput.trim()) {
        return false;
      }
      if (publishModule !== '_new') {
        return false;
      }
    }
    
    // 二级模块必须选择
    if (!publishSubmodule) {
      return false;
    }
    
    // 如果选择新建子模块，必须输入名称
    if (publishSubmodule === '_new_submodule' && !newSubmoduleInput.trim()) {
      return false;
    }
    
    return true;
  })();

  const handleReqSelect = (reqId) => {
    setSelectedReqId(reqId);
  };

  // 自动保存（防抖）
  useEffect(() => {
    if (!draftId || !testCases || testCases.length === 0 || viewMode !== 'editor') return;

    const timer = setTimeout(async () => {
      try {
        await testcaseAPI.saveDraftTestCases(draftId, testCases);
        console.log('✅ 自动保存成功');
      } catch (err) {
        console.error('自动保存失败:', err);
      }
    }, 2000);

    return () => clearTimeout(timer);
  }, [testCases, draftId, viewMode]);

  // 生成测试用例并创建草稿
  const handleGenerate = async () => {
    setLoading(true);
    setError(null);

    try {
      let sourceType, inputText, module, selectedRequirements;

      if (inputMode === 'text') {
        if (!textContent.trim()) {
          setError('请输入需求内容');
          setLoading(false);
          return;
        }
        sourceType = 'text';
        inputText = textContent;
        module = sourceName.trim() || '未分类';
        selectedRequirements = [];
      } else {
        if (!selectedReqId) {
          setError('请至少选择一个需求');
          setLoading(false);
          return;
        }
        if (!selectedModule) {
          setError('请选择模块');
          setLoading(false);
          return;
        }
        sourceType = 'requirement';
        inputText = '';
        module = selectedModule;
        selectedRequirements = requirements.filter(req => req.id === selectedReqId);
      }

      console.log('🚀 开始生成测试用例:', {
        sourceType,
        module,
        reqCount: selectedRequirements.length
      });

      // 调用生成接口（自动生成并创建草稿）
      const response = await testcaseAPI.generateAndCreateDraft(
        sourceType,
        inputText,
        module,
        selectedRequirements
      );

      console.log('✅ 生成成功:', response.data);

      // 刷新列表并跳转到草稿箱
      loadDrafts();
      setViewMode('drafts');

      // 清空输入
      setTextContent('');
      setSourceName('');
      setSelectedModule('');
      setRequirements([]);
      setSelectedReqId('');

    } catch (err) {
      console.error('❌ 生成失败:', err);
      setError(err.response?.data?.detail || err.message || '生成失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除草稿
  const handleDeleteDraft = async (draftIdToDelete, event) => {
    if (event) event.stopPropagation();
    if (!window.confirm('确定要删除这个用例草稿吗？此操作不可恢复。')) return;

    try {
      await testcaseAPI.deleteDraft(draftIdToDelete);
      loadDrafts();
      if (draftId === draftIdToDelete) {
        setTestCases([]);
        setDraftId(null);
        setDraftInfo(null);
      }
    } catch (err) {
      setError('删除失败');
    }
  };

  // 加载草稿进行编辑
  const handleEditDraft = async (draft) => {
    try {
      const response = await testcaseAPI.getDraftTestCases(draft.draft_id);
      setTestCases(response.data.test_cases || []);
      setDraftId(draft.draft_id);
      setDraftInfo(draft);
      setViewMode('editor');
    } catch (err) {
      setError('加载草稿失败');
    }
  };

  // 保存草稿
  const handleSaveTestCases = async () => {
    if (!draftId || !testCases || testCases.length === 0) {
      setError('没有可保存的测试用例');
      return;
    }

    setLoading(true);
    try {
      await testcaseAPI.saveDraftTestCases(draftId, testCases);
      loadDrafts();
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || '保存失败');
    } finally {
      setLoading(false);
    }
  };

  // 打开发布对话框
  const handlePublishClick = () => {
    if (!draftId) return;
    
    // 预填草稿中的模块信息
    setPublishModule(draftInfo?.module || '');
    setNewModuleInput(draftInfo?.module || '');
    
    // 预填草稿中的子模块信息
    const draftSubModule = draftInfo?.sub_module || '';
    setPublishSubmodule(draftSubModule);
    setNewSubmoduleInput('');
    
    setPublishDialogOpen(true);
    
    // 加载子模块列表
    if (draftInfo?.module) {
      loadSubmodules(draftInfo.module);
    }
  };

  // 发布为正式用例
  const handlePublish = async () => {
    if (!draftId) return;

    // 如果选择的是新模块，使用输入的名称
    const targetModule = publishModule === '_new' ? newModuleInput : publishModule;

    // 确定子模块
    let targetSubmodule = publishSubmodule;
    if (targetSubmodule === '_new_submodule') {
      targetSubmodule = newSubmoduleInput || undefined;
    }

    setLoading(true);
    setPublishDialogOpen(false);

    try {
      const response = await testcaseAPI.publishDraft(draftId, targetModule, targetSubmodule);

      if (response.data.success) {
        alert(`发布成功！已发布 ${response.data.saved_files?.length || 0} 条测试用例`);
        setTestCases([]);
        setDraftId(null);
        setDraftInfo(null);
        loadDrafts();
        loadFormalCases();
        setViewMode('generate');
      } else {
        setError('发布失败');
      }
    } catch (err) {
      setError(err.message || '发布失败');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setTextContent('');
    setSourceName('');
    setSelectedModule('');
    setRequirements([]);
    setSelectedReqId('');
    setError(null);
  };

  const handleNewDraft = () => {
    setTestCases([]);
    setDraftId(null);
    setDraftInfo(null);
    setError(null);
  };

  // 用例管理相关函数
  const handleModuleExpand = async (module) => {
    const newExpanded = { ...expandedModules };
    if (newExpanded[module]) {
      newExpanded[module] = false;
      setExpandedModules(newExpanded);
    } else {
      newExpanded[module] = true;
      setExpandedModules(newExpanded);
      if (!moduleSubmodules[module]) {
        try {
          const response = await testcaseAPI.getSubmodules(module);
          setModuleSubmodules(prev => ({
            ...prev,
            [module]: response.data.submodules || []
          }));
        } catch (err) {
          console.error('加载子模块失败:', err);
        }
      }
    }
  };

  const handleSubmoduleExpand = async (module, submodule) => {
    const key = `${module}-${submodule}`;
    const newExpanded = { ...expandedSubmodules };
    if (newExpanded[key]) {
      newExpanded[key] = false;
      setExpandedSubmodules(newExpanded);
    } else {
      newExpanded[key] = true;
      setExpandedSubmodules(newExpanded);
      if (!submoduleCases[key]) {
        setLoadingCases(true);
        try {
          const response = await testcaseAPI.getTestCasesBySubmodule(module, submodule);
          setSubmoduleCases(prev => ({
            ...prev,
            [key]: response.data.test_cases || []
          }));
        } catch (err) {
          console.error('加载用例列表失败:', err);
        } finally {
          setLoadingCases(false);
        }
      }
    }
  };

  const handleViewTestCase = async (module, submodule, caseId) => {
    try {
      const response = await testcaseAPI.getTestCaseDetail(module, submodule, caseId);
      setSelectedTestCase(response.data.test_case);
      setPreviewDialogOpen(true);
    } catch (err) {
      setError('加载用例详情失败');
    }
  };

  const handleEditTestCase = async (module, submodule, caseId) => {
    try {
      const response = await testcaseAPI.getTestCaseDetail(module, submodule, caseId);
      setEditingTestCase(response.data.test_case);
      setEditingTestCaseIndex(null);
      setEditMode('formal');
      setEditDialogOpen(true);
    } catch (err) {
      setError('加载用例详情失败');
    }
  };

  const handleSaveTestCase = async () => {
    if (!editingTestCase) return;
    setLoading(true);
    try {
      if (editMode === 'draft') {
        const newTestCases = [...testCases];
        if (editingTestCaseIndex !== null && editingTestCaseIndex >= 0) {
          newTestCases[editingTestCaseIndex] = editingTestCase;
        }
        setTestCases(newTestCases);
        setEditDialogOpen(false);
        setEditingTestCase(null);
        setEditingTestCaseIndex(null);
        setEditMode(null);
      } else if (editMode === 'formal') {
        const module = editingTestCase.module;
        const submodule = editingTestCase.sub_module;
        const caseId = editingTestCase.id;
        await testcaseAPI.updateTestCase(module, submodule, caseId, editingTestCase);
        setEditDialogOpen(false);
        setEditingTestCase(null);
        setEditingTestCaseIndex(null);
        setEditMode(null);
        const key = `${module}-${submodule}`;
        const response = await testcaseAPI.getTestCasesBySubmodule(module, submodule);
        setSubmoduleCases(prev => ({
          ...prev,
          [key]: response.data.test_cases || []
        }));
      }
    } catch (err) {
      setError(err.response?.data?.detail || '保存用例失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTestCase = async (module, submodule, caseId) => {
    if (!window.confirm(`确定要删除测试用例 ${caseId} 吗？此操作不可恢复。`)) return;
    setLoading(true);
    try {
      await testcaseAPI.deleteTestCase(module, submodule, caseId);
      const key = `${module}-${submodule}`;
      const response = await testcaseAPI.getTestCasesBySubmodule(module, submodule);
      setSubmoduleCases(prev => ({
        ...prev,
        [key]: response.data.test_cases || []
      }));
    } catch (err) {
      setError(err.response?.data?.detail || '删除用例失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      {/* 顶部工具栏 */}
      <Box sx={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        mb: 3,
        p: 2,
        bgcolor: 'background.paper',
        borderRadius: 2,
        boxShadow: 1
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            测试用例
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant={viewMode === 'generate' ? 'contained' : 'outlined'}
              size="small"
              onClick={() => setViewMode('generate')}
              startIcon={<AIGenerateIcon />}
            >
              用例生成
            </Button>
            <Button
              variant={viewMode === 'drafts' ? 'contained' : 'outlined'}
              size="small"
              onClick={() => setViewMode('drafts')}
              startIcon={<DocIcon />}
            >
              草稿箱 ({drafts.length})
            </Button>
            <Button
              variant={viewMode === 'formal' ? 'contained' : 'outlined'}
              size="small"
              onClick={() => setViewMode('formal')}
              startIcon={<FolderIcon />}
            >
              用例管理
            </Button>
          </Box>
        </Box>

        {viewMode === 'editor' && draftId && (
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip
              label={`草稿: ${draftId}`}
              size="small"
              color="primary"
              variant="outlined"
            />
            {draftInfo && (
              <Chip
                label={`${draftInfo.module}${draftInfo.sub_module ? `/${draftInfo.sub_module}` : ''} · ${draftInfo.total_test_cases || 0} 条用例`}
                size="small"
                variant="outlined"
              />
            )}
            <Button
              variant="contained"
              size="small"
              onClick={handleSaveTestCases}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={16} /> : <SaveIcon />}
            >
              保存
            </Button>
            <Button
              variant="contained"
              size="small"
              color="success"
              onClick={handlePublishClick}
              disabled={loading}
              startIcon={<PublishIcon />}
            >
              发布
            </Button>
          </Box>
        )}
      </Box>

      {/* 错误提示 */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          <AlertTitle>错误</AlertTitle>
          {error}
        </Alert>
      )}

      {/* 生成模式 */}
      {viewMode === 'generate' && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">输入需求</Typography>
              <Chip label="生成后自动保存为草稿" color="info" size="small" />
            </Box>

            <Tabs value={inputMode} onChange={(e, val) => setInputMode(val)} sx={{ mb: 3 }}>
              <Tab label="选择需求" value="requirement" />
              <Tab label="文本输入" value="text" />
            </Tabs>

            {/* 选择需求模式 */}
            {inputMode === 'requirement' && (
              <Box>
                <Alert severity="info" sx={{ mb: 2 }}>
                  从已有需求中选择一个要生成测试用例的项。
                </Alert>

                <FormControl fullWidth sx={{ mb: 3 }}>
                  <InputLabel>选择模块</InputLabel>
                  <Select
                    value={selectedModule}
                    label="选择模块"
                    onChange={handleModuleChange}
                  >
                    {modules.map((module) => (
                      <MenuItem key={module} value={module}>
                        {module}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                {requirements.length > 0 && (
                  <>
                    <Typography variant="subtitle2" sx={{ mb: 2 }}>
                      需求列表（请选择一个需求）
                    </Typography>

                    <TableContainer component={Paper} variant="outlined">
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell padding="checkbox" />
                            <TableCell>需求ID</TableCell>
                            <TableCell>需求标题</TableCell>
                            <TableCell>优先级</TableCell>
                            <TableCell>状态</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {requirements.map((req) => (
                            <TableRow
                              key={req.id}
                              hover
                              selected={selectedReqId === req.id}
                              onClick={() => handleReqSelect(req.id)}
                              sx={{ cursor: 'pointer' }}
                            >
                              <TableCell padding="checkbox">
                                <Checkbox
                                  checked={selectedReqId === req.id}
                                  color="primary"
                                />
                              </TableCell>
                              <TableCell>
                                <Chip label={req.id} size="small" variant="outlined" />
                              </TableCell>
                              <TableCell>{req.title}</TableCell>
                              <TableCell>
                                <Chip
                                  label={req.priority}
                                  size="small"
                                  color={req.priority === '高' ? 'error' : req.priority === '中' ? 'warning' : 'success'}
                                />
                              </TableCell>
                              <TableCell>{req.status}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </>
                )}
              </Box>
            )}

            {/* 文本输入模式 */}
            {inputMode === 'text' && (
              <Box>
                <Alert severity="info" sx={{ mb: 2 }}>
                  复制需求文档内容（支持任何格式），粘贴到下方即可。AI 会自动生成测试用例并保存为草稿。
                </Alert>
                <TextField
                  fullWidth
                  label="来源名称（可选）"
                  placeholder="例如：用户管理模块需求 v1.0"
                  value={sourceName}
                  onChange={(e) => setSourceName(e.target.value)}
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  multiline
                  rows={12}
                  label="需求文档内容"
                  placeholder="粘贴需求文档内容..."
                  value={textContent}
                  onChange={(e) => setTextContent(e.target.value)}
                />
              </Box>
            )}

            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                size="large"
                onClick={handleGenerate}
                disabled={loading || (inputMode === 'text' ? !textContent.trim() : !selectedReqId)}
                startIcon={loading ? <CircularProgress size={20} /> : <AIGenerateIcon />}
              >
                {loading ? 'AI 生成中...（可能需要 1-2 分钟）' : '开始生成'}
              </Button>
              <Button variant="outlined" onClick={handleReset}>
                重置
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* 编辑器模式（仅从草稿箱点击编辑时进入） */}
      {viewMode === 'editor' && (
        <Box>
          {draftInfo && (
            <Alert severity="info" sx={{ mb: 2 }}>
              <AlertTitle>草稿信息</AlertTitle>
              <Typography variant="body2">
                模块: {draftInfo.module}{draftInfo.sub_module ? ` / ${draftInfo.sub_module}` : ''} | 用例数: {testCases.length || 0} |
                来源: {draftInfo.source_type === 'text' ? '文本输入' : '选择需求'}
              </Typography>
            </Alert>
          )}

          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">测试用例列表</Typography>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<AddIcon />}
                  onClick={() => {
                    const newCase = {
                      id: `TC-NEW-${Date.now()}`,
                      title: '新测试用例',
                      description: '',
                      priority: '中',
                      status: '未执行',
                      case_type: '基本功能',
                      requirement_id: '',
                      preconditions: [],
                      steps: [],
                      expected_result: '',
                      tags: [],
                      updated_at: new Date().toISOString()
                    };
                    setTestCases([...testCases, newCase]);
                  }}
                >
                  添加用例
                </Button>
              </Box>

              {testCases.length === 0 ? (
                <Alert severity="info">暂无测试用例</Alert>
              ) : (
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ width: '12%', whiteSpace: 'nowrap' }}>用例ID</TableCell>
                        <TableCell sx={{ width: '28%' }}>标题</TableCell>
                        <TableCell sx={{ width: '10%', whiteSpace: 'nowrap' }}>类型</TableCell>
                        <TableCell sx={{ width: '8%', whiteSpace: 'nowrap' }}>优先级</TableCell>
                        <TableCell sx={{ width: '12%', whiteSpace: 'nowrap' }}>关联需求</TableCell>
                        <TableCell sx={{ width: '15%', whiteSpace: 'nowrap' }}>更新时间</TableCell>
                        <TableCell sx={{ width: '15%' }} align="center">操作</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {testCases.map((tc, index) => (
                        <TableRow key={tc.id || index} hover>
                          <TableCell>
                            <Chip label={tc.id} size="small" variant="outlined" />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" noWrap>
                              {tc.title}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">{tc.case_type || '-'}</Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={tc.priority || '中'}
                              size="small"
                              color={
                                tc.priority === '高' ? 'error' :
                                tc.priority === '中' ? 'warning' : 'success'
                              }
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={tc.requirement_id || '-'}
                              size="small"
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {tc.updated_at ? new Date(tc.updated_at).toLocaleDateString('zh-CN', {
                                year: 'numeric', month: '2-digit', day: '2-digit'
                              }) : '-'}
                            </Typography>
                          </TableCell>
                          <TableCell align="center" sx={{ whiteSpace: 'nowrap' }}>
                            <Tooltip title="编辑">
                              <IconButton
                                size="small"
                                onClick={() => {
                                  setEditingTestCase({ ...tc });
                                  setEditingTestCaseIndex(index);
                                  setEditMode('draft');
                                  setEditDialogOpen(true);
                                }}
                              >
                                <EditIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="删除">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => {
                                  if (window.confirm('确定要删除这个测试用例吗？')) {
                                    const newCases = testCases.filter((_, i) => i !== index);
                                    setTestCases(newCases);
                                  }
                                }}
                              >
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>

          <Box sx={{ display: 'flex', gap: 2, mt: 2, justifyContent: 'space-between' }}>
            <Box>
              <Button variant="outlined" onClick={() => setViewMode('generate')} startIcon={<AIGenerateIcon />} sx={{ mr: 1 }}>
                用例生成
              </Button>
              <Button variant="outlined" onClick={() => setViewMode('drafts')} startIcon={<DocIcon />}>
                返回草稿箱
              </Button>
            </Box>
            <Box>
              <Button
                variant="contained"
                onClick={handleSaveTestCases}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
                sx={{ mr: 1 }}
              >
                保存草稿
              </Button>
              <Button
                variant="contained"
                color="success"
                onClick={handlePublishClick}
                disabled={loading}
                startIcon={<PublishIcon />}
              >
                发布为正式用例
              </Button>
            </Box>
          </Box>
        </Box>
      )}

      {/* 草稿箱视图 */}
      {viewMode === 'drafts' && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">用例草稿箱</Typography>
              <Box>
                <Button
                  variant="outlined"
                  startIcon={<AIGenerateIcon />}
                  onClick={() => setViewMode('generate')}
                  size="small"
                  sx={{ mr: 1 }}
                >
                  用例生成
                </Button>
                <Button startIcon={<RefreshIcon />} onClick={loadDrafts} size="small" sx={{ mr: 1 }}>
                  刷新
                </Button>
              </Box>
            </Box>

            {drafts.length === 0 ? (
              <Alert severity="info">暂无草稿。点击上方"生成用例"开始创建。</Alert>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>标题</TableCell>
                      <TableCell>模块</TableCell>
                      <TableCell>用例数</TableCell>
                      <TableCell>来源</TableCell>
                      <TableCell>更新时间</TableCell>
                      <TableCell align="right">操作</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {drafts.map((draft) => (
                      <TableRow
                        key={draft.draft_id}
                        hover
                        sx={{ cursor: 'pointer' }}
                        onClick={() => handleEditDraft(draft)}
                      >
                        <TableCell>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {draft.title || draft.draft_id}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {draft.draft_id}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={draft.module || '未分类'}
                            size="small"
                            variant="outlined"
                            color={draft.module && draft.module !== '未分类' ? 'primary' : 'default'}
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={`${draft.total_test_cases || 0} 条`}
                            size="small"
                            color="success"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={draft.source_type === 'text' ? '文本输入' : '选择需求'}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          {draft.updated_at ? new Date(draft.updated_at).toLocaleDateString('zh-CN', {
                            year: 'numeric', month: '2-digit', day: '2-digit'
                          }) : '-'}
                        </TableCell>
                        <TableCell align="right" onClick={(e) => e.stopPropagation()}>
                          <Tooltip title="编辑">
                            <IconButton size="small" onClick={() => handleEditDraft(draft)}>
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="删除">
                            <IconButton size="small" onClick={(e) => handleDeleteDraft(draft.draft_id, e)}>
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      )}

      {/* 正式用例视图 - 用例管理 */}
      {viewMode === 'formal' && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">用例管理</Typography>
              <Button startIcon={<RefreshIcon />} onClick={loadFormalCases} size="small">
                刷新
              </Button>
            </Box>

            {formalCases.length === 0 ? (
              <Alert severity="info">
                暂无正式用例。请先创建草稿并发布为正式用例。
              </Alert>
            ) : (
              <Box>
                {formalCases.map((moduleData) => (
                  <Box key={moduleData.module} sx={{ mb: 1 }}>
                    {/* 一级模块 */}
                    <Paper
                      variant="outlined"
                      sx={{
                        p: 1.5,
                        cursor: 'pointer',
                        bgcolor: expandedModules[moduleData.module] ? 'action.hover' : 'background.paper',
                        '&:hover': { bgcolor: 'action.hover' }
                      }}
                      onClick={() => handleModuleExpand(moduleData.module)}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {expandedModules[moduleData.module] ? (
                            <RemoveIcon fontSize="small" color="primary" />
                          ) : (
                            <AddIcon fontSize="small" />
                          )}
                          <FolderIcon fontSize="small" color="primary" />
                          <Typography variant="subtitle1" sx={{ fontWeight: 500 }}>
                            {moduleData.module}
                          </Typography>
                        </Box>
                        <Chip
                          label={`${moduleData.total_test_cases || 0} 条用例`}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      </Box>
                    </Paper>

                    {/* 二级模块列表 */}
                    {expandedModules[moduleData.module] && (
                      <Box sx={{ pl: 3, mt: 1 }}>
                        {moduleSubmodules[moduleData.module]?.length > 0 ? (
                          moduleSubmodules[moduleData.module].map((sub) => {
                            const subKey = `${moduleData.module}-${sub.name}`;
                            return (
                              <Box key={sub.name} sx={{ mb: 1 }}>
                                {/* 二级模块 */}
                                <Paper
                                  variant="outlined"
                                  sx={{
                                    p: 1,
                                    cursor: 'pointer',
                                    bgcolor: expandedSubmodules[subKey] ? 'grey.100' : 'background.paper',
                                    '&:hover': { bgcolor: 'grey.100' }
                                  }}
                                  onClick={() => handleSubmoduleExpand(moduleData.module, sub.name)}
                                >
                                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                      {expandedSubmodules[subKey] ? (
                                        <ExpandMoreIcon fontSize="small" />
                                      ) : (
                                        <ChevronRightIcon fontSize="small" />
                                      )}
                                      <DocIcon fontSize="small" color="action" />
                                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                        {sub.name}
                                      </Typography>
                                    </Box>
                                    <Chip
                                      label={`${sub.case_count} 条`}
                                      size="small"
                                      variant="outlined"
                                    />
                                  </Box>
                                </Paper>

                                {/* 用例列表 */}
                                {expandedSubmodules[subKey] && (
                                  <Box sx={{ pl: 2, mt: 1 }}>
                                    {loadingCases ? (
                                      <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                                        <CircularProgress size={24} />
                                      </Box>
                                    ) : submoduleCases[subKey]?.length > 0 ? (
                                      <TableContainer component={Paper} variant="outlined" size="small">
                                        <Table size="small">
                                          <TableHead>
                                            <TableRow>
                                              <TableCell sx={{ width: '12%', whiteSpace: 'nowrap' }}>用例ID</TableCell>
                                              <TableCell sx={{ width: '28%' }}>标题</TableCell>
                                              <TableCell sx={{ width: '10%', whiteSpace: 'nowrap' }}>类型</TableCell>
                                              <TableCell sx={{ width: '8%', whiteSpace: 'nowrap' }}>优先级</TableCell>
                                              <TableCell sx={{ width: '12%', whiteSpace: 'nowrap' }}>关联需求</TableCell>
                                              <TableCell sx={{ width: '15%', whiteSpace: 'nowrap' }}>更新时间</TableCell>
                                              <TableCell sx={{ width: '15%' }} align="center">操作</TableCell>
                                            </TableRow>
                                          </TableHead>
                                          <TableBody>
                                            {submoduleCases[subKey].map((tc) => (
                                              <TableRow key={tc.id} hover>
                                                <TableCell>
                                                  <Chip label={tc.id} size="small" variant="outlined" />
                                                </TableCell>
                                                <TableCell>
                                                  <Typography variant="body2" noWrap>
                                                    {tc.title}
                                                  </Typography>
                                                </TableCell>
                                                <TableCell>
                                                  <Typography variant="body2">{tc.case_type || '-'}</Typography>
                                                </TableCell>
                                                <TableCell>
                                                  <Chip
                                                    label={tc.priority || '中'}
                                                    size="small"
                                                    color={
                                                      tc.priority === '高' ? 'error' :
                                                      tc.priority === '中' ? 'warning' : 'success'
                                                    }
                                                  />
                                                </TableCell>
                                                <TableCell>
                                                  <Chip
                                                    label={tc.requirement_id || '-'}
                                                    size="small"
                                                    variant="outlined"
                                                  />
                                                </TableCell>
                                                <TableCell>
                                                  <Typography variant="body2">
                                                    {tc.updated_at ? new Date(tc.updated_at).toLocaleDateString('zh-CN', {
                                                      year: 'numeric', month: '2-digit', day: '2-digit'
                                                    }) : '-'}
                                                  </Typography>
                                                </TableCell>
                                                <TableCell align="center" sx={{ whiteSpace: 'nowrap' }}>
                                                  <Tooltip title="预览">
                                                    <IconButton
                                                      size="small"
                                                      onClick={() => handleViewTestCase(moduleData.module, sub.name, tc.id)}
                                                    >
                                                      <ViewIcon fontSize="small" />
                                                    </IconButton>
                                                  </Tooltip>
                                                  <Tooltip title="编辑">
                                                    <IconButton
                                                      size="small"
                                                      onClick={() => handleEditTestCase(moduleData.module, sub.name, tc.id)}
                                                    >
                                                      <EditIcon fontSize="small" />
                                                    </IconButton>
                                                  </Tooltip>
                                                  <Tooltip title="删除">
                                                    <IconButton
                                                      size="small"
                                                      color="error"
                                                      onClick={() => handleDeleteTestCase(moduleData.module, sub.name, tc.id)}
                                                    >
                                                      <DeleteIcon fontSize="small" />
                                                    </IconButton>
                                                  </Tooltip>
                                                </TableCell>
                                              </TableRow>
                                            ))}
                                          </TableBody>
                                        </Table>
                                      </TableContainer>
                                    ) : (
                                      <Alert severity="info" sx={{ mt: 1 }}>
                                        该子模块下暂无用例
                                      </Alert>
                                    )}
                                  </Box>
                                )}
                              </Box>
                            );
                          })
                        ) : (
                          <Alert severity="info" sx={{ mt: 1 }}>
                            该模块下暂无子模块
                          </Alert>
                        )}
                      </Box>
                    )}
                  </Box>
                ))}
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* 发布对话框 */}
      <Dialog open={publishDialogOpen} onClose={() => setPublishDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>发布为正式用例</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            请选择要将用例发布到哪个模块和子模块。如果模块不存在，将会自动创建。
          </Typography>
          
          {/* 一级模块选择 */}
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>一级模块 <span style={{color: 'red'}}>*</span></InputLabel>
            <Select
              value={publishModule}
              label="一级模块 *"
              onChange={(e) => {
                const value = e.target.value;
                setPublishModule(value);
                if (value === '_new') {
                  // 选择新模块时，自动设置为新建子模块模式
                  setNewModuleInput(draftInfo?.module || '');
                  setPublishSubmodule('_new_submodule');
                  // 自动填充草稿中的子模块名称
                  setNewSubmoduleInput(draftInfo?.sub_module || '');
                  setSubmodules([]);
                } else {
                  // 选择已有模块时，清空子模块并加载子模块列表
                  setPublishSubmodule('');
                  setNewSubmoduleInput('');
                  loadSubmodules(value);
                }
              }}
            >
              {formalCases.map((moduleData) => (
                <MenuItem key={moduleData.module} value={moduleData.module}>
                  {moduleData.module}
                </MenuItem>
              ))}
              <MenuItem value="_new">+ 新模块（手动输入名称）</MenuItem>
            </Select>
          </FormControl>

          {/* 新模块名称输入 */}
          {publishModule === '_new' && (
            <TextField
              fullWidth
              label="输入新模块名称 *"
              value={newModuleInput}
              onChange={(e) => setNewModuleInput(e.target.value)}
              placeholder="请输入模块名称"
              required
              sx={{ mb: 2 }}
            />
          )}

          {/* 二级模块选择 - 选择已有模块时显示下拉框 */}
          {publishModule !== '_new' && (
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>二级模块 <span style={{color: 'red'}}>*</span></InputLabel>
              <Select
                value={publishSubmodule}
                label="二级模块 *"
                onChange={(e) => {
                  const value = e.target.value;
                  setPublishSubmodule(value);
                  // 当选择新建子模块时，自动填充草稿中的子模块名称
                  if (value === '_new_submodule') {
                    setNewSubmoduleInput(draftInfo?.sub_module || '');
                  } else {
                    setNewSubmoduleInput('');
                  }
                }}
              >
                {submodules.map((sub) => (
                  <MenuItem key={sub} value={sub}>
                    {sub}
                  </MenuItem>
                ))}
                <MenuItem value="_new_submodule">+ 新建子模块</MenuItem>
              </Select>
            </FormControl>
          )}

          {/* 新建子模块名称输入 - 选择新模块或选择新建子模块时显示 */}
          {(publishModule === '_new' || publishSubmodule === '_new_submodule') && (
            <TextField
              fullWidth
              label="输入新子模块名称 *"
              value={newSubmoduleInput}
              onChange={(e) => setNewSubmoduleInput(e.target.value)}
              placeholder="例如：Icon 图标"
              required
              sx={{ mb: 2 }}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPublishDialogOpen(false)}>取消</Button>
          <Button
            variant="contained"
            onClick={handlePublish}
            disabled={loading || !canPublish}
            startIcon={loading ? <CircularProgress size={20} /> : <PublishIcon />}
          >
            {loading ? '发布中...' : '确认发布'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 用例预览对话框 */}
      <Dialog 
        open={previewDialogOpen} 
        onClose={() => setPreviewDialogOpen(false)} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">用例详情</Typography>
            <IconButton onClick={() => setPreviewDialogOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {selectedTestCase && (
            <Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">用例ID</Typography>
                <Chip label={selectedTestCase.id} size="small" color="primary" />
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">标题</Typography>
                <Typography variant="body1">{selectedTestCase.title}</Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 3, mb: 2 }}>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">模块</Typography>
                  <Typography variant="body2">{selectedTestCase.module}</Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">子模块</Typography>
                  <Typography variant="body2">{selectedTestCase.sub_module || '-'}</Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', gap: 3, mb: 2 }}>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">优先级</Typography>
                  <Chip 
                    label={selectedTestCase.priority || '中'} 
                    size="small"
                    color={selectedTestCase.priority === '高' ? 'error' : selectedTestCase.priority === '中' ? 'warning' : 'success'}
                  />
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">状态</Typography>
                  <Chip label={selectedTestCase.status || '未执行'} size="small" variant="outlined" />
                </Box>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">用例类型</Typography>
                  <Typography variant="body2">{selectedTestCase.case_type || '-'}</Typography>
                </Box>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">关联需求</Typography>
                <Chip label={selectedTestCase.requirement_id || '-'} size="small" variant="outlined" />
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">描述</Typography>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                  {selectedTestCase.description || '-'}
                </Typography>
              </Box>
              {selectedTestCase.preconditions && selectedTestCase.preconditions.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">前置条件</Typography>
                  <Box component="ul" sx={{ pl: 2, m: 0 }}>
                    {selectedTestCase.preconditions.map((cond, idx) => (
                      <li key={idx}><Typography variant="body2">{cond}</Typography></li>
                    ))}
                  </Box>
                </Box>
              )}
              {selectedTestCase.steps && selectedTestCase.steps.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">测试步骤</Typography>
                  <TableContainer component={Paper} variant="outlined" size="small" sx={{ mt: 1 }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell width="10%">步骤</TableCell>
                          <TableCell width="30%">操作</TableCell>
                          <TableCell width="30%">输入</TableCell>
                          <TableCell width="30%">预期结果</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {selectedTestCase.steps.map((step, idx) => (
                          <TableRow key={idx}>
                            <TableCell>{idx + 1}</TableCell>
                            <TableCell>
                              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem' }}>
                                {typeof step === 'string' ? step : step.action || '-'}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem' }}>
                                {typeof step === 'string' ? '-' : step.input || '-'}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem' }}>
                                {typeof step === 'string' ? '-' : step.expected || '-'}
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              )}
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">预期结果</Typography>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                  {selectedTestCase.expected_result || '-'}
                </Typography>
              </Box>
              {selectedTestCase.test_data && Object.keys(selectedTestCase.test_data).length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">测试数据</Typography>
                  <Paper variant="outlined" sx={{ p: 1, mt: 1, bgcolor: 'grey.50' }}>
                    <pre style={{ margin: 0, fontSize: '0.85rem', overflow: 'auto' }}>
                      {JSON.stringify(selectedTestCase.test_data, null, 2)}
                    </pre>
                  </Paper>
                </Box>
              )}
              {selectedTestCase.tags && selectedTestCase.tags.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">标签</Typography>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
                    {selectedTestCase.tags.map((tag, idx) => (
                      <Chip key={idx} label={tag} size="small" variant="outlined" />
                    ))}
                  </Box>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewDialogOpen(false)}>关闭</Button>
        </DialogActions>
      </Dialog>

      {/* 用例编辑对话框 */}
      <Dialog 
        open={editDialogOpen} 
        onClose={() => setEditDialogOpen(false)} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">编辑用例</Typography>
            <IconButton onClick={() => setEditDialogOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {editingTestCase && (
            <Box>
              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <TextField
                  label="用例ID"
                  value={editingTestCase.id}
                  disabled
                  size="small"
                  sx={{ width: '150px' }}
                />
                <TextField
                  label="关联需求ID"
                  value={editingTestCase.requirement_id || ''}
                  onChange={(e) => setEditingTestCase({ ...editingTestCase, requirement_id: e.target.value })}
                  size="small"
                  sx={{ width: '150px' }}
                />
              </Box>
              <TextField
                fullWidth
                label="标题"
                value={editingTestCase.title || ''}
                onChange={(e) => setEditingTestCase({ ...editingTestCase, title: e.target.value })}
                sx={{ mb: 2 }}
              />
              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>优先级</InputLabel>
                  <Select
                    value={editingTestCase.priority || '中'}
                    label="优先级"
                    onChange={(e) => setEditingTestCase({ ...editingTestCase, priority: e.target.value })}
                  >
                    <MenuItem value="高">高</MenuItem>
                    <MenuItem value="中">中</MenuItem>
                    <MenuItem value="低">低</MenuItem>
                  </Select>
                </FormControl>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>状态</InputLabel>
                  <Select
                    value={editingTestCase.status || '未执行'}
                    label="状态"
                    onChange={(e) => setEditingTestCase({ ...editingTestCase, status: e.target.value })}
                  >
                    <MenuItem value="未执行">未执行</MenuItem>
                    <MenuItem value="执行中">执行中</MenuItem>
                    <MenuItem value="已执行">已执行</MenuItem>
                    <MenuItem value="阻塞">阻塞</MenuItem>
                  </Select>
                </FormControl>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>用例类型</InputLabel>
                  <Select
                    value={editingTestCase.case_type || '基本功能'}
                    label="用例类型"
                    onChange={(e) => setEditingTestCase({ ...editingTestCase, case_type: e.target.value })}
                  >
                    <MenuItem value="基本功能">基本功能</MenuItem>
                    <MenuItem value="异常情况">异常情况</MenuItem>
                    <MenuItem value="边界条件">边界条件</MenuItem>
                    <MenuItem value="性能测试">性能测试</MenuItem>
                    <MenuItem value="安全测试">安全测试</MenuItem>
                  </Select>
                </FormControl>
              </Box>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="描述"
                value={editingTestCase.description || ''}
                onChange={(e) => setEditingTestCase({ ...editingTestCase, description: e.target.value })}
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                multiline
                rows={2}
                label="前置条件（每行一个）"
                value={(editingTestCase.preconditions || []).join('\n')}
                onChange={(e) => setEditingTestCase({ 
                  ...editingTestCase, 
                  preconditions: e.target.value.split('\n').filter(s => s.trim()) 
                })}
                sx={{ mb: 2 }}
              />
              
              {/* 测试步骤编辑 */}
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="subtitle2">测试步骤</Typography>
                  <Button
                    size="small"
                    startIcon={<AddIcon />}
                    onClick={() => {
                      const steps = editingTestCase.steps || [];
                      const newStep = {
                        step_no: steps.length + 1,
                        action: '',
                        input: '',
                        expected: ''
                      };
                      setEditingTestCase({
                        ...editingTestCase,
                        steps: [...steps, newStep]
                      });
                    }}
                  >
                    添加步骤
                  </Button>
                </Box>
                {(editingTestCase.steps || []).map((step, stepIndex) => (
                  <Paper key={stepIndex} variant="outlined" sx={{ p: 1.5, mb: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        步骤 {step.step_no || stepIndex + 1}
                      </Typography>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => {
                          const newSteps = editingTestCase.steps.filter((_, i) => i !== stepIndex);
                          newSteps.forEach((s, i) => s.step_no = i + 1);
                          setEditingTestCase({ ...editingTestCase, steps: newSteps });
                        }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Box>
                    <TextField
                      fullWidth
                      size="small"
                      label="操作"
                      value={step.action || ''}
                      onChange={(e) => {
                        const newSteps = [...editingTestCase.steps];
                        newSteps[stepIndex].action = e.target.value;
                        setEditingTestCase({ ...editingTestCase, steps: newSteps });
                      }}
                      sx={{ mb: 1 }}
                    />
                    <TextField
                      fullWidth
                      size="small"
                      label="输入数据"
                      value={step.input || ''}
                      onChange={(e) => {
                        const newSteps = [...editingTestCase.steps];
                        newSteps[stepIndex].input = e.target.value;
                        setEditingTestCase({ ...editingTestCase, steps: newSteps });
                      }}
                      sx={{ mb: 1 }}
                    />
                    <TextField
                      fullWidth
                      size="small"
                      label="预期结果"
                      value={step.expected || ''}
                      onChange={(e) => {
                        const newSteps = [...editingTestCase.steps];
                        newSteps[stepIndex].expected = e.target.value;
                        setEditingTestCase({ ...editingTestCase, steps: newSteps });
                      }}
                    />
                  </Paper>
                ))}
                {(!editingTestCase.steps || editingTestCase.steps.length === 0) && (
                  <Alert severity="info">暂无测试步骤，点击"添加步骤"创建</Alert>
                )}
              </Box>
              
              <TextField
                fullWidth
                multiline
                rows={4}
                label="预期结果"
                value={editingTestCase.expected_result || ''}
                onChange={(e) => setEditingTestCase({ ...editingTestCase, expected_result: e.target.value })}
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="标签（逗号分隔）"
                value={(editingTestCase.tags || []).join(', ')}
                onChange={(e) => setEditingTestCase({ 
                  ...editingTestCase, 
                  tags: e.target.value.split(',').map(s => s.trim()).filter(s => s) 
                })}
                sx={{ mb: 2 }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>取消</Button>
          <Button
            variant="contained"
            onClick={handleSaveTestCase}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
          >
            保存
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
