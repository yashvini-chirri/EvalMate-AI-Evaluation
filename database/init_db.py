import sys
import os

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, Student, Examiner
from app.core.security import get_password_hash
from app.core.config import settings

# Create database engine
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize database with tables and default data"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Student).first():
            print("Database already initialized with student data.")
            return
        
        print("Populating database with student credentials...")
        
        # Create students for each standard and section
        standards = ["10th", "11th", "12th"]
        sections = ["A", "B"]
        
        student_id = 1
        for standard in standards:
            for section in sections:
                for roll_num in range(1, 21):  # 20 students per section
                    username = f"student_{standard.lower()}_{section.lower()}_{roll_num:02d}"
                    password = f"pass{roll_num:02d}"  # Shorter password
                    
                    student = Student(
                        username=username,
                        password_hash=get_password_hash(password),
                        first_name=f"Student{roll_num}",
                        last_name=f"{standard}{section}",
                        email=f"{username}@evalmate.edu",
                        standard=standard,
                        section=section,
                        roll_number=roll_num
                    )
                    db.add(student)
                    
                    if student_id % 10 == 0:
                        print(f"Created {student_id} students...")
                    student_id += 1
        
        # Create sample examiners
        examiners_data = [
            {"username": "examiner_math", "password": "math123", "first_name": "John", "last_name": "Smith", "subject": "Mathematics", "email": "john.smith@evalmate.edu"},
            {"username": "examiner_science", "password": "science123", "first_name": "Jane", "last_name": "Doe", "subject": "Science", "email": "jane.doe@evalmate.edu"},
            {"username": "examiner_english", "password": "english123", "first_name": "Robert", "last_name": "Johnson", "subject": "English", "email": "robert.johnson@evalmate.edu"},
            {"username": "examiner_history", "password": "history123", "first_name": "Mary", "last_name": "Williams", "subject": "History", "email": "mary.williams@evalmate.edu"},
        ]
        
        for examiner_data in examiners_data:
            examiner = Examiner(
                username=examiner_data["username"],
                password_hash=get_password_hash(examiner_data["password"]),
                first_name=examiner_data["first_name"],
                last_name=examiner_data["last_name"],
                subject=examiner_data["subject"],
                email=examiner_data["email"]
            )
            db.add(examiner)
        
        db.commit()
        print(f"Successfully created {student_id - 1} students and {len(examiners_data)} examiners!")
        
        # Print sample credentials
        print("\n=== SAMPLE CREDENTIALS ===")
        print("STUDENTS:")
        print("Username: student_10th_a_01 | Password: pass01")
        print("Username: student_11th_b_15 | Password: pass15")
        print("Username: student_12th_a_20 | Password: pass20")
        print("\nEXAMINERS:")
        for examiner_data in examiners_data:
            print(f"Username: {examiner_data['username']} | Password: {examiner_data['password']} | Subject: {examiner_data['subject']}")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()