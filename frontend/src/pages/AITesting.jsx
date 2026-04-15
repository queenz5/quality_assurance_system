import React, { useState } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  Button,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  BugReport as BugIcon,
  Code as CodeIcon,
  Assessment as ImpactIcon,
  Lightbulb,
  Warning,
} from '@mui/icons-material';
import { aiAPI } from '../services/api';

function AITesting() {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  // 状态
  const [bugId, setBugId] = useState('');
  const [bugAnalysis, setBugAnalysis] = useState(null);

  const [codeFiles, setCodeFiles] = useState('');
  const [module, setModule] = useState('');
  const [recommendations, setRecommendations] = useState([]);

  // 新需求影响分析
  const [newRequirementContent, setNewRequirementContent] = useState('');
  const [impactModule, setImpactModule] = useState('');
  const [impactResult, setImpactResult] = useState(null);

  // 分析BUG
  const handleAnalyzeBug = async () => {
    if (!bugId) return;

    try {
      setLoading(true);
      const response = await aiAPI.analyzeBug(bugId);
      setBugAnalysis(response.data);
    } catch (error) {
      console.error('Failed to analyze bug:', error);
    } finally {
      setLoading(false);
    }
  };

  // 推荐测试用例
  const handleRecommendTestCases = async () => {
    if (!codeFiles) return;

    try {
      setLoading(true);
      const response = await aiAPI.recommendTestCases(codeFiles, module || undefined);
      setRecommendations(response.data.test_cases);
    } catch (error) {
      console.error('Failed to recommend test cases:', error);
    } finally {
      setLoading(false);
    }
  };

  // 新需求影响分析
  const handleImpactAnalysis = async () => {
    if (!newRequirementContent) return;

    try {
      setLoading(true);
      const response = await aiAPI.analyzeRequirementImpact(newRequirementContent, impactModule || undefined);
      setImpactResult(response.data);
    } catch (error) {
      console.error('Failed to analyze requirement impact:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { label: 'BUG 根因分析', icon: <BugIcon /> },
    { label: '用例推荐', icon: <CodeIcon /> },
    { label: '新需求影响分析', icon: <ImpactIcon /> },
  ];

  return (
    <Box>
      <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
        AI 辅助测试
      </Typography>

      {/* 选项卡 */}
      <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
        {tabs.map((tab, index) => (
          <Button
            key={index}
            variant={activeTab === index ? 'contained' : 'outlined'}
            startIcon={tab.icon}
            onClick={() => setActiveTab(index)}
            sx={{ borderRadius: 2 }}
          >
            {tab.label}
          </Button>
        ))}
      </Box>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {/* BUG 根因分析 */}
      {activeTab === 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
              分析 BUG 根因，推荐修复方案
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <TextField
                label="BUG ID（如：BUG-001）"
                value={bugId}
                onChange={(e) => setBugId(e.target.value)}
                fullWidth
                onKeyDown={(e) => e.key === 'Enter' && handleAnalyzeBug()}
              />
              <Button
                variant="contained"
                onClick={handleAnalyzeBug}
                disabled={!bugId || loading}
                sx={{ minWidth: 120 }}
              >
                分析
              </Button>
            </Box>

            {bugAnalysis && (
              <Box>
                <Alert severity="info" sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                    {bugAnalysis.bug_info.title}
                  </Typography>
                  <Typography variant="body2">
                    模块：{bugAnalysis.bug_info.module} | 严重程度：{bugAnalysis.bug_info.severity}
                  </Typography>
                </Alert>

                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
                      推荐根因（按频率排序）
                    </Typography>
                    {bugAnalysis.recommended_root_causes.map((cause, index) => (
                      <Card key={index} variant="outlined" sx={{ mb: 2 }}>
                        <CardContent>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                              {cause.root_cause}
                            </Typography>
                            <Chip
                              label={`出现${cause.occurrence_count}次`}
                              size="small"
                              color="primary"
                            />
                          </Box>
                          <Typography variant="caption" color="textSecondary">
                            置信度：{(cause.confidence * 100).toFixed(0)}%
                          </Typography>
                        </CardContent>
                      </Card>
                    ))}
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
                      建议修复方案
                    </Typography>
                    <Card variant="outlined" sx={{ bgcolor: 'success.lighter' }}>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                          <Lightbulb color="success" sx={{ mr: 1 }} />
                          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                            {bugAnalysis.suggested_fix}
                          </Typography>
                        </Box>
                        <Typography variant="caption" color="textSecondary">
                          分析置信度：{(bugAnalysis.confidence * 100).toFixed(0)}%
                        </Typography>
                      </CardContent>
                    </Card>

                    {bugAnalysis.similar_bugs.length > 0 && (
                      <Box sx={{ mt: 3 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                          相似 BUG（{bugAnalysis.similar_bugs.length}个）
                        </Typography>
                        {bugAnalysis.similar_bugs.map((bug, index) => (
                          <Box key={index} sx={{ mb: 1, p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                            <Typography variant="body2">{bug.title}</Typography>
                            <Typography variant="caption" color="textSecondary">
                              相似度：{(bug.similarity * 100).toFixed(0)}%
                            </Typography>
                          </Box>
                        ))}
                      </Box>
                    )}
                  </Grid>
                </Grid>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* 用例推荐 */}
      {activeTab === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
              根据代码变更推荐回归测试用例
            </Typography>
            
            <Box sx={{ mb: 3 }}>
              <TextField
                label="修改的代码文件（多个用逗号分隔，如：user.py,auth.py）"
                value={codeFiles}
                onChange={(e) => setCodeFiles(e.target.value)}
                fullWidth
                multiline
                rows={2}
                sx={{ mb: 2 }}
              />
              <TextField
                label="模块名称（可选）"
                value={module}
                onChange={(e) => setModule(e.target.value)}
                fullWidth
                sx={{ mb: 2 }}
              />
              <Button
                variant="contained"
                onClick={handleRecommendTestCases}
                disabled={!codeFiles || loading}
                sx={{ minWidth: 120 }}
              >
                推荐
              </Button>
            </Box>

            {recommendations.length > 0 && (
              <Alert severity="success" sx={{ mb: 2 }}>
                推荐 {recommendations.length} 个测试用例
              </Alert>
            )}

            <List>
              {recommendations.map((rec, index) => (
                <ListItem
                  key={index}
                  sx={{
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 2,
                    mb: 1,
                  }}
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {rec.test_case_title}
                        </Typography>
                        <Chip
                          label={`分数: ${rec.relevance_score}`}
                          size="small"
                          color="primary"
                        />
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 0.5 }}>
                        <Typography variant="body2" color="textSecondary">
                          模块：{rec.module} | {rec.recommendation_reason}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* 新需求影响分析 */}
      {activeTab === 2 && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
              分析新需求对历史需求和测试用例的影响
            </Typography>

            <Box sx={{ mb: 3 }}>
              <TextField
                label="模块名称（可选，用于缩小检索范围）"
                value={impactModule}
                onChange={(e) => setImpactModule(e.target.value)}
                fullWidth
                sx={{ mb: 2 }}
              />
              <TextField
                label="新需求内容（Markdown 格式）"
                value={newRequirementContent}
                onChange={(e) => setNewRequirementContent(e.target.value)}
                fullWidth
                multiline
                rows={12}
                placeholder={`# REQ-010: 新功能名称

## 基本信息
- **模块**: 模块名
- **优先级**: 高
- **状态**: 新需求

## 需求描述
详细描述新功能...

## 功能点
1. 功能点1
2. 功能点2`}
                sx={{ mb: 2 }}
              />
              <Button
                variant="contained"
                onClick={handleImpactAnalysis}
                disabled={!newRequirementContent || loading}
                sx={{ minWidth: 120 }}
              >
                分析影响
              </Button>
            </Box>

            {impactResult && (
              <Box>
                {/* 风险等级 */}
                <Alert
                  severity={impactResult.risk_level === '高' ? 'error' : impactResult.risk_level === '中' ? 'warning' : 'info'}
                  sx={{ mb: 3 }}
                >
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                    风险等级：{impactResult.risk_level}
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {impactResult.impact_summary}
                  </Typography>
                </Alert>

                <Grid container spacing={3}>
                  {/* 受影响的需求 */}
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
                      受影响的历史需求（{impactResult.affected_requirements?.length || 0}个）
                    </Typography>
                    {impactResult.affected_requirements?.map((req, index) => (
                      <Card key={index} variant="outlined" sx={{ mb: 2 }}>
                        <CardContent>
                          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                            <Warning color="warning" fontSize="small" />
                            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                              {req.id}: {req.title}
                            </Typography>
                          </Box>
                          <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mb: 1 }}>
                            模块：{req.module}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {req.impact_reason}
                          </Typography>
                        </CardContent>
                      </Card>
                    ))}
                  </Grid>

                  {/* 推荐回归用例 */}
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
                      推荐回归测试用例（{impactResult.regression_test_cases?.length || 0}个）
                    </Typography>
                    {impactResult.regression_test_cases?.map((tc, index) => (
                      <Card key={index} variant="outlined" sx={{ mb: 2 }}>
                        <CardContent>
                          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                            {tc.id}: {tc.title}
                          </Typography>
                          <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mb: 1 }}>
                            模块：{tc.module}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {tc.reason}
                          </Typography>
                        </CardContent>
                      </Card>
                    ))}
                  </Grid>
                </Grid>

                {/* 建议 */}
                {impactResult.suggestions && impactResult.suggestions.length > 0 && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
                      测试建议
                    </Typography>
                    <Card variant="outlined" sx={{ bgcolor: 'success.lighter' }}>
                      <CardContent>
                        <List dense>
                          {impactResult.suggestions.map((suggestion, index) => (
                            <ListItem key={index}>
                              <ListItemIcon sx={{ minWidth: 36 }}>
                                <Lightbulb color="success" fontSize="small" />
                              </ListItemIcon>
                              <ListItemText primary={suggestion} />
                            </ListItem>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  </Box>
                )}
              </Box>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

export default AITesting;
