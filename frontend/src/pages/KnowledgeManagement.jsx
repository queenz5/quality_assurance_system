import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Alert,
  Tabs,
  Tab,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Search,
  School,
  BugReport,
  Help,
} from '@mui/icons-material';
import { knowledgeAPI } from '../services/api';

function KnowledgeManagement() {
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [trainingMaterials, setTrainingMaterials] = useState([]);
  const [historicalBugs, setHistoricalBugs] = useState([]);
  const [qaPairs, setQaPairs] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [trainingRes, bugsRes, qaRes] = await Promise.all([
        knowledgeAPI.getTrainingMaterials(),
        knowledgeAPI.getHistoricalBugs(15),
        knowledgeAPI.getQAPairs(),
      ]);

      setTrainingMaterials(trainingRes.data.materials);
      setHistoricalBugs(bugsRes.data.bugs);
      setQaPairs(qaRes.data.qa_pairs);
    } catch (error) {
      console.error('Failed to load knowledge data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery) return;
    
    try {
      setLoading(true);
      const response = await knowledgeAPI.search(searchQuery);
      setSearchResults(response.data.results);
      setActiveTab(1);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
        知识管理
      </Typography>

      {/* 搜索框 */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
            智能搜索
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              label="输入关键词搜索（如：用户登录、权限等）"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              fullWidth
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button
              variant="contained"
              startIcon={<Search />}
              onClick={handleSearch}
              disabled={!searchQuery}
            >
              搜索
            </Button>
          </Box>

          {searchResults.length > 0 && (
            <Alert severity="success" sx={{ mt: 2 }}>
              找到 {searchResults.length} 个结果
            </Alert>
          )}

          <List sx={{ mt: 2 }}>
            {searchResults.slice(0, 10).map((result, index) => (
              <ListItem
                key={index}
                sx={{
                  border: 1,
                  borderColor: 'divider',
                  borderRadius: 2,
                  mb: 1,
                }}
              >
                <ListItemIcon>
                  <Chip
                    label={result.result_type}
                    color="primary"
                    size="small"
                  />
                </ListItemIcon>
                <ListItemText
                  primary={result.title}
                  secondary={
                    <Box sx={{ mt: 0.5 }}>
                      <Typography variant="body2" color="textSecondary">
                        {result.description}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        模块: {result.module} | 相关性: {(result.relevance_score * 100).toFixed(0)}%
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ mb: 3 }}>
        <Tab label="培训材料" icon={<School />} iconPosition="start" />
        <Tab label="历史BUG案例" icon={<BugReport />} iconPosition="start" />
        <Tab label="常见问答" icon={<Help />} iconPosition="start" />
      </Tabs>

      {/* 培训材料 */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {trainingMaterials.map((material, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
                    {material.module}模块
                  </Typography>
                  <Typography variant="body2" color="textSecondary" paragraph>
                    {material.overview}
                  </Typography>

                  {material.best_practices.length > 0 && (
                    <Alert severity="info" sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                        最佳实践
                      </Typography>
                      <List dense>
                        {material.best_practices.map((practice, i) => (
                          <ListItem key={i}>
                            <ListItemText primary={`• ${practice}`} />
                          </ListItem>
                        ))}
                      </List>
                    </Alert>
                  )}

                  {material.common_bugs.length > 0 && (
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography variant="body2">常见BUG ({material.common_bugs.length}个)</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List dense>
                          {material.common_bugs.slice(0, 5).map((bug, i) => (
                            <ListItem key={i}>
                              <ListItemText
                                primary={bug.title}
                                secondary={`严重程度: ${bug.severity} | 根因: ${bug.root_cause}`}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* 历史BUG案例 */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          {historicalBugs.map((bug, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                      {bug.title}
                    </Typography>
                    <Chip
                      label={bug.severity}
                      color={bug.severity === '严重' ? 'error' : 'default'}
                      size="small"
                    />
                  </Box>

                  <Typography variant="body2" color="textSecondary" paragraph>
                    模块: {bug.module}
                  </Typography>

                  {bug.root_cause && (
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>根因:</strong> {bug.root_cause}
                    </Typography>
                  )}

                  {bug.fix_solution && (
                    <Alert severity="success" sx={{ mb: 2 }}>
                      <Typography variant="body2">
                        <strong>修复方案:</strong> {bug.fix_solution}
                      </Typography>
                    </Alert>
                  )}

                  {bug.lessons_learned.length > 0 && (
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
                        经验教训:
                      </Typography>
                      {bug.lessons_learned.map((lesson, i) => (
                        <Typography key={i} variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                          • {lesson}
                        </Typography>
                      ))}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* 常见问答 */}
      {activeTab === 2 && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
              常见问答 ({qaPairs.length}个)
            </Typography>
            <List>
              {qaPairs.map((qa, index) => (
                <ListItem key={index}>
                  <Accordion sx={{ width: '100%' }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        Q: {qa.question}
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2" color="textSecondary">
                        A: {qa.answer}
                      </Typography>
                    </AccordionDetails>
                  </Accordion>
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

export default KnowledgeManagement;
