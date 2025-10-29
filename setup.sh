#!/bin/bash

# EvalMate Setup Script
echo "🚀 Setting up EvalMate - AI-powered Answer Sheet Evaluation System"
echo "=================================================================="

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ]; then
    echo "❌ Please run this script from the EvalMate project root directory"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python installation
echo "🐍 Checking Python installation..."
if command_exists python3; then
    echo "✅ Python3 found: $(python3 --version)"
else
    echo "❌ Python3 not found. Please install Python 3.9 or higher"
    exit 1
fi

# Setup Python virtual environment
echo "📦 Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "📥 Installing Python dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
echo "✅ Python dependencies installed"

# Check Node.js installation
echo "📱 Checking Node.js installation..."
if command_exists node; then
    echo "✅ Node.js found: $(node --version)"
    echo "✅ npm found: $(npm --version)"
    
    # Install frontend dependencies
    echo "📥 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend dependencies installed"
else
    echo "⚠️  Node.js not found. Frontend setup skipped."
    echo "   To install Node.js: https://nodejs.org/"
fi

# Setup database (if PostgreSQL is available)
echo "🗄️  Checking database setup..."
if command_exists psql; then
    echo "✅ PostgreSQL found"
    echo "📝 Please ensure you have:"
    echo "   1. Created a database named 'evalmate'"
    echo "   2. Updated the DATABASE_URL in backend/.env"
else
    echo "⚠️  PostgreSQL not found. You'll need to:"
    echo "   1. Install PostgreSQL"
    echo "   2. Create a database named 'evalmate'"
    echo "   3. Update the DATABASE_URL in backend/.env"
fi

# Setup environment file
echo "⚙️  Setting up environment configuration..."
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo "✅ Environment file created at backend/.env"
    echo "📝 Please update the following in backend/.env:"
    echo "   - DATABASE_URL (PostgreSQL connection string)"
    echo "   - SECRET_KEY (generate a secure random key)"
    echo "   - OPENAI_API_KEY (for AI evaluation features)"
else
    echo "✅ Environment file already exists"
fi

# Create upload directories
echo "📁 Creating upload directories..."
mkdir -p uploads/tests
mkdir -p uploads/answer_sheets
echo "✅ Upload directories created"

# Initialize database (if possible)
echo "🗄️  Database initialization..."
echo "   Run 'python database/init_db.py' after setting up your database"

echo ""
echo "🎉 Setup completed successfully!"
echo "=================================================================="
echo ""
echo "📋 Next steps:"
echo "1. Update backend/.env with your database credentials and API keys"
echo "2. Start PostgreSQL and create the 'evalmate' database"
echo "3. Run: python database/init_db.py (to populate with sample data)"
echo "4. Start the backend: cd backend && python main.py"
echo "5. Start the frontend: cd frontend && npm start (if Node.js is installed)"
echo ""
echo "🔐 Sample login credentials will be displayed after database initialization"
echo ""
echo "📚 For more information, see README.md"