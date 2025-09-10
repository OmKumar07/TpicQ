from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .db import engine, get_db
from . import models, crud, schemas
from .services.gemini_client import generate_quiz

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="TpicQ API", version="1.0.0")

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

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
    # Check if topic exists
    topic = crud.get_topic(db, topic_id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Validate difficulty
    if quiz_request.difficulty not in ["easy", "medium", "hard"]:
        raise HTTPException(status_code=400, detail="Difficulty must be: easy, medium, or hard")
    
    # Generate quiz using Gemini API (with fallback to mock)
    quiz_content = generate_quiz(topic.name, quiz_request.difficulty)
    
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
