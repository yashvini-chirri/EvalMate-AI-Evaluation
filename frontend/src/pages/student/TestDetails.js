import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Box,
  Paper,
  CircularProgress,
  Alert,
  Chip
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';

const TestDetails = () => {
  const [test, setTest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { testId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    fetchTestDetails();
  }, [testId]);

  const fetchTestDetails = async () => {
    try {
      const response = await api.get(`/tests/${testId}`);
      setTest(response.data);
    } catch (error) {
      console.error('Error fetching test details:', error);
      setError('Failed to load test details');
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
        <Button onClick={() => navigate(-1)} sx={{ mb: 2 }}>
          ← Back
        </Button>
        <Typography variant="h4" component="h1" gutterBottom>
          {test.title}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Test Information
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" component="dt" fontWeight="bold">
                  Subject:
                </Typography>
                <Typography variant="body1" component="dd">
                  {test.subject}
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" component="dt" fontWeight="bold">
                  Description:
                </Typography>
                <Typography variant="body1" component="dd">
                  {test.description || 'No description provided'}
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" component="dt" fontWeight="bold">
                  Instructions:
                </Typography>
                <Typography variant="body1" component="dd">
                  {test.instructions || 'No specific instructions'}
                </Typography>
              </Box>
            </CardContent>
          </Card>

          {test.questions && test.questions.length > 0 && (
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Questions
                </Typography>
                {test.questions.map((question, index) => (
                  <Paper key={index} sx={{ p: 2, mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Question {index + 1}:
                    </Typography>
                    <Typography variant="body1">
                      {question.text || question.question}
                    </Typography>
                    {question.marks && (
                      <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                        Marks: {question.marks}
                      </Typography>
                    )}
                  </Paper>
                ))}
              </CardContent>
            </Card>
          )}
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Test Details
              </Typography>
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
              {test.total_marks && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">Total Marks:</Typography>
                  <Typography variant="body2">{test.total_marks}</Typography>
                </Box>
              )}
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Created:</Typography>
                <Typography variant="body2">
                  {new Date(test.created_at).toLocaleDateString()}
                </Typography>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Actions
              </Typography>
              <Button
                variant="contained"
                fullWidth
                sx={{ mb: 1 }}
                onClick={() => navigate(`/submit-answer/${testId}`)}
              >
                Submit Answer Sheet
              </Button>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => navigate('/dashboard')}
              >
                Back to Dashboard
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default TestDetails;