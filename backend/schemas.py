from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any

# Topic schemas
class TopicBase(BaseModel):
    name: str

class TopicCreate(TopicBase):
    pass

class Topic(TopicBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Quiz schemas
class QuizGenerate(BaseModel):
    difficulty: str  # easy, medium, hard

class QuizContent(BaseModel):
    title: str
    difficulty: str
    questions: List[Dict[str, Any]]

class Quiz(BaseModel):
    id: int
    topic_id: int
    difficulty: str
    content: QuizContent
    created_at: datetime
    
    class Config:
        from_attributes = True
