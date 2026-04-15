import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  Description as RequirementIcon,
  Task as TaskIcon,
  BugReport as BugIcon,
  Category as ModuleIcon,
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
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { dataAPI, qualityAPI } from '../services/api';

const COLORS = ['#1976d2', '#4caf50', '#ff9800', '#f44336', '#9c27b0'];

function StatCard({ title, value, icon, color, subtitle }) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              bgcolor: `${color}.lighter`,
              borderRadius: 2,
              p: 1,
              mr: 2,
            }}
          >
            {icon}
          </Box>
          <Typography color="textSecondary" variant="subtitle2">
            {title}
          </Typography>
        </Box>
        <Typography variant="h3" sx={{ fontWeight: 'bold', mb: 1 }}>
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="textSecondary">
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [modules, setModules] = useState([]);
  const [qualityData, setQualityData] = useState(null);
  const [bugTrend, setBugTrend] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsRes, modulesRes, qualityRes, trendRes] = await Promise.all([
        dataAPI.getStatistics(),
        dataAPI.getModules(),
        qualityAPI.getAnalysis(),
        qualityAPI.getBugTrend(7),
      ]);

      setStats(statsRes.data);
      setModules(modulesRes.data.modules);
      setQualityData(qualityRes.data);
      setBugTrend(trendRes.data.predictions);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
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

  const moduleChartData = qualityData?.module_metrics?.map((m, i) => ({
    name: m.module,
    '测试用例': m.total_test_cases,
    'BUG数': m.total_bugs,
    '缺陷密度': m.defect_density,
  })) || [];

  const severityData = [
    { name: '严重', value: qualityData?.module_metrics?.reduce((sum, m) => sum + m.total_bugs * 0.2, 0) || 0 },
    { name: '一般', value: qualityData?.module_metrics?.reduce((sum, m) => sum + m.total_bugs * 0.5, 0) || 0 },
    { name: '轻微', value: qualityData?.module_metrics?.reduce((sum, m) => sum + m.total_bugs * 0.3, 0) || 0 },
  ];

  return (
    <Box>
      <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
        数据概览仪表盘
      </Typography>

      {/* 统计卡片 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="模块总数"
            value={stats?.modules?.length || 0}
            icon={<ModuleIcon sx={{ color: 'primary.main' }} />}
            color="primary"
            subtitle="系统功能模块"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="需求总数"
            value={stats?.total_requirements || 0}
            icon={<RequirementIcon sx={{ color: 'success.main' }} />}
            color="success"
            subtitle="产品需求"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="测试用例"
            value={stats?.total_test_cases || 0}
            icon={<TaskIcon sx={{ color: 'info.main' }} />}
            color="info"
            subtitle="测试覆盖"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="BUG总数"
            value={stats?.total_bugs || 0}
            icon={<BugIcon sx={{ color: 'error.main' }} />}
            color="error"
            subtitle="缺陷统计"
          />
        </Grid>
      </Grid>

      {/* 质量指标 */}
      {qualityData && (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
              质量指标
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  整体缺陷密度
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'error.main' }}>
                  {qualityData.overall_defect_density}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={Math.min(100, qualityData.overall_defect_density * 100)}
                  sx={{ mt: 1, height: 8, borderRadius: 4 }}
                  color={qualityData.overall_defect_density > 0.5 ? 'error' : 'success'}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  需求覆盖率
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                  {(qualityData.overall_requirement_coverage * 100).toFixed(1)}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={qualityData.overall_requirement_coverage * 100}
                  sx={{ mt: 1, height: 8, borderRadius: 4 }}
                  color="success"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  高风险模块
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                  {qualityData.high_risk_modules.length > 0 ? (
                    qualityData.high_risk_modules.map((module) => (
                      <Chip
                        key={module}
                        label={module}
                        color="error"
                        variant="outlined"
                      />
                    ))
                  ) : (
                    <Chip label="无" color="success" variant="outlined" />
                  )}
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* 图表 */}
      <Box sx={{ mb: 4 }}>
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
              模块质量对比
            </Typography>
            <Box sx={{ width: '100%', height: 450 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart 
                  data={moduleChartData} 
                  margin={{ top: 10, right: 30, left: 10, bottom: 80 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="name" 
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
                  <Bar dataKey="测试用例" fill="#1976d2" radius={[6, 6, 0, 0]} barSize={50} />
                  <Bar dataKey="BUG数" fill="#f44336" radius={[6, 6, 0, 0]} barSize={50} />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
              BUG 趋势预测（未来7天）
            </Typography>
            <Box sx={{ width: '100%', height: 450 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart 
                  data={bugTrend} 
                  margin={{ top: 10, right: 30, left: 10, bottom: 80 }}
                >
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
                  <Bar dataKey="predicted_bugs" name="预测BUG数" fill="#ff9800" radius={[6, 6, 0, 0]} barSize={50} />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* 模块详情表格 */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
            模块质量详情
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>模块名称</TableCell>
                  <TableCell align="right">需求数</TableCell>
                  <TableCell align="right">测试用例</TableCell>
                  <TableCell align="right">BUG数</TableCell>
                  <TableCell align="right">缺陷密度</TableCell>
                  <TableCell align="right">风险等级</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {qualityData?.module_metrics?.map((row) => (
                  <TableRow key={row.module}>
                    <TableCell component="th" scope="row">
                      {row.module}
                    </TableCell>
                    <TableCell align="right">{row.total_requirements}</TableCell>
                    <TableCell align="right">{row.total_test_cases}</TableCell>
                    <TableCell align="right">{row.total_bugs}</TableCell>
                    <TableCell align="right">{row.defect_density}</TableCell>
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
    </Box>
  );
}

export default Dashboard;
