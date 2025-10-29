# EvalMate - AI-Powered Educational Assessment Platform

<div align="center">

![EvalMate Logo](https://img.shields.io/badge/EvalMate-AI%20Assessment-blue?style=for-the-badge&logo=education)

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-AI%20Workflow-purple?style=flat-square)](https://github.com/langchain-ai/langgraph)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange?style=flat-square&logo=openai)](https://openai.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

**Revolutionizing Educational Assessment with Intelligent AI Evaluation**

[🚀 Live Demo](#quick-start) • [📖 Documentation](#documentation) • [✨ Features](#key-features) • [🛠️ Installation](#installation) • [🤝 Contributing](#contributing)

</div>

---

## 🎯 Overview

**EvalMate** is a cutting-edge AI-powered educational assessment platform that transforms traditional answer sheet evaluation into an intelligent, automated process. Built for modern educational institutions, it combines advanced AI technology with intuitive design to provide comprehensive, fair, and detailed evaluation of student assessments.

### 🌟 Why EvalMate?

- **🤖 AI-First Approach**: Leverages GPT-4 and advanced NLP for contextual understanding
- **⚡ Instant Evaluation**: Automated grading with detailed feedback in seconds
- **📊 Deep Analytics**: Question-wise analysis with improvement suggestions
- **🎓 Educational Focus**: Designed specifically for academic institutions
- **🔒 Secure & Reliable**: Built with enterprise-grade security and reliability

---

## 🚀 Key Features

### 🧠 Intelligent AI Evaluation
- **Semantic Understanding**: Goes beyond keyword matching to understand answer context
- **Multi-Agent Workflow**: Specialized AI agents for different evaluation aspects
- **Adaptive Scoring**: Adjusts evaluation criteria based on question complexity
- **Natural Language Feedback**: Human-like explanations and improvement suggestions

### 📝 Comprehensive Assessment Tools
- **Multi-Subject Support**: Science, Mathematics, Languages, Social Studies
- **Question-wise Analysis**: Detailed breakdown of performance per question
- **Grade-level Adaptation**: Tailored for 10th, 11th, and 12th standards
- **Answer Key Management**: Flexible reference answer systems with marking schemes

### 👥 Role-Based Access Control
- **Teacher Dashboard**: Test creation, student management, evaluation oversight
- **Student Portal**: Result viewing, progress tracking, personalized feedback
- **Administrative Controls**: User management and system configuration

### 📊 Advanced Analytics & Reporting
- **Performance Insights**: Detailed analytics on student and class performance
- **Progress Tracking**: Historical performance analysis and trend identification
- **Custom Reports**: Exportable reports for institutional requirements
- **Real-time Monitoring**: Live evaluation status and system health metrics

---

## 🏗️ Technical Architecture

### 🤖 AI-Powered Core
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OCR Engine   │ ──▶ │  LangGraph AI   │ ──▶ │  Evaluation     │
│   (Text Extract)│    │   Workflow      │    │   Engine        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Question       │    │  Semantic       │    │  Feedback       │
│  Detection      │    │  Analysis       │    │  Generation     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔧 Technology Stack

**Backend Technologies**
- **Framework**: FastAPI (High-performance async Python)
- **AI/ML**: LangGraph, OpenAI GPT-4, Custom NLP models
- **Database**: PostgreSQL (Production), SQLite (Development)
- **OCR**: Tesseract OCR, Google Cloud Vision API
- **Security**: JWT Authentication, OAuth 2.0, Role-based access

**Frontend Technologies**
- **Core**: Modern HTML5, CSS3, Vanilla JavaScript
- **Design**: Material Design principles, Responsive layout
- **API Integration**: RESTful APIs with error handling
- **State Management**: LocalStorage with data persistence

**Infrastructure & DevOps**
- **Deployment**: Docker containerization ready
- **API Documentation**: Automatic OpenAPI/Swagger documentation
- **Monitoring**: Built-in health checks and logging
- **Testing**: Comprehensive test suite for reliability

---

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 2GB free space
- **Network**: Internet connection for AI features
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

---

## 🛠️ Installation

### 1️⃣ Quick Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/yashvini-chirri/EvalMate-AI-Evaluation.git
cd EvalMate-AI-Evaluation

# Run the setup script
chmod +x setup.sh
./setup.sh
```

### 2️⃣ Manual Installation

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python database/init_db.py

# Start the application
python basic_server.py
```

### 3️⃣ Environment Configuration

Create a `.env` file (optional - system works without API keys in demo mode):

```env
# OpenAI Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///./evalmate.db

# Security Settings
SECRET_KEY=your_secure_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

---

## 🚀 Quick Start

### 🎮 Demo Mode (No Setup Required)

1. **Start the server**: `python basic_server.py`
2. **Open your browser**: http://localhost:8000/evalmate-old.html
3. **Login as Teacher**: 
   - Username: `teacher1` / Password: `password123`
4. **Create a test** and **evaluate answer sheets**
5. **Login as Student**: Use any student credentials to view results

### 📚 Sample Data Included

The system comes with pre-configured data:
- **120 Real Students**: Across 10th, 11th, 12th standards
- **Biology Question Paper**: 8 questions, 50 marks total
- **Sample Evaluations**: Demonstration of AI evaluation capabilities

---

## 📖 Usage Guide

### 👨‍🏫 For Teachers

1. **Login** to the teacher dashboard
2. **Create Tests**: Biology questions are auto-configured
3. **Select Students**: Choose from organized class sections
4. **Upload Answer Sheets**: PDF/Image format supported
5. **AI Evaluation**: Get detailed question-wise analysis
6. **Review Results**: Comprehensive reports with improvement suggestions

### 👨‍🎓 For Students

1. **Login** with student credentials
2. **View Results**: Access detailed evaluation reports
3. **Question Analysis**: See performance breakdown per question
4. **Study Recommendations**: Get personalized improvement suggestions
5. **Progress Tracking**: Monitor performance over time

---

## 📁 Project Structure

```
EvalMate/
├── 📱 Frontend
│   ├── evalmate-old.html          # Main application interface
│   ├── demo.html                  # Demonstration interface
│   └── webapp-simple.html         # Simplified interface
├── 🔧 Backend
│   ├── app/
│   │   ├── api/routes/            # RESTful API endpoints
│   │   ├── core/                  # Configuration & security
│   │   ├── db/                    # Database models & schemas
│   │   ├── langgraph/             # AI workflow orchestration
│   │   ├── schemas/               # Data validation schemas
│   │   └── services/              # Business logic services
│   ├── requirements.txt           # Python dependencies
│   └── requirements-advanced.txt  # Extended dependencies
├── 🗄️ Database
│   └── init_db.py                # Database initialization
├── 🚀 Deployment
│   ├── main.py                   # FastAPI application
│   ├── basic_server.py           # Simple HTTP server
│   └── setup.sh                  # Automated setup script
└── 📚 Documentation
    ├── README.md                 # This file
    ├── CONTRIBUTING.md           # Contribution guidelines
    └── ADVANCED_EVALUATION_README.md  # Technical documentation
```

---

## 🌟 Advanced Features

### 🤖 AI-Powered Evaluation Engine

- **Multi-Agent Architecture**: Specialized agents for different evaluation tasks
- **Contextual Understanding**: Semantic analysis beyond keyword matching
- **Adaptive Feedback**: Personalized improvement suggestions
- **Quality Assurance**: Multiple validation layers for accuracy

### 📊 Analytics Dashboard

- **Performance Metrics**: Comprehensive statistical analysis
- **Trend Analysis**: Historical performance tracking
- **Class Insights**: Aggregate performance analytics
- **Export Capabilities**: PDF/Excel report generation

### 🔐 Security & Privacy

- **Data Encryption**: End-to-end encryption for sensitive data
- **Access Control**: Role-based permissions and authentication
- **Privacy Compliance**: GDPR and educational data privacy standards
- **Audit Logging**: Comprehensive activity tracking

---

## 🧪 API Documentation

### 🔗 Main Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `POST` | `/api/auth/login` | User authentication | None |
| `GET` | `/api/students` | List students | Required |
| `POST` | `/api/tests` | Create new test | Teacher |
| `POST` | `/api/evaluate` | AI evaluation | Teacher |
| `GET` | `/api/results/{id}` | Get results | Student/Teacher |

### 📝 Interactive API Documentation

Access the interactive API documentation at: `http://localhost:8000/docs`

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test categories
python -m pytest tests/test_api.py
python -m pytest tests/test_evaluation.py
```

---

## 🤝 Contributing

We welcome contributions from the educational technology community!

### 🔄 Development Workflow

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### 📋 Contribution Guidelines

- Follow Python PEP 8 style guidelines
- Add tests for new functionality
- Update documentation for API changes
- Ensure all tests pass before submitting

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 API and advanced language models
- **LangGraph** for AI workflow orchestration
- **FastAPI** for the high-performance web framework
- **Educational Community** for feedback and testing

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/yashvini-chirri/EvalMate-AI-Evaluation/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yashvini-chirri/EvalMate-AI-Evaluation/discussions)
- **Documentation**: [Project Wiki](https://github.com/yashvini-chirri/EvalMate-AI-Evaluation/wiki)

---

<div align="center">

**⭐ Star this repository if EvalMate helps your educational institution!**

[![GitHub stars](https://img.shields.io/github/stars/yashvini-chirri/EvalMate-AI-Evaluation?style=social)](https://github.com/yashvini-chirri/EvalMate-AI-Evaluation/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/yashvini-chirri/EvalMate-AI-Evaluation?style=social)](https://github.com/yashvini-chirri/EvalMate-AI-Evaluation/network/members)

*Built with ❤️ for the future of education*

</div>
