import uuid
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from .models import User, DataAnalysis, AnalysisFile, ToolGeneration, SystemLog
from .repositories import (
    user_repo, data_analysis_repo, analysis_file_repo,
    tool_generation_repo, system_log_repo
)
from .cache import get_cache_manager

logger = logging.getLogger(__name__)


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


def validate_uuid(uuid_string: str) -> bool:
    """Validate if a string is a valid UUID."""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string."""
    return dt.isoformat() if dt else None


def parse_datetime(dt_string: str) -> Optional[datetime]:
    """Parse ISO datetime string."""
    try:
        return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return None


def sanitize_json_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize JSON data for database storage."""
    if not isinstance(data, dict):
        return {}
    
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, (str, int, float, bool, type(None))):
            sanitized[key] = value
        elif isinstance(value, (list, dict)):
            # Convert to string representation for complex types
            sanitized[key] = str(value)
        else:
            # Skip unsupported types
            continue
    
    return sanitized


def get_database_stats(db: Session) -> Dict[str, Any]:
    """Get database statistics."""
    try:
        stats = {
            "users": db.query(func.count(User.id)).scalar(),
            "data_analyses": db.query(func.count(DataAnalysis.id)).scalar(),
            "analysis_files": db.query(func.count(AnalysisFile.id)).scalar(),
            "tool_generations": db.query(func.count(ToolGeneration.id)).scalar(),
            "system_logs": db.query(func.count(SystemLog.id)).scalar(),
        }
        
        # Get recent activity
        last_week = datetime.utcnow() - timedelta(days=7)
        stats["recent_analyses"] = db.query(func.count(DataAnalysis.id)).filter(
            DataAnalysis.created_at >= last_week
        ).scalar()
        
        stats["recent_tools"] = db.query(func.count(ToolGeneration.id)).filter(
            ToolGeneration.created_at >= last_week
        ).scalar()
        
        return stats
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {}


def cleanup_old_data(db: Session, days: int = 30) -> Dict[str, int]:
    """Clean up old data from database."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    cleanup_stats = {}
    
    try:
        # Clean up old system logs
        old_logs = system_log_repo.cleanup_old_logs(db, days)
        cleanup_stats["system_logs"] = old_logs
        
        # Clean up expired cache entries
        expired_cache = cache_entry_repo.cleanup_expired(db)
        cleanup_stats["cache_entries"] = expired_cache
        
        # Clean up failed analyses older than specified days
        failed_analyses = db.query(DataAnalysis).filter(
            and_(
                DataAnalysis.status == "failed",
                DataAnalysis.created_at < cutoff_date
            )
        ).delete()
        cleanup_stats["failed_analyses"] = failed_analyses
        
        db.commit()
        logger.info(f"Cleanup completed: {cleanup_stats}")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        db.rollback()
        cleanup_stats = {}
    
    return cleanup_stats


def backup_database_data(db: Session, backup_path: str) -> bool:
    """Create a backup of important database data."""
    try:
        import json
        
        backup_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "users": [],
            "data_analyses": [],
            "tool_generations": []
        }
        
        # Backup users (without sensitive data)
        users = user_repo.get_all(db)
        for user in users:
            backup_data["users"].append({
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "created_at": format_datetime(user.created_at)
            })
        
        # Backup recent analyses
        recent_analyses = data_analysis_repo.get_recent_analyses(db, days=30)
        for analysis in recent_analyses:
            backup_data["data_analyses"].append({
                "id": str(analysis.id),
                "user_id": str(analysis.user_id),
                "title": analysis.title,
                "analysis_type": analysis.analysis_type,
                "status": analysis.status,
                "created_at": format_datetime(analysis.created_at)
            })
        
        # Backup recent tool generations
        recent_tools = tool_generation_repo.get_by_status(db, "completed")
        for tool in recent_tools[:100]:  # Limit to 100 most recent
            backup_data["tool_generations"].append({
                "id": str(tool.id),
                "user_id": str(tool.user_id),
                "tool_name": tool.tool_name,
                "tool_type": tool.tool_type,
                "status": tool.status,
                "created_at": format_datetime(tool.created_at)
            })
        
        # Write backup to file
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        logger.info(f"Database backup created: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating database backup: {e}")
        return False


def validate_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize user data."""
    errors = []
    sanitized_data = {}
    
    # Validate username
    username = user_data.get("username", "").strip()
    if not username:
        errors.append("Username is required")
    elif len(username) < 3 or len(username) > 50:
        errors.append("Username must be between 3 and 50 characters")
    else:
        sanitized_data["username"] = username
    
    # Validate email
    email = user_data.get("email", "").strip()
    if not email:
        errors.append("Email is required")
    elif "@" not in email or "." not in email:
        errors.append("Invalid email format")
    else:
        sanitized_data["email"] = email.lower()
    
    # Validate password (if provided)
    password = user_data.get("password")
    if password:
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")
        else:
            sanitized_data["password"] = password
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "data": sanitized_data
    }


