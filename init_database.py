#!/usr/bin/env python3
"""
Database initialization script for the microservices project.
This script sets up the database schema, creates initial data, and performs health checks.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.database.migrations import setup_database, check_database_health
from src.database.session import check_database_connection
from src.database.cache import get_cache_manager
from src.database.utils import log_system_event
from src.database.session import SessionLocal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize the database with schema and initial setup."""
    logger.info("Starting database initialization...")
    
    # Check database connection
    logger.info("Checking database connection...")
    if not check_database_connection():
        logger.error("Database connection failed. Please check your configuration.")
        return False
    
    # Setup database schema
    logger.info("Setting up database schema...")
    try:
        setup_database()
        logger.info("Database schema setup completed successfully")
    except Exception as e:
        logger.error(f"Database schema setup failed: {e}")
        return False
    
    # Check database health
    logger.info("Checking database health...")
    health = check_database_health()
    if health["status"] != "healthy":
        logger.error(f"Database health check failed: {health['message']}")
        return False
    
    logger.info("Database health check passed")
    
    # Test cache connection
    logger.info("Testing cache connection...")
    cache_manager = get_cache_manager()
    if cache_manager.redis.is_connected():
        logger.info("Cache connection successful")
    else:
        logger.warning("Cache connection failed - continuing without cache")
    
    # Log initialization event
    try:
        db = SessionLocal()
        log_system_event(
            db=db,
            service="database_init",
            level="INFO",
            message="Database initialization completed successfully",
            details={"tables": health.get("tables", [])}
        )
        db.close()
    except Exception as e:
        logger.warning(f"Could not log initialization event: {e}")
    
    logger.info("Database initialization completed successfully!")
    return True


def create_sample_data():
    """Create sample data for development/testing."""
    logger.info("Creating sample data...")
    
    try:
        from src.database.repositories import user_repo, data_analysis_repo, tool_generation_repo
        from src.database.session import SessionLocal
        import uuid
        
        db = SessionLocal()
        
        # Create sample user
        sample_user = user_repo.create(db,
            username="demo_user",
            email="demo@example.com",
            hashed_password="hashed_password_123",
            is_active=True
        )
        logger.info(f"Created sample user: {sample_user.username}")
        
        # Create sample data analysis
        sample_analysis = data_analysis_repo.create(db,
            user_id=sample_user.id,
            title="Sample Data Analysis",
            description="A sample data analysis for demonstration",
            analysis_type="statistical",
            status="completed",
            parameters={"method": "correlation"},
            results={"correlation": 0.85, "p_value": 0.001}
        )
        logger.info(f"Created sample analysis: {sample_analysis.title}")
        
        # Create sample tool generation
        sample_tool = tool_generation_repo.create(db,
            user_id=sample_user.id,
            tool_name="Sample Calculator",
            description="A sample calculator tool",
            tool_type="calculator",
            status="completed",
            requirements={"operation": "addition"},
            generated_code="def add(a, b): return a + b"
        )
        logger.info(f"Created sample tool: {sample_tool.tool_name}")
        
        db.close()
        logger.info("Sample data created successfully")
        
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        return False
    
    return True


def main():
    """Main initialization function."""
    print("=" * 60)
    print("Database Initialization Script")
    print("=" * 60)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("Warning: .env file not found. Using default configuration.")
        print("Please copy .env.example to .env and configure your settings.")
        print()
    
    # Initialize database
    if not init_database():
        print("❌ Database initialization failed!")
        sys.exit(1)
    
    print("✅ Database initialization completed successfully!")
    print()
    
    # Ask if user wants to create sample data
    create_samples = input("Would you like to create sample data? (y/N): ").lower().strip()
    if create_samples in ['y', 'yes']:
        if create_sample_data():
            print("✅ Sample data created successfully!")
        else:
            print("❌ Sample data creation failed!")
    
    print()
    print("Database setup complete!")
    print("You can now start your microservices:")
    print("  - Data Analyzer: python start_data_analyzer.py")
    print("  - Tool Generator: python start_tool_generator.py")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()