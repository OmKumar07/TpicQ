from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime

from db import get_db
from models import ResumeUpload, ResumeQuiz
from schemas import ResumeUploadResponse, ResumeQuizResponse, ResumeQuizContent
from services.resume_processor import resume_processor

router = APIRouter()

@router.post("/upload-resume", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a resume file"""
    try:
        print(f"📄 Received file upload: {file.filename}")
        
        # Validate file
        file_content = await file.read()
        print(f"📊 File size: {len(file_content)} bytes")
        
        resume_processor.validate_file(file.filename, len(file_content))
        print(f"✅ File validation passed")
        
        # Extract text from resume
        extracted_text = await resume_processor.extract_text_from_file(file_content, file.filename)
        print(f"📝 Text extraction completed: {len(extracted_text)} characters")
        
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the resume. Please ensure the file is not corrupted.")
        
        # Extract topics and skills
        extracted_topics = resume_processor.extract_topics_and_skills(extracted_text)
        print(f"🔍 Topics extracted: {list(extracted_topics.keys())}")
        
        # Save to database
        resume_upload = ResumeUpload(
            filename=file.filename,
            original_filename=file.filename,
            file_size=len(file_content),
            extracted_text=extracted_text,
            extracted_topics=json.dumps(extracted_topics),
            processed=True,
            created_at=datetime.utcnow()
        )
        
        db.add(resume_upload)
        db.commit()
        db.refresh(resume_upload)
        
        return ResumeUploadResponse(
            id=resume_upload.id,
            filename=resume_upload.filename,
            extracted_topics=extracted_topics,
            message="Resume uploaded and processed successfully"
        )
        
    except ValueError as e:
        print(f"❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Unexpected error in resume upload: {str(e)}")
        print(f"🔍 Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")

@router.post("/generate-resume-quiz/{upload_id}", response_model=ResumeQuizResponse)
async def generate_resume_quiz(
    upload_id: int,
    db: Session = Depends(get_db)
):
    """Generate a 30-question quiz based on uploaded resume"""
    try:
        print(f"🎯 Generating quiz for upload ID: {upload_id}")
        
        # Get the uploaded resume
        resume_upload = db.query(ResumeUpload).filter(ResumeUpload.id == upload_id).first()
        
        if not resume_upload:
            print(f"❌ Resume upload not found for ID: {upload_id}")
            raise HTTPException(status_code=404, detail="Resume upload not found")
        
        print(f"✅ Found resume: {resume_upload.filename}")
        
        # Check if quiz already exists
        existing_quiz = db.query(ResumeQuiz).filter(ResumeQuiz.resume_upload_id == upload_id).first()
        if existing_quiz:
            print(f"♻️ Quiz already exists for upload ID: {upload_id}")
            return ResumeQuizResponse(
                id=existing_quiz.id,
                resume_upload_id=existing_quiz.resume_upload_id,
                quiz_content=json.loads(existing_quiz.content_json),
                message="Quiz already exists for this resume"
            )
        
        # Parse extracted topics
        extracted_topics = json.loads(resume_upload.extracted_topics)
        print(f"📊 Extracted topics: {extracted_topics}")
        
        # Generate quiz
        print(f"🤖 Starting quiz generation...")
        quiz_data = resume_processor.generate_resume_quiz(
            resume_upload.extracted_text,
            extracted_topics,
            resume_upload.filename
        )
        print(f"✅ Quiz generation completed!")
        
        # Ensure we have exactly 30 questions
        questions = quiz_data.get("questions", [])
        if len(questions) < 30:
            # If we have fewer than 30 questions, try to generate more
            additional_needed = 30 - len(questions)
            tech_skills = extracted_topics.get("technical_skills", ["General Programming"])
            
            # Generate additional questions
            from services.gemini_client import generate_quiz
            additional_prompt = f"Create {additional_needed} additional multiple choice questions about {', '.join(tech_skills[:3])}"
            additional_quiz = generate_quiz(additional_prompt, difficulty="medium")
            
            if additional_quiz and "questions" in additional_quiz:
                questions.extend(additional_quiz["questions"][:additional_needed])
        
        # Limit to exactly 30 questions
        questions = questions[:30]
        
        quiz_content = {
            "title": quiz_data.get("title", f"Resume Assessment: {resume_upload.filename}"),
            "resume_filename": resume_upload.filename,
            "questions": questions,
            "total_questions": len(questions),
            "extracted_topics": extracted_topics.get("technical_skills", []),
            "difficulty": quiz_data.get("difficulty", "medium"),
            "experience_level": extracted_topics.get("experience_years", 0)
        }
        
        # Save quiz to database
        resume_quiz = ResumeQuiz(
            resume_upload_id=upload_id,
            content_json=json.dumps(quiz_content),
            difficulty=quiz_data.get("difficulty", "medium"),
            total_questions=len(questions),
            created_at=datetime.utcnow()
        )
        
        db.add(resume_quiz)
        db.commit()
        db.refresh(resume_quiz)
        
        return ResumeQuizResponse(
            id=resume_quiz.id,
            resume_upload_id=resume_quiz.resume_upload_id,
            quiz_content=quiz_content,
            message="Quiz generated successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

@router.get("/resume-uploads", response_model=List[ResumeUploadResponse])
async def get_resume_uploads(db: Session = Depends(get_db)):
    """Get all uploaded resumes"""
    try:
        uploads = db.query(ResumeUpload).order_by(ResumeUpload.uploaded_at.desc()).all()
        
        result = []
        for upload in uploads:
            extracted_topics = json.loads(upload.extracted_topics) if upload.extracted_topics else {}
            result.append(ResumeUploadResponse(
                id=upload.id,
                filename=upload.filename,
                extracted_topics=extracted_topics,
                message="Resume data retrieved"
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve uploads: {str(e)}")

@router.get("/resume-quiz/{upload_id}", response_model=ResumeQuizResponse)
async def get_resume_quiz(
    upload_id: int,
    db: Session = Depends(get_db)
):
    """Get quiz for a specific resume upload"""
    try:
        resume_quiz = db.query(ResumeQuiz).filter(ResumeQuiz.resume_upload_id == upload_id).first()
        
        if not resume_quiz:
            raise HTTPException(status_code=404, detail="Quiz not found for this resume")
        
        quiz_content = json.loads(resume_quiz.content_json)
        
        return ResumeQuizResponse(
            id=resume_quiz.id,
            resume_upload_id=resume_quiz.resume_upload_id,
            quiz_content=quiz_content,
            message="Quiz retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve quiz: {str(e)}")

@router.delete("/resume-upload/{upload_id}")
async def delete_resume_upload(
    upload_id: int,
    db: Session = Depends(get_db)
):
    """Delete a resume upload and its associated quiz"""
    try:
        # Delete associated quiz first
        db.query(ResumeQuiz).filter(ResumeQuiz.resume_upload_id == upload_id).delete()
        
        # Delete the resume upload
        resume_upload = db.query(ResumeUpload).filter(ResumeUpload.id == upload_id).first()
        if not resume_upload:
            raise HTTPException(status_code=404, detail="Resume upload not found")
        
        db.delete(resume_upload)
        db.commit()
        
        return {"message": "Resume upload and associated quiz deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete resume upload: {str(e)}")