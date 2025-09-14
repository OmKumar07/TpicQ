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
from routes.resume import router as resume_router

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
    print(f"🔗 Frontend URL: {os.getenv('FRONTEND_URL', 'Not set')}")
    print(f"🔗 Backend URL: {os.getenv('BACKEND_URL', 'Not set')}")
    print(f"🔒 CORS: Will allow https://topicq.netlify.app and localhost:3000")
    
    # Re-initialize database on startup (important for in-memory databases)
    init_database()

# Manual CORS middleware - Always allow production URLs
@app.middleware("http")
async def cors_handler(request: Request, call_next):
    response = await call_next(request)
    
    # Get the origin from the request
    origin = request.headers.get("origin")
    
    # Define allowed origins (including all possible combinations)
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "https://topicq.netlify.app",
        "https://tpicq.onrender.com",
        os.getenv("FRONTEND_URL", ""),
        os.getenv("BACKEND_URL", "")
    ]
    
    # Filter out empty strings
    allowed_origins = [url for url in allowed_origins if url]
    
    # Check if the origin is allowed
    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
    else:
        # Default to Netlify production URL for production environment
        if os.getenv("RENDER"):
            response.headers["Access-Control-Allow-Origin"] = "https://topicq.netlify.app"
        else:
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "false"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response

# Add CORS middleware for frontend - Explicit production URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://topicq.netlify.app",  # Production frontend
        "https://tpicq.onrender.com",  # Production backend  
        "*"  # Temporary wildcard for debugging
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

# Include resume routes
app.include_router(resume_router, prefix="/api/resume", tags=["resume"])

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
            
            # Get all topics
            all_topics = db.query(models.Topic).all()
            topic_list = [{"id": t.id, "name": t.name, "created_at": str(t.created_at)} for t in all_topics]
            
        except Exception as e:
            topic_count = f"Error: {e}"
            quiz_count = f"Error: {e}"
            topic_list = []
        finally:
            db.close()
        
        return {
            "database_url": os.getenv("DATABASE_URL", "Not set"),
            "environment": "Production" if os.getenv("RENDER") else "Development",
            "tables": tables,
            "topic_count": topic_count,
            "quiz_count": quiz_count,
            "all_topics": topic_list,
            "engine_info": str(engine.url)
        }
    except Exception as e:
        return {"error": str(e)}

@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    """Handle CORS preflight requests"""
    
    # Get the origin from the request
    origin = request.headers.get("origin")
    
    # Define allowed origins
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "https://topicq.netlify.app",
        "https://tpicq.onrender.com"
    ]
    
    # Default to production frontend for production environment
    allowed_origin = "https://topicq.netlify.app" if os.getenv("RENDER") else "http://localhost:3000"
    
    # Use specific origin if it's in allowed list
    if origin in allowed_origins:
        allowed_origin = origin
    
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": allowed_origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "false",
            "Access-Control-Max-Age": "3600"
        }
    )

@app.post("/topics", response_model=schemas.Topic)
def create_topic(topic: schemas.TopicCreate, db: Session = Depends(get_db)):
    """Create a new topic"""
    try:
        print(f"📝 Creating topic: '{topic.name}' (length: {len(topic.name)})")
        
        # Validate topic name
        if not topic.name or not topic.name.strip():
            raise HTTPException(status_code=400, detail="Topic name cannot be empty")
        
        topic_name = topic.name.strip()
        print(f"🔍 Sanitized topic name: '{topic_name}'")
        
        # Check if topic already exists (with better error handling)
        try:
            db_topic = crud.get_topic_by_name(db, name=topic_name)
            if db_topic:
                print(f"⚠️  Topic '{topic_name}' already exists with ID: {db_topic.id}")
                raise HTTPException(status_code=400, detail="Topic already exists")
        except HTTPException:
            raise
        except Exception as search_error:
            print(f"⚠️  Error searching for existing topic: {search_error}")
            # Continue with creation attempt
        
        # Create new topic
        try:
            new_topic = crud.create_topic(db=db, name=topic_name)
            print(f"✅ Topic '{topic_name}' created successfully with ID: {new_topic.id}")
            return new_topic
        except Exception as create_error:
            print(f"❌ Error creating topic in database: {create_error}")
            print(f"🔍 Error type: {type(create_error)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Database error creating topic: {str(create_error)}"
            )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like topic already exists)
        raise
    except Exception as e:
        print(f"❌ Unexpected error creating topic '{topic.name}': {e}")
        print(f"🔍 Error type: {type(e)}")
        
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
    try:
        topics = crud.get_topics(db, skip=skip, limit=limit)
        print(f"📋 Retrieved {len(topics)} topics: {[t.name for t in topics]}")
        return topics
    except Exception as e:
        print(f"❌ Failed to get topics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve topics: {str(e)}")

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
        success_message = "Quiz generated successfully"
            
    except Exception as e:
        print(f"❌ Quiz generation failed: {e}")
        
        # Provide user-friendly error messages
        error_message = "Quiz generation service temporarily unavailable"
        
        if "403" in str(e) or "permission" in str(e).lower() or "disabled" in str(e).lower():
            error_message = "AI service access denied. Please check API key permissions and try again later."
        elif "503" in str(e) or "overloaded" in str(e).lower():
            error_message = "AI service is overloaded. Please try again in a few minutes."
        elif "429" in str(e) or "quota" in str(e).lower():
            error_message = "API quota limit exceeded. Please try again tomorrow or contact support."
        elif "timeout" in str(e).lower():
            error_message = "AI service timeout. Please try again."
        elif "network" in str(e).lower():
            error_message = "Network connectivity issue. Please check your connection."
        elif "no gemini api keys" in str(e).lower():
            error_message = "AI service configuration error. Please contact support."
        
        raise HTTPException(
            status_code=503, 
            detail=error_message
        )
    
    # Save quiz to database
    try:
        saved_quiz = crud.create_quiz(
            db=db,
            topic_id=topic_id,
            difficulty=quiz_request.difficulty,
            content_json=quiz_content
        )
        
        return {
            "message": success_message, 
            "quiz_id": saved_quiz.id, 
            "content": quiz_content,
            "status": "success"
        }
    except Exception as e:
        print(f"❌ Failed to save quiz to database: {e}")
        # Still return the quiz content even if saving fails
        return {
            "message": f"{success_message} (note: quiz not saved to database)", 
            "quiz_id": None, 
            "content": quiz_content,
            "status": "partial_success"
        }

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
