import { useState, useEffect } from 'react';
import axios from 'axios';
import { Typography, Grid, Card, CardContent, Box, CircularProgress, TextField, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Tabs, Tab } from '@mui/material';

function AIAssistedTesting() {
  const [requirements, setRequirements] = useState([]);
  const [bugs, setBugs] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const [inputValue, setInputValue] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [requirementsRes, bugsRes] = await Promise.all([
          axios.get('http://localhost:8000/api/requirements'),
          axios.get('http://localhost:8000/api/bugs')
        ]);
        setRequirements(requirementsRes.data);
        setBugs(bugsRes.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
    fetchData();
  }, []);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      let response;
      if (activeTab === 0) {
        // 智能用例生成
        response = await axios.get(`http://localhost:8000/api/ai-assisted-test?requirement_id=${inputValue}`);
      } else if (activeTab === 1) {
        // BUG根因分析
        response = await axios.get(`http://localhost:8000/api/ai-assisted-test?bug_id=${inputValue}`);
      } else if (activeTab === 2) {
        // 用例推荐
        response = await axios.get(`http://localhost:8000/api/ai-assisted-test?code_file=${inputValue}`);
      }
      setResult(response.data);
    } catch (error) {
      console.error('Error fetching AI assistance:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 1 }}>
      <Typography variant="h4" gutterBottom>
        AI辅助测试
      </Typography>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="智能用例生成" />
          <Tab label="BUG根因分析" />
          <Tab label="用例推荐" />
        </Tabs>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {activeTab === 0 ? '智能用例生成' : activeTab === 1 ? 'BUG根因分析' : '用例推荐'}
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            {activeTab === 0 && (
              <TextField
                select
                label="选择需求"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                fullWidth
                selectProps={{
                  native: true,
                }}
              >
                <option value="">请选择需求</option>
                {requirements.map((req) => (
                  <option key={req.id} value={req.id}>
                    {req.id}: {req.title}
                  </option>
                ))}
              </TextField>
            )}
            
            {activeTab === 1 && (
              <TextField
                select
                label="选择BUG"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                fullWidth
                selectProps={{
                  native: true,
                }}
              >
                <option value="">请选择BUG</option>
                {bugs.map((bug) => (
                  <option key={bug.id} value={bug.id}>
                    {bug.id}: {bug.title}
                  </option>
                ))}
              </TextField>
            )}
            
            {activeTab === 2 && (
              <TextField
                label="代码文件路径"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                fullWidth
                placeholder="例如: user.py"
              />
            )}
            
            <Button variant="contained" onClick={handleSubmit} disabled={!inputValue}>
              分析
            </Button>
          </Box>
          
          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          )}
          
          {result && (
            <Box sx={{ mt: 3 }}>
              {activeTab === 0 && result.generated_test_cases.length > 0 && (
                <>
                  <Typography variant="subtitle1" gutterBottom>
                    生成的测试用例:
                  </Typography>
                  <TableContainer component={Paper}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>测试用例ID</TableCell>
                          <TableCell>标题</TableCell>
                          <TableCell>优先级</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {result.generated_test_cases.map((tc, index) => (
                          <TableRow key={index}>
                            <TableCell component="th" scope="row">
                              {tc.id}
                            </TableCell>
                            <TableCell>{tc.title}</TableCell>
                            <TableCell>{tc.priority}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </>
              )}
              
              {activeTab === 1 && Object.keys(result.bug_analysis).length > 0 && (
                <>
                  <Typography variant="subtitle1" gutterBottom>
                    BUG分析结果:
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      <strong>BUG信息:</strong> {result.bug_analysis.bug_info?.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      <strong>模块:</strong> {result.bug_analysis.bug_info?.module}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      <strong>严重程度:</strong> {result.bug_analysis.bug_info?.severity}
                    </Typography>
                  </Box>
                  
                  {result.bug_analysis.recommended_root_causes && result.bug_analysis.recommended_root_causes.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        推荐的根因:
                      </Typography>
                      <ul>
                        {result.bug_analysis.recommended_root_causes.map((cause, index) => (
                          <li key={index}>{cause}</li>
                        ))}
                      </ul>
                    </Box>
                  )}
                  
                  {result.bug_analysis.similar_bugs && result.bug_analysis.similar_bugs.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        相似BUG:
                      </Typography>
                      <TableContainer component={Paper}>
                        <Table>
                          <TableHead>
                            <TableRow>
                              <TableCell>BUG ID</TableCell>
                              <TableCell>标题</TableCell>
                              <TableCell>根因</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {result.bug_analysis.similar_bugs.map((bug, index) => (
                              <TableRow key={index}>
                                <TableCell component="th" scope="row">
                                  {bug.id}
                                </TableCell>
                                <TableCell>{bug.title}</TableCell>
                                <TableCell>{bug.root_cause}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </Box>
                  )}
                  
                  {result.bug_analysis.suggested_fix && (
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        建议修复方案:
                      </Typography>
                      <Typography variant="body2">
                        {result.bug_analysis.suggested_fix}
                      </Typography>
                    </Box>
                  )}
                </>
              )}
              
              {activeTab === 2 && result.recommended_test_cases.length > 0 && (
                <>
                  <Typography variant="subtitle1" gutterBottom>
                    推荐的测试用例:
                  </Typography>
                  <TableContainer component={Paper}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>测试用例ID</TableCell>
                          <TableCell>标题</TableCell>
                          <TableCell align="right">相关度分数</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {result.recommended_test_cases.map((tc, index) => (
                          <TableRow key={index}>
                            <TableCell component="th" scope="row">
                              {tc.test_case_id}
                            </TableCell>
                            <TableCell>{tc.test_case_title}</TableCell>
                            <TableCell align="right">{tc.relevance_score.toFixed(2)}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </>
              )}
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}

export default AIAssistedTesting;