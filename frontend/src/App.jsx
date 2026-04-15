import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import RequirementAnalysis from './pages/RequirementAnalysisMarkdown';
import TestCaseGeneration from './pages/TestCaseGeneration';
import QualityAnalysis from './pages/QualityAnalysis';
import AITesting from './pages/AITesting';
import KnowledgeManagement from './pages/KnowledgeManagement';
import SmartReport from './pages/SmartReport';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#9c27b0',
      light: '#ba68c8',
      dark: '#7b1fa2',
    },
    success: {
      main: '#4caf50',
    },
    warning: {
      main: '#ff9800',
    },
    error: {
      main: '#f44336',
    },
  },
  typography: {
    fontFamily: '"PingFang SC", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Box sx={{ pt: 8 }}>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/requirement-analysis" element={<RequirementAnalysis />} />
              <Route path="/testcase-generation" element={<TestCaseGeneration />} />
              <Route path="/quality" element={<QualityAnalysis />} />
              <Route path="/ai-testing" element={<AITesting />} />
              <Route path="/knowledge" element={<KnowledgeManagement />} />
              <Route path="/report" element={<SmartReport />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Box>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
