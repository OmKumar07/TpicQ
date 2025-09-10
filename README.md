# TpicQ

A simple webapp for generating practice quizzes using the Gemini API. Users can add topics and request quizzes with different difficulty levels.

## Tech Stack

- **Backend**: FastAPI + Python
- **Database**: SQLite (with PostgreSQL support)
- **ORM**: SQLAlchemy + Alembic for migrations  
- **Frontend**: HTML + Bootstrap + Vanilla JavaScript
- **API Integration**: Gemini API for quiz generation

## Features

- ✅ Add and manage topics
- ✅ Generate quizzes with AI (Gemini API) 
- ✅ Three difficulty levels: Easy, Medium, Hard
- ✅ Save and retrieve generated quizzes
- ✅ Simple web interface
- ✅ Mock fallback when Gemini API key not provided

## Quick Start

### 1. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Set Environment Variables (Optional)
```bash
# Command Prompt
set GEMINI_API_KEY=your_gemini_api_key_here

# PowerShell
$env:GEMINI_API_KEY="your_gemini_api_key_here"

# Optional: PostgreSQL (defaults to SQLite)
$env:DATABASE_URL="postgresql://user:pass@localhost/dbname"
```

### 4. Start the Application
```bash
# Navigate to project root
cd c:\path\to\TpicQ

# Start the server
uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Or use Python directly
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### 5. Open the Web Interface
Open your browser and go to: http://127.0.0.1:8000/static/index.html

## API Endpoints

### Health Check
- `GET /health` - Returns server status

### Topics
- `GET /topics` - List all topics
- `POST /topics` - Create a new topic
  ```json
  {"name": "Arrays"}
  ```

### Quizzes  
- `POST /topics/{topic_id}/generate-quiz` - Generate quiz for topic
  ```json
  {"difficulty": "easy"}
  ```
- `GET /topics/{topic_id}/quizzes` - List saved quizzes for topic

### API Documentation
Visit http://127.0.0.1:8000/docs for interactive API documentation.

## Testing API with curl

```bash
# Health check
curl http://127.0.0.1:8000/health

# Create topic
curl -X POST http://127.0.0.1:8000/topics -H "Content-Type: application/json" -d "{\"name\":\"arrays\"}"

# Generate quiz (replace 1 with actual topic ID)
curl -X POST http://127.0.0.1:8000/topics/1/generate-quiz -H "Content-Type: application/json" -d "{\"difficulty\":\"easy\"}"

# List quizzes for topic
curl http://127.0.0.1:8000/topics/1/quizzes
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Your Gemini API key for quiz generation | None | No (uses mock data) |
| `GEMINI_API_URL` | Gemini API endpoint | Google's default | No |
| `DATABASE_URL` | Database connection string | `sqlite:///./data/dev.db` | No |

## Project Structure

```
TpicQ/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── db.py                # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── services/
│   │   └── gemini_client.py # Gemini API integration
│   └── requirements.txt     # Python dependencies
├── frontend/
│   └── index.html           # Web interface
├── data/
│   └── dev.db              # SQLite database (auto-created)
└── README.md
```

## Development

### Running in Development Mode
```bash
# With auto-reload
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Database
- The SQLite database is created automatically in `data/dev.db`
- Tables are created automatically when the server starts
- To reset the database, simply delete the `data/dev.db` file

### Adding Gemini API Integration

1. Get a Gemini API key from Google AI Studio
2. Set the environment variable:
   ```bash
   $env:GEMINI_API_KEY="your_actual_api_key"
   ```
3. Restart the server
4. Generate quizzes will now use the Gemini API instead of mock data

## Troubleshooting

### Port Already in Use
If you get a port binding error:
```bash
# Kill existing Python processes
taskkill /F /IM python.exe

# Or use a different port
uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

### CORS Issues
If you access the frontend from a different domain/port, update the CORS settings in `backend/main.py`.

### Database Issues
Delete `data/dev.db` and restart the server to recreate the database with fresh tables.

## Contributing

1. Create feature branches: `git checkout -b feature/your-feature`
2. Make small, focused commits
3. Follow the commit message format: `add feature name` (lowercase, no emoji)
4. Push branches and create pull requests

## License

MIT License - see LICENSE file for details.