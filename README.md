# TpicQ - AI-Powered Quiz Platform 🎯

A comprehensive web application offering two distinct quiz experiences: personalized resume-based assessments and customizable topic quizzes, all powered by advanced AI technology.

## 🌟 Live Demo

- **App**: [https://topicq.netlify.app](https://topicq.netlify.app)
- **API**: [https://tpicq.onrender.com/docs](https://tpicq.onrender.com/docs)

## ✨ Features

### 📄 Resume Quiz

- **Resume Upload** - Support for PDF and DOCX file formats
- **Skill Analysis** - AI extracts skills and experience from your resume
- **Personalized Questions** - 30 targeted questions based on your background
- **Interview Preparation** - Realistic questions matching your experience level
- **File Processing** - Advanced text extraction and content analysis

### 🎨 Custom Quiz

- **Multi-Topic Selection** - Choose up to 3 topics per quiz
- **Flexible Difficulty** - Easy (8 questions), Medium (10), Hard (12)
- **Any Subject Area** - Create quizzes on virtually any topic
- **Smart Topic Search** - Case-insensitive with partial matching

### 🚀 Core Features

- **AI-Generated Questions** - Powered by Google Gemini API
- **Real-time Scoring** - Instant performance feedback
- **Answer Review** - Detailed explanations with correct/incorrect highlights
- **Performance Analytics** - Visual scoring with percentage breakdown
- **Answer Randomization** - Prevents memorization patterns
- **Responsive Design** - Modern Bootstrap UI optimized for all devices

## 🛠️ Tech Stack

### Backend

- **FastAPI** - Modern Python web framework with async support
- **SQLAlchemy ORM** - Database management with SQLite
- **PyPDF2** - PDF text extraction for resume processing
- **python-docx** - Word document processing
- **Google Gemini API** - Advanced AI question generation
- **File Upload Handling** - Secure multipart form processing
- **Deployed on Render** - Auto-scaling backend hosting

### Frontend

- **React 18** - Modern JavaScript framework with hooks
- **Bootstrap 5** - Responsive UI components and utilities
- **Bootstrap Icons** - Comprehensive icon library
- **Axios** - HTTP client for API communication
- **File Upload Components** - Drag-and-drop file handling
- **State Management** - React hooks for complex UI states
- **Deployed on Netlify** - Fast frontend hosting with CDN

### Database Schema

- **Resume Uploads** - File metadata and content storage
- **Resume Quizzes** - Generated questions and user responses
- **Custom Quizzes** - Topic-based quiz data and results

### Advanced Features

- **API Key Rotation** - Multiple Gemini keys for high availability
- **CORS Handling** - Secure cross-origin requests
- **Error Handling** - Graceful fallbacks and user feedback
- **File Validation** - Type checking and size limits
- **Environment Config** - Separate dev/production settings

## 🚀 Quick Start

### Using the Live App

Simply visit [https://topicq.netlify.app](https://topicq.netlify.app) to start your quiz experience immediately!

### How to Use

#### 📄 Resume Quiz

1. **Upload Resume** - Drag and drop your PDF or DOCX resume
2. **AI Analysis** - Wait for skill extraction and question generation
3. **Take Assessment** - Answer 30 personalized questions
4. **Review Results** - Get detailed score and performance feedback

#### 🎨 Custom Quiz

1. **Add Topics** - Type topic names (e.g., "Python", "Machine Learning")
2. **Select Difficulty** - Choose Easy, Medium, or Hard
3. **Generate Quiz** - Click to create AI-powered questions
4. **Take Quiz** - Answer questions and get instant scoring

---

**Ready to test your knowledge?** 🎯 Visit the app and choose your quiz experience!
