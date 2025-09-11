from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with quizzes
    quizzes = relationship("Quiz", back_populates="topic")

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    difficulty = Column(String(20), nullable=False)  # easy, medium, hard
    content_json = Column(Text, nullable=False)  # JSON string with quiz data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with topic
    topic = relationship("Topic", back_populates="quizzes")
