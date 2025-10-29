import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Box,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';

const ExaminerDashboard = () => {
  const [tests, setTests] = useState([]);
  const [evaluations, setEvaluations] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [testsResponse, evaluationsResponse] = await Promise.all([
        api.get('/examiners/tests'),
        api.get('/examiners/evaluations')
      ]);
      setTests(testsResponse.data);
      setEvaluations(evaluationsResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Examiner Dashboard
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/create-test')}
        >
          Create New Test
        </Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                Your Tests
              </Typography>
              {tests.length === 0 ? (
                <Typography color="text.secondary">
                  No tests created yet. Click "Create New Test" to get started.
                </Typography>
              ) : (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Test Title</TableCell>
                        <TableCell>Subject</TableCell>
                        <TableCell>Due Date</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Submissions</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {tests.map((test) => (
                        <TableRow key={test.id}>
                          <TableCell>{test.title}</TableCell>
                          <TableCell>{test.subject}</TableCell>
                          <TableCell>{new Date(test.due_date).toLocaleDateString()}</TableCell>
                          <TableCell>
                            <Chip
                              label={test.status}
                              color={test.status === 'active' ? 'success' : 'default'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{test.submission_count || 0}</TableCell>
                          <TableCell>
                            <Button
                              variant="outlined"
                              size="small"
                              onClick={() => navigate(`/test-management/${test.id}`)}
                              sx={{ mr: 1 }}
                            >
                              Manage
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                Recent Evaluations
              </Typography>
              {evaluations.length === 0 ? (
                <Typography color="text.secondary">
                  No evaluations performed yet.
                </Typography>
              ) : (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Student</TableCell>
                        <TableCell>Test</TableCell>
                        <TableCell>Score</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Evaluated On</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {evaluations.slice(0, 10).map((evaluation) => (
                        <TableRow key={evaluation.id}>
                          <TableCell>{evaluation.student_name}</TableCell>
                          <TableCell>{evaluation.test_title}</TableCell>
                          <TableCell>{evaluation.score}</TableCell>
                          <TableCell>
                            <Chip
                              label={evaluation.status}
                              color={evaluation.status === 'completed' ? 'success' : 'warning'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {new Date(evaluation.created_at).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <Button
                              variant="outlined"
                              size="small"
                              onClick={() => navigate(`/evaluation/${evaluation.id}`)}
                            >
                              View Details
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ExaminerDashboard;