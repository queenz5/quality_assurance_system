import { useState, useEffect } from 'react';
import axios from 'axios';
import { Typography, Grid, Card, CardContent, Box, CircularProgress } from '@mui/material';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function Home() {
  const [data, setData] = useState({
    requirements: [],
    testCases: [],
    bugs: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [requirementsRes, testCasesRes, bugsRes] = await Promise.all([
          axios.get('http://localhost:8000/api/requirements'),
          axios.get('http://localhost:8000/api/test-cases'),
          axios.get('http://localhost:8000/api/bugs')
        ]);
        setData({
          requirements: requirementsRes.data,
          testCases: testCasesRes.data,
          bugs: bugsRes.data
        });
      } catch (error) {
        console.error('Error fetching data:', error);
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

  // 统计数据
  const totalRequirements = data.requirements.length;
  const totalTestCases = data.testCases.length;
  const totalBugs = data.bugs.length;

  // 按模块统计
  const moduleStats = {};
  data.requirements.forEach(req => {
    if (!moduleStats[req.module]) {
      moduleStats[req.module] = { requirements: 0, testCases: 0, bugs: 0 };
    }
    moduleStats[req.module].requirements++;
  });

  data.testCases.forEach(tc => {
    if (moduleStats[tc.module]) {
      moduleStats[tc.module].testCases++;
    }
  });

  data.bugs.forEach(bug => {
    if (moduleStats[bug.module]) {
      moduleStats[bug.module].bugs++;
    }
  });

  const moduleData = Object.entries(moduleStats).map(([module, stats]) => ({
    module,
    ...stats
  }));

  // 饼图数据
  const pieData = [
    { name: '需求', value: totalRequirements, color: '#3498db' },
    { name: '测试用例', value: totalTestCases, color: '#2ecc71' },
    { name: 'BUG', value: totalBugs, color: '#e74c3c' }
  ];

  return (
    <Box sx={{ p: 1 }}>
      <Typography variant="h4" gutterBottom>
        系统概览
      </Typography>
      
      {/* 总览卡片 */}
      <Grid container spacing={2} mb={2}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ p: 1.5 }}>
              <Typography variant="h6" color="text.secondary">
                总需求数
              </Typography>
              <Typography variant="h4">
                {totalRequirements}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ p: 1.5 }}>
              <Typography variant="h6" color="text.secondary">
                总测试用例数
              </Typography>
              <Typography variant="h4">
                {totalTestCases}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ p: 1.5 }}>
              <Typography variant="h6" color="text.secondary">
                总BUG数
              </Typography>
              <Typography variant="h4">
                {totalBugs}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 图表 */}
      <Grid container spacing={2} sx={{ width: '100%' }}>
        {/* 饼图 */}
        <Grid item xs={12} md={4}>
          <Card sx={{ width: '100%' }}>
            <CardContent sx={{ p: 1.5, height: 400 }}>
              <Typography variant="h6" gutterBottom>
                数据分布
              </Typography>
              <ResponsiveContainer width="100%" height="80%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* 模块统计 */}
        <Grid item xs={12} md={8}>
          <Card sx={{ width: '100%' }}>
            <CardContent sx={{ p: 1.5, height: 400 }}>
              <Typography variant="h6" gutterBottom>
                模块统计
              </Typography>
              <ResponsiveContainer width="100%" height="80%">
                <BarChart
                  data={moduleData}
                  margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="module" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="requirements" name="需求" fill="#3498db" />
                  <Bar dataKey="testCases" name="测试用例" fill="#2ecc71" />
                  <Bar dataKey="bugs" name="BUG" fill="#e74c3c" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Home;