def validate_analysis_data(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize analysis data."""
    errors = []
    sanitized_data = {}
    
    # Validate title
    title = analysis_data.get("title", "").strip()
    if not title:
        errors.append("Analysis title is required")
    elif len(title) > 200:
        errors.append("Title must be less than 200 characters")
    else:
        sanitized_data["title"] = title
    
    # Validate analysis type
    analysis_type = analysis_data.get("analysis_type", "").strip()
    valid_types = ["statistical", "ml", "visualization", "correlation", "trend"]
    if analysis_type and analysis_type not in valid_types:
        errors.append(f"Invalid analysis type. Must be one of: {', '.join(valid_types)}")
    else:
        sanitized_data["analysis_type"] = analysis_type
    
    # Validate parameters
    parameters = analysis_data.get("parameters")
    if parameters:
        sanitized_data["parameters"] = sanitize_json_data(parameters)
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "data": sanitized_data
    }


def validate_tool_data(tool_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize tool generation data."""
    errors = []
    sanitized_data = {}
    
    # Validate tool name
    tool_name = tool_data.get("tool_name", "").strip()
    if not tool_name:
        errors.append("Tool name is required")
    elif len(tool_name) > 200:
        errors.append("Tool name must be less than 200 characters")
    else:
        sanitized_data["tool_name"] = tool_name
    
    # Validate tool type
    tool_type = tool_data.get("tool_type", "").strip()
    valid_types = ["calculator", "converter", "analyzer", "generator", "validator"]
    if tool_type and tool_type not in valid_types:
        errors.append(f"Invalid tool type. Must be one of: {', '.join(valid_types)}")
    else:
        sanitized_data["tool_type"] = tool_type
    
    # Validate requirements
    requirements = tool_data.get("requirements")
    if requirements:
        sanitized_data["requirements"] = sanitize_json_data(requirements)
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "data": sanitized_data
    }


def log_system_event(db: Session, service: str, level: str, message: str, details: Dict[str, Any] = None):
    """Log a system event to the database."""
    try:
        system_log_repo.create(db, 
            service=service,
            level=level,
            message=message,
            details=details or {}
        )
    except Exception as e:
        logger.error(f"Error logging system event: {e}")


def get_user_activity_summary(db: Session, user_id: str) -> Dict[str, Any]:
    """Get a summary of user activity."""
    try:
        # Get user's analyses
        analyses = data_analysis_repo.get_by_user_id(db, user_id)
        
        # Get user's tool generations
        tools = tool_generation_repo.get_by_user_id(db, user_id)
        
        # Calculate statistics
        total_analyses = len(analyses)
        completed_analyses = len([a for a in analyses if a.status == "completed"])
        failed_analyses = len([a for a in analyses if a.status == "failed"])
        
        total_tools = len(tools)
        completed_tools = len([t for t in tools if t.status == "completed"])
        
        # Get recent activity
        last_week = datetime.utcnow() - timedelta(days=7)
        recent_analyses = len([a for a in analyses if a.created_at >= last_week])
        recent_tools = len([t for t in tools if t.created_at >= last_week])
        
        return {
            "total_analyses": total_analyses,
            "completed_analyses": completed_analyses,
            "failed_analyses": failed_analyses,
            "success_rate": (completed_analyses / total_analyses * 100) if total_analyses > 0 else 0,
            "total_tools": total_tools,
            "completed_tools": completed_tools,
            "recent_analyses": recent_analyses,
            "recent_tools": recent_tools,
            "last_activity": format_datetime(max([a.created_at for a in analyses] + [t.created_at for t in tools])) if analyses or tools else None
        }
    except Exception as e:
        logger.error(f"Error getting user activity summary: {e}")
        return {}


# Import missing dependencies
from sqlalchemy import and_
from .repositories import cache_entry_repo