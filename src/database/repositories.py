from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime, timedelta
import uuid

from .models import (
    User, DataAnalysis, AnalysisFile, ToolGeneration, 
    SystemLog, CacheEntry, Base
)


class BaseRepository:
    """Base repository class with common CRUD operations."""
    
    def __init__(self, model_class):
        self.model = model_class
    
    def create(self, db: Session, **kwargs) -> Base:
        """Create a new record."""
        db_obj = self.model(**kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, db: Session, id: uuid.UUID) -> Optional[Base]:
        """Get record by ID."""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Base]:
        """Get all records with pagination."""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def update(self, db: Session, id: uuid.UUID, **kwargs) -> Optional[Base]:
        """Update a record."""
        db_obj = self.get_by_id(db, id)
        if db_obj:
            for key, value in kwargs.items():
                setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: uuid.UUID) -> bool:
        """Delete a record."""
        db_obj = self.get_by_id(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False


class UserRepository(BaseRepository):
    """Repository for User model operations."""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    def get_active_users(self, db: Session) -> List[User]:
        """Get all active users."""
        return db.query(User).filter(User.is_active == True).all()


class DataAnalysisRepository(BaseRepository):
    """Repository for DataAnalysis model operations."""
    
    def __init__(self):
        super().__init__(DataAnalysis)
    
    def get_by_user_id(self, db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[DataAnalysis]:
        """Get analyses by user ID."""
        return db.query(DataAnalysis).filter(
            DataAnalysis.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def get_by_status(self, db: Session, status: str) -> List[DataAnalysis]:
        """Get analyses by status."""
        return db.query(DataAnalysis).filter(DataAnalysis.status == status).all()
    
    def get_recent_analyses(self, db: Session, days: int = 7) -> List[DataAnalysis]:
        """Get recent analyses from the last N days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return db.query(DataAnalysis).filter(
            DataAnalysis.created_at >= cutoff_date
        ).order_by(desc(DataAnalysis.created_at)).all()
    
    def update_status(self, db: Session, analysis_id: uuid.UUID, status: str, progress: float = None) -> Optional[DataAnalysis]:
        """Update analysis status and progress."""
        update_data = {"status": status, "updated_at": datetime.utcnow()}
        if progress is not None:
            update_data["progress"] = progress
        if status == "completed":
            update_data["completed_at"] = datetime.utcnow()
        return self.update(db, analysis_id, **update_data)


class AnalysisFileRepository(BaseRepository):
    """Repository for AnalysisFile model operations."""
    
    def __init__(self):
        super().__init__(AnalysisFile)
    
    def get_by_analysis_id(self, db: Session, analysis_id: uuid.UUID) -> List[AnalysisFile]:
        """Get files by analysis ID."""
        return db.query(AnalysisFile).filter(
            AnalysisFile.data_analysis_id == analysis_id
        ).all()
    
    def get_by_file_type(self, db: Session, analysis_id: uuid.UUID, file_type: str) -> List[AnalysisFile]:
        """Get files by analysis ID and file type."""
        return db.query(AnalysisFile).filter(
            and_(
                AnalysisFile.data_analysis_id == analysis_id,
                AnalysisFile.file_type == file_type
            )
        ).all()


class ToolGenerationRepository(BaseRepository):
    """Repository for ToolGeneration model operations."""
    
    def __init__(self):
        super().__init__(ToolGeneration)
    
    def get_by_user_id(self, db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[ToolGeneration]:
        """Get tool generations by user ID."""
        return db.query(ToolGeneration).filter(
            ToolGeneration.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def get_by_tool_type(self, db: Session, tool_type: str) -> List[ToolGeneration]:
        """Get tool generations by tool type."""
        return db.query(ToolGeneration).filter(ToolGeneration.tool_type == tool_type).all()
    
    def get_by_status(self, db: Session, status: str) -> List[ToolGeneration]:
        """Get tool generations by status."""
        return db.query(ToolGeneration).filter(ToolGeneration.status == status).all()
    
    def update_status(self, db: Session, tool_id: uuid.UUID, status: str) -> Optional[ToolGeneration]:
        """Update tool generation status."""
        update_data = {"status": status, "updated_at": datetime.utcnow()}
        if status == "completed":
            update_data["completed_at"] = datetime.utcnow()
        return self.update(db, tool_id, **update_data)


class SystemLogRepository(BaseRepository):
    """Repository for SystemLog model operations."""
    
    def __init__(self):
        super().__init__(SystemLog)
    
    def get_by_service(self, db: Session, service: str, limit: int = 100) -> List[SystemLog]:
        """Get logs by service."""
        return db.query(SystemLog).filter(
            SystemLog.service == service
        ).order_by(desc(SystemLog.created_at)).limit(limit).all()
    
    def get_by_level(self, db: Session, level: str, limit: int = 100) -> List[SystemLog]:
        """Get logs by level."""
        return db.query(SystemLog).filter(
            SystemLog.level == level
        ).order_by(desc(SystemLog.created_at)).limit(limit).all()
    
    def get_recent_logs(self, db: Session, hours: int = 24) -> List[SystemLog]:
        """Get recent logs from the last N hours."""
        cutoff_date = datetime.utcnow() - timedelta(hours=hours)
        return db.query(SystemLog).filter(
            SystemLog.created_at >= cutoff_date
        ).order_by(desc(SystemLog.created_at)).all()
    
    def cleanup_old_logs(self, db: Session, days: int = 30) -> int:
        """Delete logs older than N days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = db.query(SystemLog).filter(
            SystemLog.created_at < cutoff_date
        ).delete()
        db.commit()
        return result


class CacheEntryRepository(BaseRepository):
    """Repository for CacheEntry model operations."""
    
    def __init__(self):
        super().__init__(CacheEntry)
    
    def get_by_key(self, db: Session, key: str) -> Optional[CacheEntry]:
        """Get cache entry by key."""
        return db.query(CacheEntry).filter(
            and_(
                CacheEntry.key == key,
                CacheEntry.expires_at > datetime.utcnow()
            )
        ).first()
    
    def set_cache(self, db: Session, key: str, value: Dict[str, Any], ttl_seconds: int = 3600) -> CacheEntry:
        """Set cache entry with TTL."""
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        return self.create(db, key=key, value=value, expires_at=expires_at)
    
    def cleanup_expired(self, db: Session) -> int:
        """Delete expired cache entries."""
        result = db.query(CacheEntry).filter(
            CacheEntry.expires_at <= datetime.utcnow()
        ).delete()
        db.commit()
        return result


# Repository instances
user_repo = UserRepository()
data_analysis_repo = DataAnalysisRepository()
analysis_file_repo = AnalysisFileRepository()
tool_generation_repo = ToolGenerationRepository()
system_log_repo = SystemLogRepository()
cache_entry_repo = CacheEntryRepository()