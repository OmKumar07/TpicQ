# TpicQ - AI-Powered Quiz Generator 🎯

A modern, full-stack web application for generating practice quizzes using AI. Built with FastAPI, React, and the Gemini API, TpicQ provides an intelligent quiz platform with multi-topic support, API key rotation, and professional UI.

## 🌟 Live Demo

- **Frontend**: [https://topicq.netlify.app](https://topicq.netlify.app)
- **Backend API**: [https://tpicq.onrender.com](https://tpicq.onrender.com)
- **API Documentation**: [https://tpicq.onrender.com/docs](https://tpicq.onrender.com/docs)

## 🚀 Features

### Core Features
- ✅ **Multi-Topic Quiz Generation** - Select up to 3 topics per quiz
- ✅ **AI-Powered Questions** - Real-time generation using Gemini API
- ✅ **3 Difficulty Levels** - Easy, Medium, Hard with adaptive complexity
- ✅ **Interactive Quiz Interface** - Professional Bootstrap-styled UI
- ✅ **Real-time Scoring** - Instant feedback with performance analytics
- ✅ **Answer Randomization** - Prevents memorization, ensures fairness

### Advanced Features
- 🔄 **API Key Rotation System** - 4-key rotation for high availability (200+ quizzes/day)
- 🌐 **Production Deployment** - Live on Netlify (frontend) + Render (backend)
- 🔒 **Robust Error Handling** - Graceful fallbacks and user-friendly messages
- 📊 **Performance Analytics** - Detailed scoring with visual progress indicators
- 🎨 **Modern UI/UX** - Responsive design with Bootstrap 5 components
- 🔍 **Smart Topic Search** - Case-insensitive, partial matching support

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite with SQLAlchemy ORM
- **AI Integration**: Google Gemini API (1.5-flash model)
- **Deployment**: Render (with auto-scaling)
- **Features**: CORS middleware, environment configuration, error handling

### Frontend  
- **Framework**: React 18 with functional components
- **Styling**: Bootstrap 5 + custom CSS
- **HTTP Client**: Axios for API communication
- **Deployment**: Netlify (with continuous deployment)
- **Features**: Responsive design, real-time updates, error boundaries

### DevOps
- **Version Control**: Git with GitHub
- **CI/CD**: Automatic deployment on push
- **Environment**: Separate dev/prod configurations
- **Monitoring**: Comprehensive logging and debug endpoints

## 🔑 Gemini API Configuration

### Multiple API Keys for High Availability

The system supports up to 4 API keys for quota rotation:

```bash
# Environment Variables
GEMINI_API_KEY_1=your_first_api_key_here
GEMINI_API_KEY_2=your_second_api_key_here  
GEMINI_API_KEY_3=your_third_api_key_here
GEMINI_API_KEY_4=your_fourth_api_key_here

# Fallback (for backward compatibility)
GEMINI_API_KEY=your_primary_api_key_here
```

### Getting Gemini API Keys

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with different Google accounts (for multiple keys)
3. Click "Create API Key" for each account
4. Enable the Generative Language API for each project
5. Add keys to your environment configuration

**💡 Pro Tip**: Use different Google accounts to get separate quotas for each API key!

## ⚙️ Environment Configuration

### Backend Environment (.env)

```bash
# API Keys (Add up to 4 for rotation)
GEMINI_API_KEY_1=your_first_api_key_here
GEMINI_API_KEY_2=your_second_api_key_here
GEMINI_API_KEY_3=your_third_api_key_here
GEMINI_API_KEY_4=your_fourth_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///./quiz_app.db

# CORS Settings (for production)
FRONTEND_URL=https://topicq.netlify.app

# Debug Mode
DEBUG=false
```

### Frontend Environment (.env)

```bash
# Backend API URL
REACT_APP_BACKEND_URL=https://tpicq.onrender.com

# Development settings
REACT_APP_DEBUG=false
```

## 🚀 Quick Start

### Option 1: Use Live Demo (Recommended)
Simply visit [https://topicq.netlify.app](https://topicq.netlify.app) to start using the app immediately!

### Option 2: Local Development

#### Prerequisites
- Python 3.11+
- Node.js 16+
- npm or yarn

#### Backend Setup
```bash
# 1. Clone repository
git clone https://github.com/your-username/TpicQ.git
cd TpicQ

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux  
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your Gemini API keys

# 5. Start backend server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Frontend Setup
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Set up environment
echo "REACT_APP_BACKEND_URL=http://127.0.0.1:8000" > .env

# 4. Start development server
npm start
```

## 📚 Usage Guide

### Creating Your First Quiz

1. **Access the App**
   - Visit [https://topicq.netlify.app](https://topicq.netlify.app)
   - Or run locally at `http://localhost:3000`

2. **Add Topics**
   - Type topic names in the input field
   - Select up to 3 topics for your quiz
   - Topics are saved automatically

3. **Configure Quiz**
   - Choose difficulty: Easy (8 questions), Medium (10 questions), Hard (12 questions)
   - Click "Generate Quiz" to create questions

4. **Take the Quiz**
   - Answer multiple-choice questions
   - Get instant feedback on each answer
   - View your final score and performance summary

### Advanced Features

#### Multi-Topic Quizzes
- Combine related topics for comprehensive testing
- Example: "Python", "Django", "REST APIs" for web development
- Each topic contributes equally to question generation

#### Smart Error Handling
- Automatic API key rotation on quota limits
- Graceful fallbacks for network issues
- User-friendly error messages with retry options

#### Performance Analytics
- Detailed scoring breakdown by topic
- Visual progress indicators
- Historical performance tracking (local storage)

## 🏗️ Architecture

### System Overview
```
Frontend (React/Netlify) ←→ Backend (FastAPI/Render) ←→ Gemini API
                                    ↓
                              SQLite Database
```

### Key Components

#### Backend Services
- **`main.py`**: Core FastAPI application with CORS and error handling
- **`gemini_client.py`**: AI integration with API key rotation
- **`crud.py`**: Database operations with constraint handling
- **`models.py`**: SQLAlchemy data models
- **`database.py`**: Database configuration and session management

#### Frontend Components
- **`App.js`**: Main React component with state management
- **Topic Management**: Dynamic topic selection with validation
- **Quiz Interface**: Interactive question display with scoring
- **Error Handling**: User-friendly error messages and retry logic

### Database Schema
```sql
-- Topics table
CREATE TABLE topics (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quizzes table  
CREATE TABLE quizzes (
    id INTEGER PRIMARY KEY,
    topic_names TEXT NOT NULL,
    difficulty VARCHAR(10) NOT NULL,
    questions JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Development

### Project Structure
```
TpicQ/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── crud.py              # Database operations
│   ├── database.py          # DB configuration
│   ├── services/
│   │   └── gemini_client.py # AI integration
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.js           # Main React component
│   │   ├── App.css          # Custom styles
│   │   └── index.js         # React entry point
│   ├── public/
│   └── package.json         # Node dependencies
├── .env.example             # Environment template
└── README.md                # Documentation
```

### API Endpoints

#### Topic Management
- `GET /topics` - List all topics
- `POST /topics` - Create new topic
- `DELETE /topics/{topic_id}` - Delete topic

#### Quiz Operations
- `POST /quiz/generate` - Generate new quiz
- `GET /quiz/{quiz_id}` - Get quiz by ID
- `GET /quizzes` - List all quizzes

#### Debug & Health
- `GET /` - Health check
- `GET /debug/api-keys` - API key status
- `GET /debug/database` - Database statistics

### Local Development Tips

#### Backend Development
```bash
# Run with auto-reload
python -m uvicorn backend.main:app --reload --port 8000

# View API documentation
open http://127.0.0.1:8000/docs

# Check logs
tail -f logs/app.log
```

#### Frontend Development  
```bash
# Development server with hot reload
npm start

# Build for production
npm run build

# Run tests
npm test
```

#### Database Management
```bash
# View database content
sqlite3 quiz_app.db ".tables"
sqlite3 quiz_app.db "SELECT * FROM topics;"

# Reset database
rm quiz_app.db
# Restart backend to recreate
```

## 🐛 Troubleshooting

### Common Issues

#### "API Key Quota Exceeded"
**Solution**: Add more API keys to environment configuration
```bash
# Add additional keys
GEMINI_API_KEY_2=your_second_key
GEMINI_API_KEY_3=your_third_key
```

#### "CORS Error in Browser"
**Solution**: Check environment variables
```bash
# Backend .env
FRONTEND_URL=http://localhost:3000  # for development
FRONTEND_URL=https://topicq.netlify.app  # for production
```

#### "Database Locked" Error
**Solution**: Restart the backend server
```bash
# Kill existing processes
pkill -f uvicorn
# Restart server
python -m uvicorn backend.main:app --reload
```

#### "Topic Already Exists"
**Solution**: Topic names are case-insensitive and unique. Use different names or delete existing topics.

### Debug Tools

#### Backend Debug Endpoints
- `/debug/api-keys` - Check API key rotation status
- `/debug/database` - View database statistics
- `/debug/cors` - Test CORS configuration

#### Frontend Debug Mode
```bash
# Enable debug logging
REACT_APP_DEBUG=true npm start
# Check browser console for detailed logs
```

## 🚀 Deployment

### Production Deployment (Current Setup)

#### Backend (Render)
1. **Connect Repository**: Link GitHub repo to Render
2. **Configure Build**:
   ```bash
   # Build Command
   pip install -r requirements.txt
   
   # Start Command  
   python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```
3. **Environment Variables**: Add all `GEMINI_API_KEY_*` variables
4. **Auto-Deploy**: Enabled on main branch pushes

#### Frontend (Netlify)
1. **Connect Repository**: Link GitHub repo to Netlify
2. **Build Settings**:
   ```bash
   # Build Directory: frontend
   # Build Command: npm run build
   # Publish Directory: build
   ```
3. **Environment Variables**: Set `REACT_APP_BACKEND_URL`
4. **Auto-Deploy**: Enabled on main branch pushes

### Alternative Deployment Options

#### Docker Deployment
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ ./backend/
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Local Production Build
```bash
# Backend production
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend production
npm run build
npx serve -s build -l 3000
```

## 🤝 Contributing

### Development Workflow
1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Submit** pull request

### Code Standards
- **Python**: Follow PEP 8, use type hints
- **JavaScript**: Use ESLint, prefer functional components
- **Documentation**: Update README for new features
- **Testing**: Add tests for new functionality

### Bug Reports
When reporting bugs, include:
- Steps to reproduce
- Expected vs actual behavior
- Browser/OS information
- Screenshots (if applicable)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini API** for AI-powered quiz generation
- **FastAPI** for the robust backend framework
- **React** for the interactive frontend
- **Bootstrap** for responsive UI components
- **Render & Netlify** for reliable hosting

---

**🎯 Ready to test your knowledge?** Visit [https://topicq.netlify.app](https://topicq.netlify.app) and start your first quiz!
