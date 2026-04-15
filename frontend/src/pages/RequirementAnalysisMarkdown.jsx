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
import MDEditor from '@uiw/react-md-editor';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  CloudUpload as UploadIcon,
  Save as SaveIcon,
  Publish as PublishIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Close as CloseIcon,
  Add as AddIcon,
  Description as DocIcon,
  Folder as FolderIcon,
  Analytics as AnalysisIcon,
} from '@mui/icons-material';
import { requirementAPI } from '../services/api';

export default function RequirementAnalysisMarkdown() {
  // 视图模式: 'editor' | 'drafts' | 'formal'
  const [viewMode, setViewMode] = useState('editor');
  
  // 输入相关
  const [inputMode, setInputMode] = useState('text');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [textContent, setTextContent] = useState('');
  const [sourceName, setSourceName] = useState('');
  
  // Markdown相关
  const [markdown, setMarkdown] = useState('');
  const [draftId, setDraftId] = useState(null);
  const [analysisInfo, setAnalysisInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // 草稿列表
  const [drafts, setDrafts] = useState([]);
  
  // 正式需求列表
  const [formalRequirements, setFormalRequirements] = useState([]);
  const [selectedFormal, setSelectedFormal] = useState(null);
  const [formalContent, setFormalContent] = useState('');
  const [formalDialogOpen, setFormalDialogOpen] = useState(false);
  const [editMode, setEditMode] = useState(false); // true=编辑, false=预览

  // 页面加载时获取列表
  useEffect(() => {
    loadDrafts();
    loadFormalRequirements();
  }, []);

  const loadDrafts = async () => {
    try {
      const response = await requirementAPI.getDrafts();
      setDrafts(response.data.drafts || []);
    } catch (err) {
      console.error('加载草稿列表失败:', err);
    }
  };

  const loadFormalRequirements = async () => {
    try {
      const response = await requirementAPI.getFormalRequirements();
      setFormalRequirements(response.data.requirements || []);
    } catch (err) {
      console.error('加载正式需求失败:', err);
    }
  };

  // 自动保存（防抖）
  useEffect(() => {
    if (!draftId || !markdown || viewMode !== 'editor') return;

    const timer = setTimeout(async () => {
      try {
        await requirementAPI.saveDraftMarkdown(draftId, markdown);
        console.log('✅ 自动保存成功');
      } catch (err) {
        console.error('自动保存失败:', err);
      }
    }, 2000);

    return () => clearTimeout(timer);
  }, [markdown, draftId, viewMode]);

  // 文件处理
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const allowedExtensions = ['.md', '.txt'];
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
      
      if (!allowedExtensions.includes(fileExtension)) {
        setError('不支持的文件格式。仅支持 .md 和 .txt');
        return;
      }

      if (file.size > 10 * 1024 * 1024) {
        setError('文件大小超过限制(10MB)');
        return;
      }

      setUploadedFile(file);
      setError(null);
    }
  };

  // 分析需求并生成Markdown
  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);

    try {
      let content, name;

      if (inputMode === 'file') {
        if (!uploadedFile) throw new Error('请先选择文件');
        
        const fileExt = uploadedFile.name.split('.').pop().toLowerCase();
        
        if (['md', 'txt', 'json', 'xml', 'html'].includes(fileExt)) {
          content = await readFileContent(uploadedFile);
        } else {
          setError(`不支持${fileExt.toUpperCase()}，请复制到文本输入框`);
          setLoading(false);
          return;
        }
        
        name = sourceName.trim() || uploadedFile.name;
      } else {
        if (!textContent.trim()) throw new Error('请输入需求内容');
        content = textContent;
        name = sourceName.trim() || '手动输入的需求文档';
      }

      const result = await requirementAPI.analyzeToMarkdown(content, name);
      
      setMarkdown(result.data.markdown);
      setDraftId(result.data.draft_id);
      setAnalysisInfo({
        summary: result.data.summary,
        total_issues: result.data.total_issues
      });
      
      loadDrafts();
    } catch (err) {
      setError(err.message || err.response?.data?.detail || '分析失败');
    } finally {
      setLoading(false);
    }
  };

  const readFileContent = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = (e) => reject(new Error('文件读取失败'));
      reader.readAsText(file);
    });
  };

  // 保存草稿
  const handleSave = async () => {
    if (!draftId || !markdown) {
      setError('没有可保存的草稿');
      return;
    }

    setLoading(true);
    try {
      await requirementAPI.saveDraftMarkdown(draftId, markdown);
      loadDrafts();
    } catch (err) {
      setError(err.message || '保存失败');
    } finally {
      setLoading(false);
    }
  };

  // 发布为正式文档
  const handlePublish = async () => {
    if (!draftId) return;

    if (!window.confirm('确定要发布为正式文档吗？发布后草稿将被删除。')) return;

    setLoading(true);
    try {
      await requirementAPI.publishDraft(draftId);
      alert('发布成功！');
      handleNewDraft();
      loadDrafts();
      loadFormalRequirements();
    } catch (err) {
      setError(err.message || '发布失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除草稿
  const handleDeleteDraft = async (draftIdToDelete, event) => {
    if (event) event.stopPropagation();
    if (!window.confirm('确定要删除这个草稿吗？')) return;

    try {
      await requirementAPI.deleteDraft(draftIdToDelete);
      loadDrafts();
      if (draftId === draftIdToDelete) handleNewDraft();
    } catch (err) {
      setError('删除失败');
    }
  };

  // 加载草稿进行编辑
  const handleEditDraft = async (draft) => {
    try {
      const response = await requirementAPI.getDraftMarkdown(draft.draft_id);
      setMarkdown(response.data.markdown);
      setDraftId(draft.draft_id);
      setAnalysisInfo(null);
      setViewMode('editor');
    } catch (err) {
      setError('加载草稿失败');
    }
  };

  // 新建草稿
  const handleNewDraft = () => {
    setMarkdown('');
    setDraftId(null);
    setAnalysisInfo(null);
    setTextContent('');
    setSourceName('');
    setUploadedFile(null);
    setError(null);
  };

  // 预览正式需求
  const handleViewFormal = async (req) => {
    try {
      const response = await requirementAPI.getFormalRequirement(req.module, req.file_name);
      setSelectedFormal(req);
      setFormalContent(response.data.content);
      setFormalDialogOpen(true);
      setEditMode(false); // 预览模式
    } catch (err) {
      setError('加载需求失败');
    }
  };

  // 编辑正式需求
  const handleEditFormal = async (req) => {
    try {
      const response = await requirementAPI.getFormalRequirement(req.module, req.file_name);
      setSelectedFormal(req);
      setFormalContent(response.data.content);
      setFormalDialogOpen(true);
      setEditMode(true); // 编辑模式
    } catch (err) {
      setError('加载需求失败');
    }
  };

  // 保存正式需求
  const handleSaveFormal = async () => {
    if (!selectedFormal) return;

    setLoading(true);
    try {
      await requirementAPI.updateFormalRequirement(
        selectedFormal.module,
        selectedFormal.file_name,
        formalContent
      );
      alert('保存成功！');
      setFormalDialogOpen(false);
      loadFormalRequirements();
    } catch (err) {
      setError('保存失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除正式需求
  const handleDeleteFormal = async (req, event) => {
    if (event) event.stopPropagation();
    if (!window.confirm('确定要删除这个正式需求吗？此操作不可恢复。')) return;

    try {
      await requirementAPI.deleteFormalRequirement(req.module, req.file_name);
      loadFormalRequirements();
    } catch (err) {
      setError('删除失败');
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
            需求分析
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant={viewMode === 'editor' ? 'contained' : 'outlined'}
              size="small"
              onClick={() => setViewMode('editor')}
              startIcon={<AnalysisIcon />}
            >
              需求分析
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
              需求管理 ({formalRequirements.length})
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
            <Button
              variant="outlined"
              size="small"
              onClick={handleSave}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={16} /> : <SaveIcon />}
            >
              保存
            </Button>
            <Button
              variant="contained"
              size="small"
              color="success"
              onClick={handlePublish}
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
          {error}
        </Alert>
      )}

      {/* 编辑器视图 */}
      {viewMode === 'editor' && (
        <Box>
          {!markdown ? (
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">输入需求文档</Typography>
                  <Chip label="AI自动生成结构化Markdown" color="info" size="small" />
                </Box>

                <Tabs value={inputMode} onChange={(e, val) => setInputMode(val)} sx={{ mb: 2 }}>
                  <Tab label="文本输入" value="text" />
                  <Tab label="文件上传" value="file" />
                </Tabs>

                {inputMode === 'file' ? (
                  <Box>
                    <Alert severity="info" sx={{ mb: 2 }}>
                      仅支持 .md 和 .txt 文件。PDF/Word请复制到文本输入框。
                    </Alert>
                    <input
                      accept=".md,.txt"
                      style={{ display: 'none' }}
                      id="file-upload-button"
                      type="file"
                      onChange={handleFileChange}
                    />
                    <label htmlFor="file-upload-button">
                      <Button variant="outlined" component="span" startIcon={<UploadIcon />}>
                        选择文件
                      </Button>
                    </label>
                    {uploadedFile && (
                      <Alert severity="success" sx={{ mt: 2 }}>
                        {uploadedFile.name}
                        <IconButton size="small" onClick={() => setUploadedFile(null)}>
                          <CloseIcon />
                        </IconButton>
                      </Alert>
                    )}
                  </Box>
                ) : (
                  <Box>
                    <Alert severity="info" sx={{ mb: 2 }}>
                      复制PDF/Word/任何格式的需求文本，粘贴到下方即可。
                    </Alert>
                    <TextField
                      fullWidth
                      multiline
                      rows={10}
                      label="需求文档内容"
                      placeholder="粘贴需求文档内容..."
                      value={textContent}
                      onChange={(e) => setTextContent(e.target.value)}
                    />
                  </Box>
                )}

                <Button
                  variant="contained"
                  size="large"
                  onClick={handleAnalyze}
                  disabled={loading || (inputMode === 'file' ? !uploadedFile : !textContent)}
                  startIcon={loading ? <CircularProgress size={20} /> : <AddIcon />}
                  sx={{ mt: 2 }}
                >
                  {loading ? 'AI 分析中...' : '开始分析'}
                </Button>
              </CardContent>
            </Card>
          ) : (
            <Box>
              {analysisInfo && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  <AlertTitle>分析完成</AlertTitle>
                  {analysisInfo.summary}
                </Alert>
              )}

              <Card>
                <CardContent>
                  <Box data-color-mode="light">
                    <MDEditor
                      value={markdown}
                      onChange={setMarkdown}
                      height={600}
                      preview="edit"
                    />
                  </Box>
                </CardContent>
              </Card>

              <Box sx={{ display: 'flex', gap: 2, mt: 2, justifyContent: 'space-between' }}>
                <Button variant="outlined" onClick={handleNewDraft} startIcon={<AddIcon />}>
                  新建分析
                </Button>
                <Box>
                  <Button variant="outlined" onClick={() => setViewMode('drafts')} sx={{ mr: 1 }}>
                    草稿箱
                  </Button>
                  <Button
                    variant="contained"
                    onClick={handleSave}
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
                    sx={{ mr: 1 }}
                  >
                    保存草稿
                  </Button>
                  <Button
                    variant="contained"
                    color="success"
                    onClick={handlePublish}
                    disabled={loading}
                    startIcon={<PublishIcon />}
                  >
                    发布正式文档
                  </Button>
                </Box>
              </Box>
            </Box>
          )}
        </Box>
      )}

      {/* 草稿箱视图 */}
      {viewMode === 'drafts' && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">草稿箱</Typography>
              <Box>
                <Button startIcon={<RefreshIcon />} onClick={loadDrafts} size="small" sx={{ mr: 1 }}>
                  刷新
                </Button>
                <Button 
                  variant="contained"
                  startIcon={<AddIcon />} 
                  onClick={() => { handleNewDraft(); setViewMode('editor'); }}
                  size="small"
                >
                  新建分析
                </Button>
              </Box>
            </Box>

            {drafts.length === 0 ? (
              <Alert severity="info">暂无草稿。点击上方"新建分析"开始创建。</Alert>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>标题</TableCell>
                      <TableCell>模块</TableCell>
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
                            {draft.title || draft.source_name || draft.draft_id}
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
                        <TableCell>{draft.source_name}</TableCell>
                        <TableCell>
                          {new Date(draft.updated_at).toLocaleString('zh-CN', {
                            month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit'
                          })}
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

      {/* 需求管理视图 */}
      {viewMode === 'formal' && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">需求管理</Typography>
              <Button startIcon={<RefreshIcon />} onClick={loadFormalRequirements} size="small">
                刷新
              </Button>
            </Box>

            {formalRequirements.length === 0 ? (
              <Alert severity="info">
                暂无正式需求。请先创建草稿并发布为正式文档。
              </Alert>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>标题</TableCell>
                      <TableCell>模块</TableCell>
                      <TableCell>文件大小</TableCell>
                      <TableCell>更新时间</TableCell>
                      <TableCell align="right">操作</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {formalRequirements.map((req) => (
                      <TableRow 
                        key={req.file_name} 
                        hover
                        sx={{ cursor: 'pointer' }}
                        onClick={() => handleViewFormal(req)}
                      >
                        <TableCell>{req.title}</TableCell>
                        <TableCell>
                          <Chip label={req.module} size="small" variant="outlined" />
                        </TableCell>
                        <TableCell>{req.size_kb} KB</TableCell>
                        <TableCell>
                          {new Date(req.updated_at).toLocaleString('zh-CN', {
                            month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit'
                          })}
                        </TableCell>
                        <TableCell align="right" onClick={(e) => e.stopPropagation()}>
                          <Tooltip title="预览">
                            <IconButton 
                              size="small" 
                              onClick={(e) => {
                                e.stopPropagation();
                                handleViewFormal(req);
                              }}
                            >
                              <DocIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="编辑">
                            <IconButton size="small" onClick={() => handleEditFormal(req)}>
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="删除">
                            <IconButton size="small" onClick={(e) => handleDeleteFormal(req, e)}>
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

      {/* 正式需求预览/编辑对话框 */}
      <Dialog
        open={formalDialogOpen}
        onClose={() => setFormalDialogOpen(false)}
        maxWidth="md"
        fullWidth
        sx={{
          '& .MuiDialog-paper': {
            minHeight: '80vh',
            maxHeight: '90vh'
          }
        }}
      >
        {selectedFormal && (
          <>
            <DialogTitle sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              borderBottom: '1px solid',
              borderColor: 'divider'
            }}>
              <Typography variant="h6">
                {editMode ? '编辑需求' : '需求预览'}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip 
                  label={selectedFormal.title} 
                  variant="outlined" 
                  size="small"
                  sx={{ maxWidth: 300 }}
                />
                <Chip 
                  label={editMode ? '编辑模式' : '预览模式'} 
                  size="small" 
                  color={editMode ? 'primary' : 'success'}
                  variant={editMode ? 'filled' : 'outlined'}
                />
                {!editMode && (
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<EditIcon />}
                    onClick={() => setEditMode(true)}
                  >
                    编辑
                  </Button>
                )}
              </Box>
            </DialogTitle>
            <DialogContent dividers sx={{ p: editMode ? 0 : 3 }}>
              {editMode ? (
                // 编辑模式：使用Markdown编辑器
                <Box data-color-mode="light">
                  <MDEditor
                    value={formalContent}
                    onChange={setFormalContent}
                    height={600}
                    preview="edit"
                  />
                </Box>
              ) : (
                // 预览模式：渲染成网页格式
                <Box 
                  sx={{ 
                    maxHeight: '70vh',
                    overflow: 'auto',
                    '& h1': { fontSize: '2em', fontWeight: 'bold', mt: 3, mb: 2, pb: 1, borderBottom: '2px solid #eaecef' },
                    '& h2': { fontSize: '1.5em', fontWeight: 'bold', mt: 2.5, mb: 2, pb: 0.8, borderBottom: '1px solid #eaecef' },
                    '& h3': { fontSize: '1.25em', fontWeight: 'bold', mt: 2, mb: 1.5 },
                    '& h4': { fontSize: '1.1em', fontWeight: 'bold', mt: 1.5, mb: 1 },
                    '& p': { lineHeight: 1.8, my: 1.5 },
                    '& ul, & ol': { pl: 3, my: 1 },
                    '& li': { my: 0.5 },
                    '& table': { borderCollapse: 'collapse', width: '100%', my: 2 },
                    '& th, & td': { border: '1px solid #d0d7de', padding: '8px 12px', textAlign: 'left' },
                    '& th': { backgroundColor: '#f6f8fa', fontWeight: 'bold' },
                    '& tr:nth-of-type(2n)': { backgroundColor: '#f6f8fa' },
                    '& blockquote': { 
                      borderLeft: '4px solid #d0d7de', 
                      pl: 3, 
                      py: 1, 
                      my: 2,
                      backgroundColor: '#f6f8fa',
                      color: '#57606a'
                    },
                    '& code': { 
                      backgroundColor: '#f6f8fa', 
                      px: 1, 
                      py: 0.5, 
                      borderRadius: 1,
                      fontFamily: 'monospace',
                      fontSize: '0.9em'
                    },
                    '& pre': { 
                      backgroundColor: '#f6f8fa', 
                      p: 2, 
                      borderRadius: 2,
                      overflow: 'auto',
                      my: 2
                    },
                    '& pre code': { 
                      backgroundColor: 'transparent', 
                      px: 0, 
                      py: 0 
                    },
                    '& hr': { border: 'none', borderTop: '2px solid #eaecef', my: 3 }
                  }}
                >
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {formalContent}
                  </ReactMarkdown>
                </Box>
              )}
            </DialogContent>
            <DialogActions sx={{ borderTop: '1px solid', borderColor: 'divider' }}>
              <Button onClick={() => { setFormalDialogOpen(false); setEditMode(false); }}>
                关闭
              </Button>
              {editMode && (
                <Button
                  variant="outlined"
                  onClick={() => setEditMode(false)}
                  sx={{ mr: 1 }}
                >
                  取消编辑
                </Button>
              )}
              {editMode && (
                <Button
                  variant="contained"
                  onClick={handleSaveFormal}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
                >
                  保存修改
                </Button>
              )}
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
}
