import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemText,
  Chip,
  Box,
  CircularProgress
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';

const StudentDashboard = () => {
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
        api.get('/students/tests'),
        api.get('/students/evaluations')
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
      <Typography variant="h4" component="h1" gutterBottom>
        Welcome, {user?.name}!
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                Available Tests
              </Typography>
              {tests.length === 0 ? (
                <Typography color="text.secondary">
                  No tests available at the moment.
                </Typography>
              ) : (
                <List>
                  {tests.map((test) => (
                    <ListItem key={test.id} divider>
                      <ListItemText
                        primary={test.title}
                        secondary={`Subject: ${test.subject} | Due: ${new Date(test.due_date).toLocaleDateString()}`}
                      />
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => navigate(`/test/${test.id}`)}
                      >
                        View Details
                      </Button>
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                Recent Evaluations
              </Typography>
              {evaluations.length === 0 ? (
                <Typography color="text.secondary">
                  No evaluations yet.
                </Typography>
              ) : (
                <List>
                  {evaluations.slice(0, 5).map((evaluation) => (
                    <ListItem key={evaluation.id} divider>
                      <ListItemText
                        primary={evaluation.test_title}
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2">
                              Score: {evaluation.score}
                            </Typography>
                            <Chip
                              label={evaluation.status}
                              size="small"
                              color={evaluation.status === 'completed' ? 'success' : 'warning'}
                            />
                          </Box>
                        }
                      />
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => navigate(`/evaluation/${evaluation.id}`)}
                      >
                        View Results
                      </Button>
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default StudentDashboard;