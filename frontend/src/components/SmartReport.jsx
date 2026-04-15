import { useState, useEffect } from 'react';
import axios from 'axios';
import { Typography, Grid, Card, CardContent, Box, CircularProgress, TextField, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function SmartReport() {
  const [projectReport, setProjectReport] = useState(null);
  const [module, setModule] = useState('用户管理');
  const [moduleReport, setModuleReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [modules, setModules] = useState(['用户管理', '订单管理', '商品管理']);

  useEffect(() => {
    const fetchProjectReport = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/smart-report');
        setProjectReport(response.data);
      } catch (error) {
        console.error('Error fetching project report:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchProjectReport();
  }, []);

  useEffect(() => {
    const fetchModuleReport = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/module-report?module=${encodeURIComponent(module)}`);
        setModuleReport(response.data);
      } catch (error) {
        console.error('Error fetching module report:', error);
      }
    };
    if (module) {
      fetchModuleReport();
    }
  }, [module]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 1 }}>
      <Typography variant="h4" gutterBottom>
        智能报告
      </Typography>
      
      {/* 项目质量报告 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            项目质量报告
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="h6" color="text.secondary">
                    项目质量得分
                  </Typography>
                  <Typography variant="h4">
                    {projectReport.project_quality_score}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="h6" color="text.secondary">
                    缺陷密度
                  </Typography>
                  <Typography variant="h4">
                    {projectReport.defect_density.toFixed(2)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="h6" color="text.secondary">
                    需求覆盖率
                  </Typography>
                  <Typography variant="h4">
                    {(projectReport.requirement_coverage * 100).toFixed(0)}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="h6" color="text.secondary">
                    高风险模块数
                  </Typography>
                  <Typography variant="h4">
                    {projectReport.high_risk_modules.length}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
          
          {/* BUG趋势 */}
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              BUG趋势
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart
                data={projectReport.bug_trend}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="bugs" name="BUG数" stroke="#e74c3c" />
              </LineChart>
            </ResponsiveContainer>
          </Box>
          
          {/* 建议 */}
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              改进建议
            </Typography>
            <ul>
              {projectReport.recommendations.map((recommendation, index) => (
                <li key={index}>{recommendation}</li>
              ))}
            </ul>
          </Box>
        </CardContent>
      </Card>
      
      {/* 模块报告 */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            模块报告
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <TextField
              select
              label="选择模块"
              value={module}
              onChange={(e) => setModule(e.target.value)}
              SelectProps={{
                native: true,
              }}
            >
              {modules.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </TextField>
          </Box>
          
          {moduleReport && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="text.secondary">
                      模块质量得分
                    </Typography>
                    <Typography variant="h4">
                      {moduleReport.quality_score}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="text.secondary">
                      缺陷密度
                    </Typography>
                    <Typography variant="h4">
                      {moduleReport.defect_density.toFixed(2)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="text.secondary">
                      需求覆盖率
                    </Typography>
                    <Typography variant="h4">
                      {(moduleReport.requirement_coverage * 100).toFixed(0)}%
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="text.secondary">
                      总需求数
                    </Typography>
                    <Typography variant="h4">
                      {moduleReport.total_requirements}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="text.secondary">
                      总测试用例数
                    </Typography>
                    <Typography variant="h4">
                      {moduleReport.total_test_cases}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="text.secondary">
                      总BUG数
                    </Typography>
                    <Typography variant="h4">
                      {moduleReport.total_bugs}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="text.secondary">
                      修复率
                    </Typography>
                    <Typography variant="h4">
                      {(moduleReport.fix_rate * 100).toFixed(0)}%
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}

export default SmartReport;