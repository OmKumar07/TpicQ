import os
import re
import json
from typing import List, Dict, Optional
import tempfile
from PyPDF2 import PdfReader
from docx import Document

class ResumeProcessor:
    """Service for processing resume files and extracting relevant information"""
    
    def __init__(self):
        self.tech_keywords = [
            # Programming Languages
            "python", "javascript", "java", "c++", "c#", "php", "ruby", "go", "rust", "swift",
            "kotlin", "typescript", "scala", "r", "matlab", "sql", "html", "css", "sass", "scss",
            
            # Frameworks & Libraries
            "react", "angular", "vue", "node.js", "express", "django", "flask", "spring", "laravel",
            "rails", "asp.net", "xamarin", "flutter", "react native", "bootstrap", "tailwind",
            "jquery", "vue.js", "next.js", "nuxt.js", "svelte", "ember", "backbone",
            
            # Databases
            "mysql", "postgresql", "mongodb", "redis", "cassandra", "elasticsearch", "sqlite",
            "oracle", "sql server", "dynamodb", "firebase", "supabase",
            
            # Cloud & DevOps
            "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "jenkins", "gitlab",
            "github", "terraform", "ansible", "vagrant", "chef", "puppet", "ci/cd", "devops",
            
            # Data & Analytics
            "machine learning", "data science", "artificial intelligence", "deep learning",
            "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn", "jupyter", "tableau",
            "power bi", "spark", "hadoop", "kafka", "airflow",
            
            # Mobile Development
            "ios", "android", "mobile development", "app development", "xamarin", "ionic",
            
            # Web Technologies
            "rest api", "graphql", "microservices", "web development", "frontend", "backend",
            "full stack", "api development", "web services", "json", "xml", "ajax",
            
            # Tools & Methodologies
            "git", "svn", "jira", "confluence", "agile", "scrum", "kanban", "tdd", "bdd",
            "unit testing", "integration testing", "selenium", "jest", "cypress", "postman",
            
            # Operating Systems
            "linux", "windows", "macos", "ubuntu", "centos", "debian",
            
            # Other Technologies
            "blockchain", "cryptocurrency", "iot", "ar", "vr", "augmented reality", "virtual reality"
        ]
        
        self.soft_skills = [
            "leadership", "teamwork", "communication", "problem solving", "analytical thinking",
            "project management", "time management", "adaptability", "creativity", "collaboration",
            "critical thinking", "decision making", "interpersonal skills", "presentation",
            "public speaking", "mentoring", "coaching", "training", "documentation"
        ]
    
    async def extract_text_from_file(self, file_content: bytes, filename: str) -> str:
        """Extract text from PDF or DOCX file"""
        try:
            file_extension = os.path.splitext(filename)[1].lower()
            
            if file_extension == '.pdf':
                return await self._extract_from_pdf(file_content)
            elif file_extension in ['.docx', '.doc']:
                return await self._extract_from_docx(file_content)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            raise Exception(f"Failed to extract text from {filename}: {str(e)}")
    
    async def _extract_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                reader = PdfReader(temp_file_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                return text.strip()
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    async def _extract_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                doc = Document(temp_file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                
                return text.strip()
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            raise Exception(f"Failed to extract text from DOCX: {str(e)}")
    
    def extract_topics_and_skills(self, resume_text: str) -> Dict[str, List[str]]:
        """Extract technical skills and topics from resume text"""
        resume_lower = resume_text.lower()
        
        # Find technical keywords
        found_tech_skills = []
        for keyword in self.tech_keywords:
            if keyword.lower() in resume_lower:
                found_tech_skills.append(keyword.title())
        
        # Find soft skills
        found_soft_skills = []
        for skill in self.soft_skills:
            if skill.lower() in resume_lower:
                found_soft_skills.append(skill.title())
        
        # Extract years of experience patterns
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\+?\s*yrs?\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\+?\s*years?\s*in',
            r'(\d+)\+?\s*yrs?\s*in'
        ]
        
        experience_years = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, resume_lower)
            experience_years.extend([int(match) for match in matches])
        
        # Extract education/certifications
        education_keywords = [
            "bachelor", "master", "phd", "doctorate", "degree", "certification", "certified",
            "diploma", "associate", "mba", "ms", "bs", "ba", "ma", "btech", "mtech"
        ]
        
        found_education = []
        for keyword in education_keywords:
            if keyword.lower() in resume_lower:
                found_education.append(keyword.title())
        
        # Remove duplicates and sort
        found_tech_skills = sorted(list(set(found_tech_skills)))
        found_soft_skills = sorted(list(set(found_soft_skills)))
        found_education = sorted(list(set(found_education)))
        
        return {
            "technical_skills": found_tech_skills[:15],  # Limit to top 15
            "soft_skills": found_soft_skills[:10],       # Limit to top 10
            "education": found_education[:5],            # Limit to top 5
            "experience_years": max(experience_years) if experience_years else 0
        }
    
    def generate_resume_quiz(self, resume_text: str, extracted_topics: Dict, filename: str) -> Dict:
        """Generate a 30-question quiz based on resume content"""
        try:
            tech_skills = extracted_topics.get("technical_skills", [])
            soft_skills = extracted_topics.get("soft_skills", [])
            experience_years = extracted_topics.get("experience_years", 0)
            
            # Create a prompt for generating resume-based questions
            if tech_skills:
                primary_skills = tech_skills[:5]  # Focus on top 5 technical skills
                skills_text = ", ".join(primary_skills)
                
                # Determine difficulty based on experience (made more challenging)
                if experience_years >= 3:
                    difficulty = "hard"  # Lowered threshold from 5 to 3
                elif experience_years >= 1:
                    difficulty = "medium"  # Lowered threshold from 2 to 1
                else:
                    difficulty = "medium"  # Default to medium instead of easy
                
                # Create a specialized prompt for resume-based quiz
                prompt = f"""
                Create a comprehensive 30-question multiple choice quiz for someone with experience in: {skills_text}.
                
                Based on their resume, they have {experience_years} years of experience.
                Difficulty level: {difficulty}
                
                Focus on:
                - Technical concepts related to their skills
                - Best practices and industry standards
                - Problem-solving scenarios
                - Integration between different technologies they know
                
                Return EXACTLY 30 questions in this JSON format:
                {{
                    "questions": [
                        {{
                            "q": "Question text here?",
                            "options": ["Option A", "Option B", "Option C", "Option D"],
                            "answer_index": 0,
                            "category": "Technical Category"
                        }}
                    ]
                }}
                
                Make questions practical and interview-relevant.
                """
                
                # Use the existing Gemini client to generate questions (3 batches of 10)
                from services.gemini_client import generate_quiz
                
                all_questions = []
                print(f"🎯 Generating quiz for skills: {skills_text}")
                print(f"🔧 Difficulty: {difficulty}, Experience: {experience_years} years")
                
                # Enhanced prompts for tougher questions
                tough_prompts = [
                    f"Create 10 advanced {difficulty} level interview questions about {skills_text}. Focus on complex scenarios, architectural decisions, performance optimization, and real-world problem-solving challenges.",
                    f"Generate 10 expert-level questions on {skills_text}. Include questions about debugging complex issues, system design patterns, integration challenges, and best practices for production environments.",
                    f"Create 10 challenging technical questions for {skills_text}. Focus on edge cases, security considerations, scalability issues, and advanced implementation details that experienced developers face."
                ]
                
                for batch in range(3):  # Generate 3 batches of 10 questions each
                    try:
                        batch_prompt = tough_prompts[batch]
                        print(f"📝 Generating batch {batch + 1}/3...")
                        quiz_response = generate_quiz(batch_prompt, difficulty)
                        
                        if quiz_response and "questions" in quiz_response:
                            questions_count = len(quiz_response["questions"])
                            print(f"✅ Batch {batch + 1} completed: {questions_count} questions")
                            all_questions.extend(quiz_response["questions"])
                        else:
                            print(f"⚠️ Batch {batch + 1} failed: no questions generated")
                    except Exception as batch_error:
                        print(f"❌ Batch {batch + 1} error: {str(batch_error)}")
                        continue
                
                print(f"🎲 Total questions generated: {len(all_questions)}")
                quiz_response = {"questions": all_questions}
                
                if quiz_response and "questions" in quiz_response:
                    return {
                        "title": f"Resume-Based Assessment: {filename}",
                        "resume_filename": filename,
                        "questions": quiz_response["questions"],
                        "total_questions": len(quiz_response["questions"]),
                        "extracted_topics": tech_skills,
                        "difficulty": difficulty,
                        "experience_level": experience_years
                    }
                else:
                    raise Exception("Failed to generate quiz questions")
            else:
                # Fallback for resumes without clear technical skills (made more challenging)
                challenging_topics = [
                    "Advanced Problem Solving and Critical Thinking", 
                    "Strategic Communication and Leadership", 
                    "Complex Project Management and Risk Assessment"
                ]
                
                from services.gemini_client import generate_quiz
                
                all_questions = []
                print(f"🔄 Fallback mode: generating challenging professional questions")
                
                for topic in challenging_topics:
                    try:
                        print(f"📝 Generating questions for: {topic}")
                        quiz_response = generate_quiz(topic, difficulty="hard")  # Always use hard for fallback
                        if quiz_response and "questions" in quiz_response:
                            questions_count = len(quiz_response["questions"])
                            print(f"✅ {topic} completed: {questions_count} questions")
                            all_questions.extend(quiz_response["questions"])
                        else:
                            print(f"⚠️ {topic} failed: no questions generated")
                    except Exception as topic_error:
                        print(f"❌ {topic} error: {str(topic_error)}")
                        continue
                
                print(f"🎲 Total fallback questions: {len(all_questions)}")
                quiz_response = {"questions": all_questions}
                
                return {
                    "title": f"Professional Skills Assessment: {filename}",
                    "resume_filename": filename,
                    "questions": quiz_response.get("questions", []),
                    "total_questions": len(quiz_response.get("questions", [])),
                    "extracted_topics": challenging_topics,
                    "difficulty": "hard",
                    "experience_level": experience_years
                }
                
        except Exception as e:
            print(f"❌ Error in generate_resume_quiz: {str(e)}")
            print(f"🔍 Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to generate resume quiz: {str(e)}")
    
    def validate_file(self, filename: str, file_size: int) -> bool:
        """Validate file type and size"""
        allowed_extensions = ['.pdf', '.doc', '.docx']
        max_size = 5 * 1024 * 1024  # 5MB
        
        file_extension = os.path.splitext(filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise ValueError(f"File type {file_extension} not supported. Please upload PDF, DOC, or DOCX files.")
        
        if file_size > max_size:
            raise ValueError(f"File size {file_size / (1024*1024):.1f}MB exceeds maximum size of 5MB.")
        
        return True

# Global instance
resume_processor = ResumeProcessor()