from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from config import DATABASE_URI

engine = create_engine(DATABASE_URI)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), nullable=False)  

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class University(Base):
    __tablename__ = 'universities'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    courses = relationship("UniversityCourse", back_populates="university")
    plans = relationship("Plan", back_populates="university")  

class UniversityCourse(Base):
    __tablename__ = 'university_courses'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    credits = Column(Integer)
    department = Column(String(100))
    prerequisites = Column(Text)
    language = Column(String(10), default='en')
    university_id = Column(Integer, ForeignKey('universities.id'))
    university = relationship("University", back_populates="courses")

class Plan(Base):
    __tablename__ = 'plans'
    id = Column(Integer, primary_key=True)
    major = Column(String(100), nullable=False)
    university_id = Column(Integer, ForeignKey('universities.id'))
    university = relationship("University", back_populates="plans")  

class ComparisonHistory(Base):
    __tablename__ = 'comparison_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    input_data = Column(Text)  
    equivalency_score = Column(Float)
    matched_course_id = Column(Integer, ForeignKey('university_courses.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    decision = Column(String(20))  
    matched_course = relationship("UniversityCourse")
    user = relationship("User")

class Feedback(Base):
    __tablename__ = 'feedbacks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")

#Base.metadata.create_all(engine)