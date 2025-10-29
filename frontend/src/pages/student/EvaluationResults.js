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
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import { ExpandMore as ExpandMoreIcon } from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';

const EvaluationResults = () => {
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { evaluationId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    fetchEvaluationResults();
  }, [evaluationId]);

  const fetchEvaluationResults = async () => {
    try {
      const response = await api.get(`/evaluations/${evaluationId}`);
      setEvaluation(response.data);
    } catch (error) {
      console.error('Error fetching evaluation results:', error);
      setError('Failed to load evaluation results');
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

  if (!evaluation) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="warning">Evaluation results not found</Alert>
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
          Evaluation Results
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Overview
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Test:</Typography>
                <Typography variant="body2">{evaluation.test_title}</Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Score:</Typography>
                <Typography variant="h4" color="primary">
                  {evaluation.score}
                  {evaluation.total_marks && `/${evaluation.total_marks}`}
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Status:</Typography>
                <Chip
                  label={evaluation.status}
                  color={evaluation.status === 'completed' ? 'success' : 'warning'}
                  size="small"
                />
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Evaluated On:</Typography>
                <Typography variant="body2">
                  {new Date(evaluation.created_at).toLocaleDateString()}
                </Typography>
              </Box>
              {evaluation.percentage && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">Percentage:</Typography>
                  <Typography variant="body2">{evaluation.percentage}%</Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Detailed Feedback
              </Typography>
              
              {evaluation.overall_feedback && (
                <Alert severity="info" sx={{ mb: 3 }}>
                  <Typography variant="subtitle2">Overall Feedback:</Typography>
                  <Typography variant="body2">{evaluation.overall_feedback}</Typography>
                </Alert>
              )}

              {evaluation.question_feedback && evaluation.question_feedback.length > 0 && (
                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    Question-wise Analysis
                  </Typography>
                  {evaluation.question_feedback.map((feedback, index) => (
                    <Accordion key={index} sx={{ mb: 1 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography variant="subtitle2">
                          Question {index + 1}: {feedback.score || 0}/{feedback.max_marks || '-'} marks
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Box>
                          <Typography variant="body2" sx={{ mb: 2 }}>
                            <strong>Student Answer:</strong>
                          </Typography>
                          <Paper sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
                            <Typography variant="body2">
                              {feedback.student_answer || 'No answer provided'}
                            </Typography>
                          </Paper>
                          
                          <Typography variant="body2" sx={{ mb: 2 }}>
                            <strong>Feedback:</strong>
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {feedback.feedback || 'No specific feedback provided'}
                          </Typography>
                          
                          {feedback.correct_answer && (
                            <>
                              <Typography variant="body2" sx={{ mb: 1, mt: 2 }}>
                                <strong>Expected Answer:</strong>
                              </Typography>
                              <Paper sx={{ p: 2, bgcolor: 'success.light' }}>
                                <Typography variant="body2">
                                  {feedback.correct_answer}
                                </Typography>
                              </Paper>
                            </>
                          )}
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>
              )}

              {evaluation.evaluation_details && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Evaluation Details
                  </Typography>
                  <TableContainer component={Paper}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Criterion</TableCell>
                          <TableCell>Score</TableCell>
                          <TableCell>Comments</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {Object.entries(evaluation.evaluation_details).map(([key, value]) => (
                          <TableRow key={key}>
                            <TableCell>{key.replace(/_/g, ' ').toUpperCase()}</TableCell>
                            <TableCell>{value.score || '-'}</TableCell>
                            <TableCell>{value.comment || '-'}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default EvaluationResults;