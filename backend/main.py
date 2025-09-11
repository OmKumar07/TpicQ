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

# Initialize database
def init_database():
    """Initialize database tables and ensure they exist"""
    try:
        print("🔧 Initializing database...")
        
        # Create all tables
        models.Base.metadata.create_all(bind=engine)
        
        # Verify tables were created by trying to connect and check
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"📊 Database tables created: {tables}")
        
        if "topics" not in tables or "quizzes" not in tables:
            print("⚠️  Warning: Required tables not found, attempting to recreate...")
            models.Base.metadata.drop_all(bind=engine)
            models.Base.metadata.create_all(bind=engine)
            
            # Check again
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"📊 Tables after recreation: {tables}")
        
        print("✅ Database initialization completed!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise e

# Initialize database
init_database()

app = FastAPI(title="TpicQ API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Startup event to ensure database is ready"""
    print("🚀 Starting TpicQ API...")
    print(f"🌍 Environment: {'Production' if os.getenv('RENDER') else 'Development'}")
    print(f"🔗 Frontend URL: {os.getenv('FRONTEND_URL', 'http://localhost:3000')}")
    print(f"🔗 Backend URL: {os.getenv('BACKEND_URL', 'http://localhost:8000')}")
    
    # Re-initialize database on startup (important for in-memory databases)
    init_database()

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

@app.get("/debug/database")
def debug_database():
    """Debug endpoint to check database status"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # Try to count topics
        db = next(get_db())
        try:
            topic_count = db.query(models.Topic).count()
            quiz_count = db.query(models.Quiz).count()
        except Exception as e:
            topic_count = f"Error: {e}"
            quiz_count = f"Error: {e}"
        finally:
            db.close()
        
        return {
            "database_url": os.getenv("DATABASE_URL", "Not set"),
            "environment": "Production" if os.getenv("RENDER") else "Development",
            "tables": tables,
            "topic_count": topic_count,
            "quiz_count": quiz_count,
            "engine_info": str(engine.url)
        }
    except Exception as e:
        return {"error": str(e)}

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
    try:
        print(f"📝 Creating topic: {topic.name}")
        
        # Check if topic already exists
        db_topic = crud.get_topic_by_name(db, name=topic.name)
        if db_topic:
            print(f"⚠️  Topic '{topic.name}' already exists")
            raise HTTPException(status_code=400, detail="Topic already exists")
        
        # Create new topic
        new_topic = crud.create_topic(db=db, name=topic.name)
        print(f"✅ Topic '{topic.name}' created successfully with ID: {new_topic.id}")
        return new_topic
        
    except HTTPException:
        # Re-raise HTTP exceptions (like topic already exists)
        raise
    except Exception as e:
        print(f"❌ Failed to create topic '{topic.name}': {e}")
        
        # Check if it's a database table issue
        if "no such table" in str(e):
            print("🔧 Database table issue detected, attempting to reinitialize...")
            try:
                init_database()
                # Retry the operation
                db_topic = crud.get_topic_by_name(db, name=topic.name)
                if db_topic:
                    raise HTTPException(status_code=400, detail="Topic already exists")
                return crud.create_topic(db=db, name=topic.name)
            except Exception as retry_error:
                print(f"❌ Retry failed: {retry_error}")
                raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(retry_error)}")
        
        raise HTTPException(status_code=500, detail=f"Failed to create topic: {str(e)}")

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
