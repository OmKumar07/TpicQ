from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional

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

# Resume Upload schemas
class ResumeUploadBase(BaseModel):
    original_filename: str
    file_size: int

class ResumeUploadCreate(ResumeUploadBase):
    filename: str
    extracted_text: Optional[str] = None
    extracted_topics: Optional[str] = None

class ResumeUpload(ResumeUploadBase):
    id: int
    filename: str
    extracted_text: Optional[str] = None
    extracted_topics: Optional[str] = None
    processed: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True

# Resume Quiz schemas
class ResumeQuizCreate(BaseModel):
    resume_upload_id: int
    difficulty: Optional[str] = "medium"
    content_json: str
    total_questions: int = 30

class ResumeQuizContent(BaseModel):
    title: str
    resume_filename: str
    questions: List[Dict[str, Any]]
    total_questions: int
    extracted_topics: Optional[List[str]] = []

class ResumeQuiz(BaseModel):
    id: int
    resume_upload_id: int
    difficulty: str
    content: ResumeQuizContent
    score: Optional[int] = None
    total_questions: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Response schemas
class ResumeUploadResponse(BaseModel):
    id: int
    filename: str
    extracted_topics: Dict
    message: str

class ResumeQuizResponse(BaseModel):
    id: int
    resume_upload_id: int
    quiz_content: Dict
    message: str
