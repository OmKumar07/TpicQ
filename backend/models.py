from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
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

class ResumeUpload(Base):
    __tablename__ = "resume_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    extracted_text = Column(Text, nullable=True)  # extracted resume text
    extracted_topics = Column(Text, nullable=True)  # JSON string of extracted topics/skills
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with resume quizzes
    resume_quizzes = relationship("ResumeQuiz", back_populates="resume_upload")

class ResumeQuiz(Base):
    __tablename__ = "resume_quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_upload_id = Column(Integer, ForeignKey("resume_uploads.id"), nullable=False)
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    content_json = Column(Text, nullable=False)  # JSON string with 30 quiz questions
    score = Column(Integer, nullable=True)  # user's score if quiz was taken
    total_questions = Column(Integer, default=30)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with resume upload
    resume_upload = relationship("ResumeUpload", back_populates="resume_quizzes")
