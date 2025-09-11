from sqlalchemy.orm import Session
import models
import json

# Topic CRUD operations
def create_topic(db: Session, name: str):
    """Create a new topic with better error handling"""
    try:
        db_topic = models.Topic(name=name)
        db.add(db_topic)
        db.commit()
        db.refresh(db_topic)
        return db_topic
    except Exception as e:
        db.rollback()  # Rollback the transaction on error
        print(f"❌ Database error creating topic '{name}': {e}")
        print(f"🔍 Error type: {type(e)}")
        
        # Check if it's a constraint violation (unique name)
        if "UNIQUE constraint failed" in str(e) or "unique" in str(e).lower():
            # Topic already exists, try to retrieve it
            existing_topic = db.query(models.Topic).filter(models.Topic.name == name).first()
            if existing_topic:
                print(f"🔄 Topic '{name}' already exists, returning existing one with ID: {existing_topic.id}")
                return existing_topic
        
        # Re-raise the original error if we can't handle it
        raise e

def get_topic(db: Session, topic_id: int):
    """Get a topic by ID"""
    return db.query(models.Topic).filter(models.Topic.id == topic_id).first()

def get_topic_by_name(db: Session, name: str):
    """Get a topic by name (case-insensitive)"""
    return db.query(models.Topic).filter(models.Topic.name.ilike(name)).first()

def get_topics(db: Session, skip: int = 0, limit: int = 100):
    """Get all topics"""
    return db.query(models.Topic).offset(skip).limit(limit).all()

# Quiz CRUD operations
def create_quiz(db: Session, topic_id: int, difficulty: str, content_json: dict):
    """Create a new quiz"""
    content_str = json.dumps(content_json)
    db_quiz = models.Quiz(
        topic_id=topic_id,
        difficulty=difficulty,
        content_json=content_str
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz

def get_quiz(db: Session, quiz_id: int):
    """Get a quiz by ID"""
    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
    if quiz:
        # Parse JSON content
        quiz.content = json.loads(quiz.content_json)
    return quiz

def get_quizzes_by_topic(db: Session, topic_id: int):
    """Get all quizzes for a topic"""
    quizzes = db.query(models.Quiz).filter(models.Quiz.topic_id == topic_id).all()
    for quiz in quizzes:
        quiz.content = json.loads(quiz.content_json)
    return quizzes
