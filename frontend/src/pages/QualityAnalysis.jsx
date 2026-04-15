import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  TrendingUp,
  Warning,
  CheckCircle,
  Info,
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
import { qualityAPI } from '../services/api';

function QualityAnalysis() {
  const [loading, setLoading] = useState(true);
  const [qualityData, setQualityData] = useState(null);
  const [bugTrend, setBugTrend] = useState([]);
  const [bugPrediction, setBugPrediction] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [qualityRes, trendRes, predictionRes] = await Promise.all([
        qualityAPI.getAnalysis(),
        qualityAPI.getBugTrend(7),
        qualityAPI.getBugPrediction(),
      ]);

      setQualityData(qualityRes.data);
      setBugTrend(trendRes.data.predictions);
      setBugPrediction(predictionRes.data.predictions);
    } catch (error) {
      console.error('Failed to load quality data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    switch (level) {
      case '高': return 'error';
      case '中': return 'warning';
      case '低': return 'success';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  const moduleTrendData = bugPrediction.map((p) => ({
    module: p.module,
    '历史BUG率': p.historical_bug_rate,
    '预测新BUG': p.predicted_new_bugs,
    '置信度': p.confidence,
  }));

  return (
    <Box>
      <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
        质量分析与预测
      </Typography>

      {/* 建议提醒 */}
      {qualityData?.recommendations && qualityData.recommendations.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
            改进建议
          </Typography>
          <List dense sx={{ mt: 1 }}>
            {qualityData.recommendations.map((rec, index) => (
              <ListItem key={index}>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <Info color="warning" fontSize="small" />
                </ListItemIcon>
                <ListItemText primary={rec} />
              </ListItem>
            ))}
          </List>
        </Alert>
      )}

      {/* 核心指标 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                整体缺陷密度
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'error.main', mb: 1 }}>
                {qualityData?.overall_defect_density}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={Math.min(100, qualityData?.overall_defect_density * 100)}
                sx={{ height: 8, borderRadius: 4 }}
                color={qualityData?.overall_defect_density > 0.5 ? 'error' : 'success'}
              />
              <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                越低越好
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                需求覆盖率
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'success.main', mb: 1 }}>
                {(qualityData?.overall_requirement_coverage * 100).toFixed(1)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={qualityData?.overall_requirement_coverage * 100}
                sx={{ height: 8, borderRadius: 4 }}
                color="success"
              />
              <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                越高越好
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                未覆盖需求
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'warning.main', mb: 1 }}>
                {qualityData?.uncovered_requirements?.length || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                需要补充测试用例
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 模块质量详情 */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
            模块质量指标
          </Typography>
          <TableContainer component={Paper} sx={{ maxHeight: 500 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>模块</TableCell>
                  <TableCell align="right">需求</TableCell>
                  <TableCell align="right">测试用例</TableCell>
                  <TableCell align="right">执行率</TableCell>
                  <TableCell align="right">BUG数</TableCell>
                  <TableCell align="right">修复率</TableCell>
                  <TableCell align="right">缺陷密度</TableCell>
                  <TableCell align="right">风险等级</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {qualityData?.module_metrics?.map((row) => (
                  <TableRow key={row.module} hover>
                    <TableCell component="th" scope="row" sx={{ fontWeight: 'bold' }}>
                      {row.module}
                    </TableCell>
                    <TableCell align="right">{row.total_requirements}</TableCell>
                    <TableCell align="right">
                      {row.covered_requirements}/{row.total_requirements}
                    </TableCell>
                    <TableCell align="right">
                      <LinearProgress
                        variant="determinate"
                        value={row.execution_rate * 100}
                        sx={{ width: '100%', height: 6, borderRadius: 3, mb: 0.5 }}
                        color={row.execution_rate > 0.7 ? 'success' : 'warning'}
                      />
                      <Typography variant="caption" color="textSecondary">
                        {(row.execution_rate * 100).toFixed(0)}%
                      </Typography>
                    </TableCell>
                    <TableCell align="right">{row.total_bugs}</TableCell>
                    <TableCell align="right">
                      <Chip
                        label={`${(row.bug_fix_rate * 100).toFixed(0)}%`}
                        color={row.bug_fix_rate > 0.7 ? 'success' : 'warning'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography sx={{ fontWeight: 'bold', color: row.defect_density > 0.5 ? 'error.main' : 'inherit' }}>
                        {row.defect_density}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={row.risk_level}
                        color={getRiskColor(row.risk_level)}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* 图表 */}
      <Box sx={{ mb: 4 }}>
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
              BUG 趋势预测（未来7天）
            </Typography>
            <Box sx={{ width: '100%', height: 450 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={bugTrend} margin={{ top: 10, right: 30, left: 10, bottom: 80 }}>
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
                    dataKey="predicted_bugs"
                    stroke="#ff9800"
                    strokeWidth={3}
                    dot={{ r: 6, strokeWidth: 2 }}
                    activeDot={{ r: 8, strokeWidth: 2 }}
                    name="预测BUG数"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
              模块 BUG 预测
            </Typography>
            <Box sx={{ width: '100%', height: 450 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={moduleTrendData} margin={{ top: 10, right: 30, left: 10, bottom: 80 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="module" 
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
                  <Bar dataKey="历史BUG率" fill="#1976d2" radius={[6, 6, 0, 0]} barSize={50} />
                  <Bar dataKey="预测新BUG" fill="#f44336" radius={[6, 6, 0, 0]} barSize={50} />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}

export default QualityAnalysis;
