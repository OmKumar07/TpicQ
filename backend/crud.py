from sqlalchemy.orm import Session
from . import models
import json

# Topic CRUD operations
def create_topic(db: Session, name: str):
    """Create a new topic"""
    db_topic = models.Topic(name=name)
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

def get_topic(db: Session, topic_id: int):
    """Get a topic by ID"""
    return db.query(models.Topic).filter(models.Topic.id == topic_id).first()

def get_topic_by_name(db: Session, name: str):
    """Get a topic by name"""
    return db.query(models.Topic).filter(models.Topic.name == name).first()

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
