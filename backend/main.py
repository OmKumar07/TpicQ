from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import sys
import os

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import engine, get_db
import models, crud, schemas
from services.gemini_client import generate_quiz

# Load environment variables from .env file
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="TpicQ API", version="1.0.0")

# Manual CORS middleware
@app.middleware("http")
async def cors_handler(request: Request, call_next):
    response = await call_next(request)
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    response.headers["Access-Control-Allow-Origin"] = frontend_url
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response

# Add CORS middleware for frontend
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        frontend_url,
        backend_url,
        "https://topicq.netlify.app",
        "https://tpicq.onrender.com",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount React build files (when available)
try:
    app.mount("/react", StaticFiles(directory="frontend-react/build", html=True), name="react")
except Exception:
    pass  # React build not available yet

@app.get("/")
def root():
    return {"message": "TpicQ API is running", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    """Handle CORS preflight requests"""
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": frontend_url,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/topics", response_model=schemas.Topic)
def create_topic(topic: schemas.TopicCreate, db: Session = Depends(get_db)):
    """Create a new topic"""
    # Check if topic already exists
    db_topic = crud.get_topic_by_name(db, name=topic.name)
    if db_topic:
        raise HTTPException(status_code=400, detail="Topic already exists")
    return crud.create_topic(db=db, name=topic.name)

@app.get("/topics", response_model=list[schemas.Topic])
def get_topics(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all topics"""
    topics = crud.get_topics(db, skip=skip, limit=limit)
    return topics

@app.post("/topics/{topic_id}/generate-quiz")
def generate_quiz_endpoint(topic_id: int, quiz_request: schemas.QuizGenerate, db: Session = Depends(get_db)):
    """Generate a quiz for a topic using Gemini API"""
    print(f"🎯 Quiz generation requested for topic {topic_id}, difficulty: {quiz_request.difficulty}")
    
    # Check if topic exists
    topic = crud.get_topic(db, topic_id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    print(f"📚 Topic found: {topic.name}")
    
    # Validate difficulty
    if quiz_request.difficulty not in ["easy", "medium", "hard"]:
        raise HTTPException(status_code=400, detail="Difficulty must be: easy, medium, or hard")
    
    # Generate quiz using Gemini API
    print(f"🤖 Calling generate_quiz function...")
    try:
        quiz_content = generate_quiz(topic.name, quiz_request.difficulty)
        print(f"✅ Quiz generation completed!")
    except Exception as e:
        print(f"❌ Quiz generation failed: {e}")
        # Return a proper error response instead of crashing
        raise HTTPException(
            status_code=503, 
            detail=f"Quiz generation service temporarily unavailable: {str(e)}"
        )
    
    # Save quiz to database
    saved_quiz = crud.create_quiz(
        db=db,
        topic_id=topic_id,
        difficulty=quiz_request.difficulty,
        content_json=quiz_content
    )
    
    return {"message": "Quiz generated successfully", "quiz_id": saved_quiz.id, "content": quiz_content}

@app.get("/topics/{topic_id}/quizzes")
def get_topic_quizzes(topic_id: int, db: Session = Depends(get_db)):
    """Get all saved quizzes for a topic"""
    # Check if topic exists
    topic = crud.get_topic(db, topic_id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get all quizzes for this topic
    quizzes = crud.get_quizzes_by_topic(db, topic_id=topic_id)
    
    # Format response
    quiz_list = []
    for quiz in quizzes:
        quiz_list.append({
            "id": quiz.id,
            "difficulty": quiz.difficulty,
            "created_at": quiz.created_at,
            "content": quiz.content
        })
    
    return {
        "topic": {"id": topic.id, "name": topic.name},
        "quizzes": quiz_list
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
