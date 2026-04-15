import { useState, useEffect } from 'react';
import axios from 'axios';
import { Typography, Grid, Card, CardContent, Box, CircularProgress, TextField, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Tabs, Tab } from '@mui/material';

function KnowledgeManagement() {
  const [activeTab, setActiveTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [trainingMaterials, setTrainingMaterials] = useState([]);
  const [historicalBugs, setHistoricalBugs] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await axios.get('http://localhost:8000/api/knowledge-management');
        setTrainingMaterials(response.data.training_materials);
        setHistoricalBugs(response.data.historical_bugs);
      } catch (error) {
        console.error('Error fetching knowledge data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSearch = async () => {
    if (!searchQuery) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/api/knowledge-management?query=${encodeURIComponent(searchQuery)}`);
      setSearchResults(response.data.search_results);
    } catch (error) {
      console.error('Error searching knowledge:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 1 }}>
      <Typography variant="h4" gutterBottom>
        知识管理
      </Typography>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="新人培训" />
          <Tab label="经验沉淀" />
          <Tab label="智能搜索" />
        </Tabs>
      </Box>

      {/* 智能搜索 */}
      {activeTab === 2 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              智能搜索
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <TextField
                label="搜索查询"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                fullWidth
                placeholder="输入关键词搜索需求、测试用例或BUG"
              />
              <Button variant="contained" onClick={handleSearch} disabled={!searchQuery}>
                搜索
              </Button>
            </Box>
            
            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            )}
            
            {searchResults.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  搜索结果 ({searchResults.length}):
                </Typography>
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>类型</TableCell>
                        <TableCell>ID</TableCell>
                        <TableCell>标题</TableCell>
                        <TableCell>模块</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {searchResults.map((result, index) => (
                        <TableRow key={index}>
                          <TableCell component="th" scope="row">
                            {result.type === 'requirement' ? '需求' : result.type === 'test_case' ? '测试用例' : 'BUG'}
                          </TableCell>
                          <TableCell>{result.id}</TableCell>
                          <TableCell>{result.title}</TableCell>
                          <TableCell>{result.module}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* 新人培训 */}
      {activeTab === 0 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            新人培训材料
          </Typography>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Grid container spacing={3}>
              {trainingMaterials.map((material, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card>
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>
                        {material.split('\n')[0].replace('# ', '')}
                      </Typography>
                      <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
                        {material.split('\n').slice(1).map((line, idx) => (
                          <Typography key={idx} variant="body2" sx={{ mb: 0.5 }}>
                            {line}
                          </Typography>
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      )}

      {/* 经验沉淀 */}
      {activeTab === 1 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            历史BUG与修复方案
          </Typography>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>BUG ID</TableCell>
                    <TableCell>标题</TableCell>
                    <TableCell>模块</TableCell>
                    <TableCell>根因</TableCell>
                    <TableCell>修复方案</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {historicalBugs.map((bug, index) => (
                    <TableRow key={index}>
                      <TableCell component="th" scope="row">
                        {bug.id}
                      </TableCell>
                      <TableCell>{bug.title}</TableCell>
                      <TableCell>{bug.module}</TableCell>
                      <TableCell>{bug.root_cause || '未知'}</TableCell>
                      <TableCell>{bug.fix_solution || '未提供'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Box>
      )}
    </Box>
  );
}

export default KnowledgeManagement;