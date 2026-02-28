from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    skills = relationship("Skill", back_populates="owner")


class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    file_path = Column(String(500), nullable=False)
    status = Column(String(20), default="pending")  # pending, analyzing, completed, failed
    
    # Technical scores (0-100)
    tool_capability_score = Column(Float, default=0)
    code_quality_score = Column(Float, default=0)
    logic_score = Column(Float, default=0)
    rag_score = Column(Float, default=0)
    technical_total = Column(Float, default=0)
    
    # AI performance scores (0-100)
    task_completion_score = Column(Float, default=0)
    instruction_following_score = Column(Float, default=0)
    robustness_score = Column(Float, default=0)
    token_efficiency_score = Column(Float, default=0)
    ai_total = Column(Float, default=0)
    
    # Overall
    total_score = Column(Float, default=0)
    
    # Report
    report_json = Column(Text)
    report_html = Column(Text)
    report_markdown = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="skills")
