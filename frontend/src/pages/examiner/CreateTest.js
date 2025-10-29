import React, { useState } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  Grid,
  Box,
  Paper,
  IconButton,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';

const CreateTest = () => {
  const [testData, setTestData] = useState({
    title: '',
    subject: '',
    description: '',
    instructions: '',
    due_date: '',
    total_marks: '',
    status: 'draft'
  });
  const [questions, setQuestions] = useState([
    { question: '', marks: '', answer_key: '' }
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleTestDataChange = (field, value) => {
    setTestData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleQuestionChange = (index, field, value) => {
    const updatedQuestions = [...questions];
    updatedQuestions[index][field] = value;
    setQuestions(updatedQuestions);
  };

  const addQuestion = () => {
    setQuestions([...questions, { question: '', marks: '', answer_key: '' }]);
  };

  const removeQuestion = (index) => {
    if (questions.length > 1) {
      const updatedQuestions = questions.filter((_, i) => i !== index);
      setQuestions(updatedQuestions);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const totalMarks = questions.reduce((sum, q) => sum + (parseInt(q.marks) || 0), 0);
      
      const payload = {
        ...testData,
        total_marks: totalMarks,
        questions: questions.filter(q => q.question.trim() !== ''),
        examiner_id: user.id
      };

      await api.post('/tests', payload);
      setSuccess(true);
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (error) {
      console.error('Error creating test:', error);
      setError('Failed to create test. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="success">
          Test created successfully! Redirecting to dashboard...
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 3 }}>
        <Button onClick={() => navigate(-1)} sx={{ mb: 2 }}>
          ← Back
        </Button>
        <Typography variant="h4" component="h1" gutterBottom>
          Create New Test
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Test Information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Test Title"
                  value={testData.title}
                  onChange={(e) => handleTestDataChange('title', e.target.value)}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Subject"
                  value={testData.subject}
                  onChange={(e) => handleTestDataChange('subject', e.target.value)}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="date"
                  label="Due Date"
                  value={testData.due_date}
                  onChange={(e) => handleTestDataChange('due_date', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Description"
                  value={testData.description}
                  onChange={(e) => handleTestDataChange('description', e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Instructions"
                  value={testData.instructions}
                  onChange={(e) => handleTestDataChange('instructions', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={testData.status}
                    onChange={(e) => handleTestDataChange('status', e.target.value)}
                    label="Status"
                  >
                    <MenuItem value="draft">Draft</MenuItem>
                    <MenuItem value="active">Active</MenuItem>
                    <MenuItem value="inactive">Inactive</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Questions
              </Typography>
              <Button
                startIcon={<AddIcon />}
                onClick={addQuestion}
                variant="outlined"
              >
                Add Question
              </Button>
            </Box>

            {questions.map((question, index) => (
              <Paper key={index} sx={{ p: 2, mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="subtitle1">
                    Question {index + 1}
                  </Typography>
                  {questions.length > 1 && (
                    <IconButton
                      onClick={() => removeQuestion(index)}
                      color="error"
                      size="small"
                    >
                      <DeleteIcon />
                    </IconButton>
                  )}
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      multiline
                      rows={3}
                      label="Question"
                      value={question.question}
                      onChange={(e) => handleQuestionChange(index, 'question', e.target.value)}
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      type="number"
                      label="Marks"
                      value={question.marks}
                      onChange={(e) => handleQuestionChange(index, 'marks', e.target.value)}
                      required
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      multiline
                      rows={2}
                      label="Answer Key"
                      value={question.answer_key}
                      onChange={(e) => handleQuestionChange(index, 'answer_key', e.target.value)}
                      helperText="Provide the expected answer or key points"
                    />
                  </Grid>
                </Grid>
              </Paper>
            ))}
          </CardContent>
        </Card>

        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          <Button
            variant="outlined"
            onClick={() => navigate('/dashboard')}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create Test'}
          </Button>
        </Box>
      </form>
    </Container>
  );
};

export default CreateTest;