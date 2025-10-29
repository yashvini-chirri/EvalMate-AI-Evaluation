from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    standard = Column(String, nullable=False)  # 10th, 11th, 12th
    section = Column(String, nullable=False)   # A, B
    roll_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    evaluations = relationship("Evaluation", back_populates="student")

class Examiner(Base):
    __tablename__ = "examiners"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    subject = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    tests = relationship("Test", back_populates="examiner")

class Test(Base):
    __tablename__ = "tests"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    standard = Column(String, nullable=False)  # 10th, 11th, 12th
    section = Column(String, nullable=False)   # A, B
    examiner_id = Column(Integer, ForeignKey("examiners.id"))
    
    # File paths
    question_paper_path = Column(String)
    answer_key_path = Column(String)
    reference_book_path = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    examiner = relationship("Examiner", back_populates="tests")
    evaluations = relationship("Evaluation", back_populates="test")

class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    
    # Answer sheet
    answer_sheet_path = Column(String, nullable=False)
    
    # Evaluation results
    total_marks = Column(Float)
    obtained_marks = Column(Float)
    percentage = Column(Float)
    grade = Column(String)
    
    # AI Analysis
    ocr_text = Column(Text)  # Extracted text from answer sheet
    evaluation_details = Column(Text)  # JSON string with detailed analysis
    feedback = Column(Text)  # AI-generated feedback
    
    # Status
    status = Column(String, default="pending")  # pending, processing, completed, failed
    
    created_at = Column(DateTime, default=datetime.utcnow)
    evaluated_at = Column(DateTime)
    
    # Relationships
    test = relationship("Test", back_populates="evaluations")
    student = relationship("Student", back_populates="evaluations")

class AnswerSheetUpload(Base):
    __tablename__ = "answer_sheet_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer)
    upload_status = Column(String, default="uploaded")  # uploaded, processing, processed, failed
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)