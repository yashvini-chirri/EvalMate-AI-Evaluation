import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || '';

class APIService {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE,
      timeout: 30000,
    });

    // Add request interceptor for auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          localStorage.removeItem('userType');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth APIs
  async loginStudent(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await this.api.post('/api/auth/login/student', formData);
    return response.data;
  }

  async loginExaminer(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await this.api.post('/api/auth/login/examiner', formData);
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.api.get('/api/auth/me');
    return response.data;
  }

  // Student APIs
  async getStudentDashboard() {
    const response = await this.api.get('/api/students/dashboard');
    return response.data;
  }

  async getStudentPerformance() {
    const response = await this.api.get('/api/students/performance');
    return response.data;
  }

  async getStudentEvaluations(studentId) {
    const response = await this.api.get(`/api/evaluations/student/${studentId}`);
    return response.data;
  }

  // Examiner APIs
  async getExaminerDashboard() {
    const response = await this.api.get('/api/examiners/dashboard');
    return response.data;
  }

  async getExaminerAnalytics() {
    const response = await this.api.get('/api/examiners/analytics');
    return response.data;
  }

  // Test APIs
  async getTests(filters = {}) {
    const params = new URLSearchParams(filters);
    const response = await this.api.get(`/api/tests?${params}`);
    return response.data;
  }

  async getTest(testId) {
    const response = await this.api.get(`/api/tests/${testId}`);
    return response.data;
  }

  async createTest(testData) {
    const formData = new FormData();
    
    // Add text fields
    Object.keys(testData).forEach(key => {
      if (key !== 'questionPaper' && key !== 'answerKey' && key !== 'referenceBook') {
        formData.append(key, testData[key]);
      }
    });

    // Add files
    if (testData.questionPaper) {
      formData.append('question_paper', testData.questionPaper);
    }
    if (testData.answerKey) {
      formData.append('answer_key', testData.answerKey);
    }
    if (testData.referenceBook) {
      formData.append('reference_book', testData.referenceBook);
    }

    const response = await this.api.post('/api/tests/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async updateTest(testId, testData) {
    const response = await this.api.put(`/api/tests/${testId}`, testData);
    return response.data;
  }

  async deleteTest(testId) {
    const response = await this.api.delete(`/api/tests/${testId}`);
    return response.data;
  }

  async getTestStudents(testId) {
    const response = await this.api.get(`/api/tests/${testId}/students`);
    return response.data;
  }

  // Evaluation APIs
  async uploadAnswerSheet(testId, studentId, answerSheetFile) {
    const formData = new FormData();
    formData.append('test_id', testId);
    formData.append('student_id', studentId);
    formData.append('answer_sheet', answerSheetFile);

    const response = await this.api.post('/api/evaluations/upload-answer-sheet', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getEvaluation(evaluationId) {
    const response = await this.api.get(`/api/evaluations/${evaluationId}`);
    return response.data;
  }

  async getDetailedEvaluation(evaluationId) {
    const response = await this.api.get(`/api/evaluations/${evaluationId}/detailed`);
    return response.data;
  }

  async getTestEvaluations(testId) {
    const response = await this.api.get(`/api/evaluations/test/${testId}`);
    return response.data;
  }
}

const apiService = new APIService();
export default apiService;