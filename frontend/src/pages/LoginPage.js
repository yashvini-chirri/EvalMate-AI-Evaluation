import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Container,
  Alert,
  Tabs,
  Tab,
  CircularProgress,
  Paper,
  Chip
} from '@mui/material';
import { School, Person } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const LoginPage = () => {
  const [userType, setUserType] = useState('student');
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleTabChange = (event, newValue) => {
    setUserType(newValue);
    setError('');
    setCredentials({ username: '', password: '' });
  };

  const handleInputChange = (field) => (event) => {
    setCredentials(prev => ({
      ...prev,
      [field]: event.target.value
    }));
    setError('');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await login(credentials.username, credentials.password, userType);
      
      if (result.success) {
        const redirectPath = result.userType === 'student' ? '/student/dashboard' : '/examiner/dashboard';
        navigate(redirectPath);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getSampleCredentials = () => {
    if (userType === 'student') {
      return [
        { username: 'student_10th_a_01', password: 'pass_10tha01', desc: '10th Grade A, Roll 1' },
        { username: 'student_11th_b_15', password: 'pass_11thb15', desc: '11th Grade B, Roll 15' },
        { username: 'student_12th_a_20', password: 'pass_12tha20', desc: '12th Grade A, Roll 20' },
      ];
    } else {
      return [
        { username: 'examiner_math', password: 'math123', desc: 'Mathematics Teacher' },
        { username: 'examiner_science', password: 'science123', desc: 'Science Teacher' },
        { username: 'examiner_english', password: 'english123', desc: 'English Teacher' },
      ];
    }
  };

  const fillSampleCredentials = (username, password) => {
    setCredentials({ username, password });
  };

  return (
    <Box className="gradient-bg" minHeight="100vh" display="flex" alignItems="center">
      <Container maxWidth="md">
        <Paper elevation={24} sx={{ borderRadius: 4, overflow: 'hidden' }}>
          <Box p={4}>
            <Box textAlign="center" mb={4}>
              <Typography variant="h3" component="h1" className="text-gradient" gutterBottom>
                EvalMate
              </Typography>
              <Typography variant="h6" color="text.secondary">
                AI-powered Answer Sheet Evaluation System
              </Typography>
            </Box>

            <Card elevation={0} sx={{ mb: 4 }}>
              <Tabs 
                value={userType} 
                onChange={handleTabChange} 
                centered
                sx={{ borderBottom: 1, borderColor: 'divider' }}
              >
                <Tab 
                  value="student" 
                  label="Student Login" 
                  icon={<School />} 
                  iconPosition="start"
                />
                <Tab 
                  value="examiner" 
                  label="Examiner Login" 
                  icon={<Person />} 
                  iconPosition="start"
                />
              </Tabs>

              <CardContent sx={{ pt: 3 }}>
                <form onSubmit={handleSubmit}>
                  <TextField
                    fullWidth
                    label="Username"
                    value={credentials.username}
                    onChange={handleInputChange('username')}
                    margin="normal"
                    required
                    disabled={loading}
                    autoComplete="username"
                  />
                  <TextField
                    fullWidth
                    label="Password"
                    type="password"
                    value={credentials.password}
                    onChange={handleInputChange('password')}
                    margin="normal"
                    required
                    disabled={loading}
                    autoComplete="current-password"
                  />

                  {error && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                      {error}
                    </Alert>
                  )}

                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    size="large"
                    disabled={loading}
                    sx={{ mt: 3, mb: 2, py: 1.5 }}
                  >
                    {loading ? (
                      <CircularProgress size={24} color="inherit" />
                    ) : (
                      `Login as ${userType === 'student' ? 'Student' : 'Examiner'}`
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Sample Credentials */}
            <Card elevation={1}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📝 Sample Credentials
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Use these sample credentials to test the system:
                </Typography>
                <Box display="flex" flexDirection="column" gap={1}>
                  {getSampleCredentials().map((cred, index) => (
                    <Box key={index} display="flex" alignItems="center" gap={2} flexWrap="wrap">
                      <Chip 
                        label={cred.desc}
                        variant="outlined"
                        size="small"
                      />
                      <Button
                        size="small"
                        onClick={() => fillSampleCredentials(cred.username, cred.password)}
                        sx={{ textTransform: 'none' }}
                      >
                        {cred.username}
                      </Button>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default LoginPage;