import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Chip,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Button,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Warning,
  Print,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';
import { reportAPI } from '../services/api';

function SmartReport() {
  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState(null);
  const [moduleReports, setModuleReports] = useState([]);

  useEffect(() => {
    loadReport();
  }, []);

  const loadReport = async () => {
    try {
      setLoading(true);
      const [projectRes, moduleRes] = await Promise.all([
        reportAPI.getProjectReport(),
        reportAPI.getAllModuleReports(),
      ]);

      setReport(projectRes.data);
      setModuleReports(moduleRes.data.reports);
    } catch (error) {
      console.error('Failed to load report:', error);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success.main';
    if (score >= 60) return 'warning.main';
    return 'error.main';
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return '优秀';
    if (score >= 60) return '良好';
    if (score >= 40) return '一般';
    return '较差';
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  const bugTrendData = report?.bug_trend?.map((item) => ({
    date: item.date,
    '预测BUG数': item.predicted_bugs,
  })) || [];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          智能报告
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Print />}
          onClick={() => window.print()}
        >
          打印报告
        </Button>
      </Box>

      {report && (
        <>
          {/* 执行摘要 */}
          <Card sx={{ mb: 4, bgcolor: 'primary.lighter' }}>
            <CardContent>
              <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 2 }}>
                执行摘要
              </Typography>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                {report.executive_summary}
              </Typography>
            </CardContent>
          </Card>

          {/* 质量得分 */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={4}>
              <Card sx={{ textAlign: 'center' }}>
                <CardContent>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    项目质量得分
                  </Typography>
                  <Typography
                    variant="h2"
                    sx={{
                      fontWeight: 'bold',
                      color: getScoreColor(report.project_quality_score),
                      mb: 1,
                    }}
                  >
                    {report.project_quality_score}
                  </Typography>
                  <Chip
                    label={getScoreLabel(report.project_quality_score)}
                    color={report.project_quality_score >= 60 ? 'success' : 'warning'}
                  />
                  <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                    满分 100 分
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card sx={{ textAlign: 'center' }}>
                <CardContent>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    需求覆盖率
                  </Typography>
                  <Typography
                    variant="h2"
                    sx={{
                      fontWeight: 'bold',
                      color: 'success.main',
                      mb: 1,
                    }}
                  >
                    {(report.overall_requirement_coverage * 100).toFixed(1)}%
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={report.overall_requirement_coverage * 100}
                    sx={{ height: 8, borderRadius: 4 }}
                    color="success"
                  />
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card sx={{ textAlign: 'center' }}>
                <CardContent>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    缺陷密度
                  </Typography>
                  <Typography
                    variant="h2"
                    sx={{
                      fontWeight: 'bold',
                      color: 'error.main',
                      mb: 1,
                    }}
                  >
                    {report.overall_defect_density}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    BUG总数: {report.bug_statistics.total_bugs}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    已修复: {report.bug_statistics.fixed_bugs} | 修复率: {(report.bug_statistics.fix_rate * 100).toFixed(0)}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* 改进建议 */}
          {report.recommendations.length > 0 && (
            <Alert severity="warning" sx={{ mb: 4 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                改进建议
              </Typography>
              <List dense>
                {report.recommendations.map((rec, index) => (
                  <ListItem key={index}>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <Warning color="warning" />
                    </ListItemIcon>
                    <ListItemText primary={rec} />
                  </ListItem>
                ))}
              </List>
            </Alert>
          )}

          {/* 测试执行摘要 */}
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
                测试执行摘要
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="textSecondary">
                    测试用例总数
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {report.test_execution_summary.total_test_cases}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="textSecondary">
                    已执行
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                    {report.test_execution_summary.executed}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="textSecondary">
                    执行率
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                    {(report.test_execution_summary.execution_rate * 100).toFixed(0)}%
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="textSecondary">
                    BUG发现率
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'error.main' }}>
                    {report.test_execution_summary.bug_discovery_rate}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* 图表 */}
          <Box sx={{ mb: 4 }}>
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
                  BUG 趋势预测
                </Typography>
                <Box sx={{ width: '100%', height: 450 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={bugTrendData} margin={{ top: 10, right: 30, left: 10, bottom: 80 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis 
                        dataKey="date" 
                        tick={{ fontSize: 13, fill: '#666' }} 
                        angle={-30} 
                        textAnchor="end" 
                        height={80}
                        interval={0}
                      />
                      <YAxis tick={{ fontSize: 13, fill: '#666' }} />
                      <Tooltip
                        contentStyle={{
                          borderRadius: 8,
                          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                          fontSize: 13,
                          border: 'none'
                        }}
                      />
                      <Legend wrapperStyle={{ fontSize: 14, paddingTop: 30 }} />
                      <Line
                        type="monotone"
                        dataKey="预测BUG数"
                        stroke="#ff9800"
                        strokeWidth={3}
                        dot={{ r: 6, strokeWidth: 2 }}
                        activeDot={{ r: 8, strokeWidth: 2 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
                  BUG 统计
                </Typography>
                <Box sx={{ width: '100%', height: 450 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={[
                        { name: '严重', count: report.bug_statistics.severity_distribution.严重 },
                        { name: '一般', count: report.bug_statistics.severity_distribution.一般 },
                        { name: '轻微', count: report.bug_statistics.severity_distribution.轻微 },
                      ]}
                      margin={{ top: 10, right: 30, left: 10, bottom: 80 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis dataKey="name" tick={{ fontSize: 14, fill: '#666' }} />
                      <YAxis tick={{ fontSize: 13, fill: '#666' }} />
                      <Tooltip
                        contentStyle={{
                          borderRadius: 8,
                          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                          fontSize: 13,
                          border: 'none'
                        }}
                      />
                      <Legend wrapperStyle={{ fontSize: 14, paddingTop: 30 }} />
                      <Bar dataKey="count" fill="#f44336" name="BUG数量" radius={[8, 8, 0, 0]} barSize={80} />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Box>

          {/* 高风险模块 */}
          {report.high_risk_modules.length > 0 && (
            <Card sx={{ mb: 4 }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
                  高风险模块报告
                </Typography>
                <Grid container spacing={3}>
                  {report.high_risk_modules.map((moduleReport, index) => (
                    <Grid item xs={12} md={6} key={index}>
                      <Card variant="outlined" sx={{ borderColor: 'error.light' }}>
                        <CardContent>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                              {moduleReport.module}
                            </Typography>
                            <Chip
                              label={moduleReport.risk_assessment}
                              color="error"
                              size="small"
                            />
                          </Box>
                          <Typography variant="body2" color="textSecondary" paragraph>
                            质量得分: {moduleReport.quality_score}/100
                          </Typography>
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="caption" color="textSecondary">
                              需求覆盖率: {(moduleReport.requirement_coverage * 100).toFixed(0)}%
                            </Typography>
                            <LinearProgress
                              variant="determinate"
                              value={moduleReport.requirement_coverage * 100}
                              sx={{ height: 6, borderRadius: 3, mt: 0.5 }}
                              color={moduleReport.requirement_coverage > 0.7 ? 'success' : 'warning'}
                            />
                          </Box>
                          {moduleReport.recommendations.length > 0 && (
                            <List dense>
                              {moduleReport.recommendations.slice(0, 3).map((rec, i) => (
                                <ListItem key={i}>
                                  <ListItemIcon sx={{ minWidth: 36 }}>
                                    <Warning color="warning" fontSize="small" />
                                  </ListItemIcon>
                                  <ListItemText primary={rec} />
                                </ListItem>
                              ))}
                            </List>
                          )}
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          )}

          {/* 所有模块报告 */}
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
                所有模块质量报告
              </Typography>
              <Grid container spacing={2}>
                {moduleReports.map((moduleReport, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                          {moduleReport.module}
                        </Typography>
                        <Typography variant="h4" sx={{ fontWeight: 'bold', color: getScoreColor(moduleReport.quality_score), mb: 1 }}>
                          {moduleReport.quality_score}
                        </Typography>
                        <Divider sx={{ my: 1 }} />
                        <Typography variant="body2" color="textSecondary">
                          需求: {moduleReport.total_requirements} | 用例: {moduleReport.total_test_cases}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          BUG: {moduleReport.total_bugs} | 修复率: {(moduleReport.bug_fix_rate * 100).toFixed(0)}%
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </>
      )}
    </Box>
  );
}

export default SmartReport;
