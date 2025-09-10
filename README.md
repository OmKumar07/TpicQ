# TpicQ

A simple webapp for generating practice quizzes using the Gemini API. Users can add topics and request quizzes with different difficulty levels.

## Tech Stack

- **Backend**: FastAPI + Python
- **Database**: SQLite (with PostgreSQL support)
- **ORM**: SQLAlchemy + Alembic for migrations  
- **Frontend**: HTML + Bootstrap + Vanilla JavaScript
- **API Integration**: Gemini API for quiz generation

## Setup (Windows)

### 1. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Set Environment Variables
```bash
# Command Prompt
set GEMINI_API_KEY=your_key_here

# PowerShell
$env:GEMINI_API_KEY="your_key_here"

# Optional: PostgreSQL (defaults to SQLite)
$env:DATABASE_URL="postgresql://user:pass@localhost/dbname"
```

### 4. Run Database Migrations
```bash
cd backend
alembic upgrade head
```

### 5. Start Backend Server
```bash
uvicorn backend.main:app --reload
```

## API Endpoints

- `GET /health` - Health check
- `GET /topics` - List all topics
- `POST /topics` - Create a new topic
- `POST /topics/{topic_id}/generate-quiz` - Generate quiz for topic
- `GET /topics/{topic_id}/quizzes` - List saved quizzes for topic

## Testing

After starting the server, test endpoints:
```bash
# Health check
curl http://localhost:8000/health

# Create topic
curl -X POST http://localhost:8000/topics -H "Content-Type: application/json" -d "{\"name\":\"arrays\"}"

# Generate quiz
curl -X POST http://localhost:8000/topics/1/generate-quiz -H "Content-Type: application/json" -d "{\"difficulty\":\"easy\"}"
```

## Frontend

Open `frontend/index.html` in a browser to use the web interface.