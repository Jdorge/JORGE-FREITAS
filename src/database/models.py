from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class User(Base):
    """User model for authentication and user management."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    data_analyses = relationship("DataAnalysis", back_populates="user")
    tool_generations = relationship("ToolGeneration", back_populates="user")


class DataAnalysis(Base):
    """Model for storing data analysis results."""
    __tablename__ = "data_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    data_source = Column(String(500))  # URL or file path
    analysis_type = Column(String(50))  # e.g., 'statistical', 'ml', 'visualization'
    parameters = Column(JSON)  # Analysis parameters
    results = Column(JSON)  # Analysis results
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    progress = Column(Float, default=0.0)  # Progress percentage
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="data_analyses")
    analysis_files = relationship("AnalysisFile", back_populates="data_analysis")


class AnalysisFile(Base):
    """Model for storing files related to data analysis."""
    __tablename__ = "analysis_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_analysis_id = Column(UUID(as_uuid=True), ForeignKey("data_analyses.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))  # e.g., 'input', 'output', 'report'
    file_size = Column(Integer)  # Size in bytes
    mime_type = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    data_analysis = relationship("DataAnalysis", back_populates="analysis_files")


class ToolGeneration(Base):
    """Model for storing interactive tool generation requests and results."""
    __tablename__ = "tool_generations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tool_name = Column(String(200), nullable=False)
    description = Column(Text)
    tool_type = Column(String(50))  # e.g., 'calculator', 'converter', 'analyzer'
    requirements = Column(JSON)  # Tool requirements and specifications
    generated_code = Column(Text)  # Generated tool code
    dependencies = Column(JSON)  # Required dependencies
    status = Column(String(20), default="pending")  # pending, generating, completed, failed
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="tool_generations")


class SystemLog(Base):
    """Model for storing system logs and events."""
    __tablename__ = "system_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    level = Column(String(20), nullable=False)  # DEBUG, INFO, WARNING, ERROR
    service = Column(String(50), nullable=False)  # data_analyzer, tool_generator
    message = Column(Text, nullable=False)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        {"postgresql_partition_by": "RANGE (created_at)"}
    )


class CacheEntry(Base):
    """Model for storing cache entries."""
    __tablename__ = "cache_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(255), nullable=False, unique=True, index=True)
    value = Column(JSON)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)