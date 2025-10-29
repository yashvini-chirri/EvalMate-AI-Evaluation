import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  FileUpload as FileUploadIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';

const TestManagement = () => {
  const [test, setTest] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editData, setEditData] = useState({});
  const { testId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    fetchTestData();
  }, [testId]);

  const fetchTestData = async () => {
    try {
      const [testResponse, submissionsResponse] = await Promise.all([
        api.get(`/tests/${testId}`),
        api.get(`/tests/${testId}/submissions`)
      ]);
      setTest(testResponse.data);
      setSubmissions(submissionsResponse.data);
      setEditData(testResponse.data);
    } catch (error) {
      console.error('Error fetching test data:', error);
      setError('Failed to load test data');
    } finally {
      setLoading(false);
    }
  };

  const handleEditTest = async () => {
    try {
      await api.put(`/tests/${testId}`, editData);
      setTest(editData);
      setEditDialogOpen(false);
    } catch (error) {
      console.error('Error updating test:', error);
      setError('Failed to update test');
    }
  };

  const handleDeleteTest = async () => {
    if (window.confirm('Are you sure you want to delete this test? This action cannot be undone.')) {
      try {
        await api.delete(`/tests/${testId}`);
        navigate('/dashboard');
      } catch (error) {
        console.error('Error deleting test:', error);
        setError('Failed to delete test');
      }
    }
  };

  const handleEvaluateSubmission = async (submissionId) => {
    try {
      // Trigger AI evaluation
      await api.post(`/evaluations/evaluate/${submissionId}`);
      // Refresh submissions to show updated status
      fetchTestData();
    } catch (error) {
      console.error('Error evaluating submission:', error);
      setError('Failed to evaluate submission');
    }
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!test) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="warning">Test not found</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 3 }}>
        <Button onClick={() => navigate('/dashboard')} sx={{ mb: 2 }}>
          ← Back to Dashboard
        </Button>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h4" component="h1">
            Manage Test: {test.title}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              startIcon={<EditIcon />}
              onClick={() => setEditDialogOpen(true)}
              variant="outlined"
            >
              Edit Test
            </Button>
            <Button
              startIcon={<DeleteIcon />}
              onClick={handleDeleteTest}
              variant="outlined"
              color="error"
            >
              Delete Test
            </Button>
          </Box>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Test Overview
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Subject:</Typography>
                <Typography variant="body2">{test.subject}</Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Due Date:</Typography>
                <Typography variant="body2">
                  {new Date(test.due_date).toLocaleDateString()}
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Status:</Typography>
                <Chip
                  label={test.status}
                  color={test.status === 'active' ? 'success' : 'default'}
                  size="small"
                />
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Total Marks:</Typography>
                <Typography variant="body2">{test.total_marks}</Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Submissions:</Typography>
                <Typography variant="body2">{submissions.length}</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Student Submissions
              </Typography>
              {submissions.length === 0 ? (
                <Typography color="text.secondary">
                  No submissions yet.
                </Typography>
              ) : (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Student</TableCell>
                        <TableCell>Submitted On</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Score</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {submissions.map((submission) => (
                        <TableRow key={submission.id}>
                          <TableCell>{submission.student_name}</TableCell>
                          <TableCell>
                            {new Date(submission.created_at).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={submission.status || 'submitted'}
                              color={submission.status === 'evaluated' ? 'success' : 'warning'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {submission.score !== null ? submission.score : 'Not evaluated'}
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                              <Tooltip title="View Submission">
                                <IconButton
                                  size="small"
                                  onClick={() => navigate(`/submission/${submission.id}`)}
                                >
                                  <ViewIcon />
                                </IconButton>
                              </Tooltip>
                              {(!submission.status || submission.status !== 'evaluated') && (
                                <Tooltip title="Evaluate with AI">
                                  <IconButton
                                    size="small"
                                    onClick={() => handleEvaluateSubmission(submission.id)}
                                    color="primary"
                                  >
                                    <FileUploadIcon />
                                  </IconButton>
                                </Tooltip>
                              )}
                            </Box>
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

      {/* Edit Test Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit Test</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Title"
                value={editData.title || ''}
                onChange={(e) => setEditData({ ...editData, title: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Subject"
                value={editData.subject || ''}
                onChange={(e) => setEditData({ ...editData, subject: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="date"
                label="Due Date"
                value={editData.due_date ? editData.due_date.split('T')[0] : ''}
                onChange={(e) => setEditData({ ...editData, due_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={editData.description || ''}
                onChange={(e) => setEditData({ ...editData, description: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleEditTest} variant="contained">Save Changes</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default TestManagement;