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
    Base.metadata.drop_all(bind=engine)  # Drop existing tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Populating database with student credentials...")
        
        # Create students for each standard and section
        standards = ["10th", "11th", "12th"]
        sections = ["A", "B"]
        
        # Better student names
        first_names = [
            "Rahul", "Priya", "Aarav", "Anita", "Arjun", "Kavya", "Ravi", "Sneha", 
            "Vikram", "Meera", "Suresh", "Divya", "Kiran", "Pooja", "Manoj", "Lakshmi",
            "Rajesh", "Deepika", "Amit", "Sita"
        ]
        
        student_id = 1
        for standard in standards:
            for section in sections:
                for i in range(20):  # 20 students per section (back to original)
                    roll_num = i + 1
                    username = f"student_{standard.lower()}_{section.lower()}_{roll_num:02d}"
                    password = f"pass{roll_num:02d}"
                    
                    student = Student(
                        username=username,
                        password_hash=get_password_hash(password),
                        first_name=first_names[i],
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
        
        # Create single examiner with admin credentials (old version)
        examiner = Examiner(
            username="admin",
            password_hash=get_password_hash("admin123"),
            first_name="Admin",
            last_name="User",
            subject="All Subjects",
            email="admin@evalmate.edu"
        )
        db.add(examiner)
        
        db.commit()
        print(f"Successfully created {student_id - 1} students and 1 examiner!")
        
        # Print sample credentials
        print("\n=== SAMPLE CREDENTIALS ===")
        print("STUDENTS:")
        print("Username: student_10th_a_01 | Password: pass01")
        print("Username: student_11th_b_15 | Password: pass15")
        print("Username: student_12th_a_20 | Password: pass20")
        print("\nEXAMINER:")
        print("Username: admin | Password: admin123 | Subject: All Subjects")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()