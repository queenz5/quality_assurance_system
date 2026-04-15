import { useState, useEffect } from 'react';
import axios from 'axios';
import { Typography, Grid, Card, CardContent, Box, CircularProgress, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

function QualityAnalysis() {
  const [qualityData, setQualityData] = useState(null);
  const [bugTrend, setBugTrend] = useState([]);
  const [bugPrediction, setBugPrediction] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [qualityRes, trendRes, predictionRes] = await Promise.all([
          axios.get('http://localhost:8000/api/quality-analysis'),
          axios.get('http://localhost:8000/api/bug-trend'),
          axios.get('http://localhost:8000/api/bug-prediction')
        ]);
        setQualityData(qualityRes.data);
        setBugTrend(trendRes.data);
        setBugPrediction(predictionRes.data);
      } catch (error) {
        console.error('Error fetching quality data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  // 准备图表数据
  const defectDensityData = Object.entries(qualityData.defect_density).map(([module, density]) => ({
    module,
    density
  }));

  const coverageData = Object.entries(qualityData.requirement_coverage).map(([module, coverage]) => ({
    module,
    coverage: coverage * 100 // 转换为百分比
  }));

  return (
    <Box sx={{ p: 1 }}>
      <Typography variant="h4" gutterBottom>
        质量分析与预测
      </Typography>
      
      <Grid container spacing={3}>
        {/* 缺陷密度分析 */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                缺陷密度分析
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={defectDensityData}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="module" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="density" name="缺陷密度" fill="#e74c3c" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* 需求覆盖率 */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                需求覆盖率
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={coverageData}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="module" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip formatter={(value) => [`${value}%`, '覆盖率']} />
                  <Legend />
                  <Bar dataKey="coverage" name="覆盖率 (%)" fill="#3498db" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* 高风险模块 */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                高风险模块
              </Typography>
              {qualityData.high_risk_modules.length > 0 ? (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>模块名称</TableCell>
                        <TableCell align="right">缺陷密度</TableCell>
                        <TableCell align="right">需求覆盖率</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {qualityData.high_risk_modules.map((module) => (
                        <TableRow key={module}>
                          <TableCell component="th" scope="row">
                            {module}
                          </TableCell>
                          <TableCell align="right">
                            {qualityData.defect_density[module]?.toFixed(2) || 'N/A'}
                          </TableCell>
                          <TableCell align="right">
                            {(qualityData.requirement_coverage[module] * 100).toFixed(0)}%
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  暂无高风险模块
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* BUG趋势预测 */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                BUG趋势预测
              </Typography>
              {bugTrend.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart
                    data={bugTrend}
                    margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="predicted_bugs" name="预测BUG数" stroke="#9b59b6" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  暂无趋势数据
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* 模块BUG预测 */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                模块BUG预测
              </Typography>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>模块</TableCell>
                      <TableCell align="right">预测BUG数</TableCell>
                      <TableCell align="right">置信度</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {bugPrediction.map((prediction, index) => (
                      <TableRow key={index}>
                        <TableCell component="th" scope="row">
                          {prediction.module}
                        </TableCell>
                        <TableCell align="right">{prediction.predicted_bugs}</TableCell>
                        <TableCell align="right">{prediction.confidence.toFixed(2)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default QualityAnalysis;