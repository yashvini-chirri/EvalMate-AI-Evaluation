import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { CircularProgress, Box } from '@mui/material';

export const ProtectedRoute = ({ children, userType }) => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Check user type if specified
  if (userType && user?.user_type !== userType) {
    const redirectPath = user?.user_type === 'student' ? '/student/dashboard' : '/examiner/dashboard';
    return <Navigate to={redirectPath} replace />;
  }

  return children;
};