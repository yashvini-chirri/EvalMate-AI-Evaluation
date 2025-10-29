import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import StudentDashboard from './pages/student/StudentDashboard';
import ExaminerDashboard from './pages/examiner/ExaminerDashboard';
import TestDetails from './pages/student/TestDetails';
import EvaluationResults from './pages/student/EvaluationResults';
import CreateTest from './pages/examiner/CreateTest';
import TestManagement from './pages/examiner/TestManagement';
import './App.css';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={<Navigate to="/login" replace />} />
            
            {/* Student Routes */}
            <Route
              path="/student/dashboard"
              element={
                <ProtectedRoute userType="student">
                  <StudentDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/student/test/:testId"
              element={
                <ProtectedRoute userType="student">
                  <TestDetails />
                </ProtectedRoute>
              }
            />
            <Route
              path="/student/evaluation/:evaluationId"
              element={
                <ProtectedRoute userType="student">
                  <EvaluationResults />
                </ProtectedRoute>
              }
            />
            
            {/* Examiner Routes */}
            <Route
              path="/examiner/dashboard"
              element={
                <ProtectedRoute userType="examiner">
                  <ExaminerDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/examiner/create-test"
              element={
                <ProtectedRoute userType="examiner">
                  <CreateTest />
                </ProtectedRoute>
              }
            />
            <Route
              path="/examiner/tests"
              element={
                <ProtectedRoute userType="examiner">
                  <TestManagement />
                </ProtectedRoute>
              }
            />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;