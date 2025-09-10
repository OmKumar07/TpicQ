# TpicQ React Frontend

A modern React-based frontend for the TpicQ quiz generator app.

## Features

- 🎯 Interactive quiz generation
- 📚 Topic management
- 🏆 Real-time scoring
- 📱 Responsive Bootstrap design
- ⚡ Fast API integration with Axios

## Quick Start

### Prerequisites
- Node.js 16+ installed
- Backend server running on http://127.0.0.1:8000

### Development Setup

```bash
# Navigate to frontend directory
cd frontend-react

# Install dependencies
npm install

# Start development server
npm start
```

The app will open at http://localhost:3000

### Production Build

```bash
# Build for production
npm run build

# The build files will be in the 'build' directory
# The FastAPI server will serve these at http://127.0.0.1:8000/react
```

## Usage

1. **Add Topics**: Enter topic names like "React Hooks", "Data Structures"
2. **Select Topic & Difficulty**: Choose from Easy, Medium, or Hard
3. **Generate Quiz**: Click to create AI-powered questions
4. **Take Quiz**: Click on answer options to select them
5. **Submit & Review**: See your score and correct answers

## API Integration

The frontend communicates with the FastAPI backend:

- `GET /topics` - Load available topics
- `POST /topics` - Create new topics  
- `POST /topics/{id}/generate-quiz` - Generate quiz content

## Styling

Uses Bootstrap 5 for responsive design with custom CSS for:
- Quiz question styling
- Interactive answer selection
- Loading states
- Score visualization

## Dependencies

- **React 18** - UI framework
- **Bootstrap 5** - CSS framework
- **Axios** - HTTP client
- **React Scripts** - Build tooling
