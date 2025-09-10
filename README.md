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
- ✅ Simple web interface (HTML + React versions)
- ✅ Interactive quiz taking with scoring
- ✅ Mock fallback when Gemini API key not provided

## 🔑 **Setting Up Gemini API Key**

### **Option 1: Environment Variable (Recommended)**
```bash
# PowerShell (Windows)
$env:GEMINI_API_KEY="your_actual_gemini_api_key_here"

# Command Prompt (Windows)  
set GEMINI_API_KEY=your_actual_gemini_api_key_here

# Then restart the server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### **Option 2: Create a .env file**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your key:
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### **Getting a Gemini API Key**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and use it in step 1 or 2 above

**✅ Will it work after that?** YES! The app will automatically switch from mock data to real AI-generated quizzes.

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

**Option A: Basic HTML Interface**
http://127.0.0.1:8000/static/index.html

**Option B: React Interface (Recommended)**
```bash
# Install Node.js dependencies
cd frontend-react
npm install

# Start React development server
npm start
# Opens at http://localhost:3000

# OR build for production and serve via FastAPI
npm run build
# Then visit http://127.0.0.1:8000/react
```

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
│   └── index.html           # Basic HTML interface
├── frontend-react/          # React interface (recommended)
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   └── index.js        # React entry point
│   ├── package.json        # Node.js dependencies
│   └── README.md           # React-specific docs
├── data/
│   └── dev.db              # SQLite database (auto-created)
├── .env.example            # Environment variables template
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