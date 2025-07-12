import os
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session

from .session import engine, SessionLocal
from .models import Base

logger = logging.getLogger(__name__)


class DatabaseMigration:
    """Database migration utility class."""
    
    def __init__(self):
        self.engine = engine
        self.migrations_table = "schema_migrations"
    
    def create_migrations_table(self):
        """Create the migrations tracking table if it doesn't exist."""
        with self.engine.connect() as connection:
            connection.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.migrations_table} (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            connection.commit()
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions."""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(f"SELECT version FROM {self.migrations_table} ORDER BY version"))
                return [row[0] for row in result.fetchall()]
        except Exception as e:
            logger.warning(f"Could not get applied migrations: {e}")
            return []
    
    def record_migration(self, version: str, name: str):
        """Record that a migration has been applied."""
        with self.engine.connect() as connection:
            connection.execute(text(f"""
                INSERT INTO {self.migrations_table} (version, name)
                VALUES (:version, :name)
            """), {"version": version, "name": name})
            connection.commit()
    
    def run_migration(self, version: str, name: str, sql: str):
        """Run a migration and record it."""
        try:
            with self.engine.connect() as connection:
                connection.execute(text(sql))
                connection.commit()
                self.record_migration(version, name)
                logger.info(f"Migration {version}: {name} applied successfully")
        except Exception as e:
            logger.error(f"Migration {version}: {name} failed: {e}")
            raise
    
    def create_initial_schema(self):
        """Create the initial database schema."""
        self.create_migrations_table()
        
        # Create all tables
        Base.metadata.create_all(bind=self.engine)
        
        # Record initial migration
        initial_version = "001"
        initial_name = "initial_schema"
        
        if initial_version not in self.get_applied_migrations():
            self.record_migration(initial_version, initial_name)
            logger.info("Initial schema created successfully")
    
    def add_indexes(self):
        """Add performance indexes to the database."""
        indexes_sql = """
        -- Add indexes for better performance
        
        -- Users table indexes
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
        
        -- DataAnalysis table indexes
        CREATE INDEX IF NOT EXISTS idx_data_analyses_user_id ON data_analyses(user_id);
        CREATE INDEX IF NOT EXISTS idx_data_analyses_status ON data_analyses(status);
        CREATE INDEX IF NOT EXISTS idx_data_analyses_created_at ON data_analyses(created_at);
        CREATE INDEX IF NOT EXISTS idx_data_analyses_analysis_type ON data_analyses(analysis_type);
        
        -- AnalysisFile table indexes
        CREATE INDEX IF NOT EXISTS idx_analysis_files_analysis_id ON analysis_files(data_analysis_id);
        CREATE INDEX IF NOT EXISTS idx_analysis_files_file_type ON analysis_files(file_type);
        
        -- ToolGeneration table indexes
        CREATE INDEX IF NOT EXISTS idx_tool_generations_user_id ON tool_generations(user_id);
        CREATE INDEX IF NOT EXISTS idx_tool_generations_status ON tool_generations(status);
        CREATE INDEX IF NOT EXISTS idx_tool_generations_tool_type ON tool_generations(tool_type);
        CREATE INDEX IF NOT EXISTS idx_tool_generations_created_at ON tool_generations(created_at);
        
        -- SystemLog table indexes
        CREATE INDEX IF NOT EXISTS idx_system_logs_service ON system_logs(service);
        CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);
        CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at);
        
        -- CacheEntry table indexes
        CREATE INDEX IF NOT EXISTS idx_cache_entries_key ON cache_entries(key);
        CREATE INDEX IF NOT EXISTS idx_cache_entries_expires_at ON cache_entries(expires_at);
        """
        
        self.run_migration("002", "add_performance_indexes", indexes_sql)
    
    def add_partitions(self):
        """Add table partitioning for system_logs."""
        partitions_sql = """
        -- Create partitions for system_logs table
        -- This helps with performance for large log tables
        
        -- Create partition for current month
        CREATE TABLE IF NOT EXISTS system_logs_2024_01 PARTITION OF system_logs
        FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
        
        CREATE TABLE IF NOT EXISTS system_logs_2024_02 PARTITION OF system_logs
        FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
        
        CREATE TABLE IF NOT EXISTS system_logs_2024_03 PARTITION OF system_logs
        FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');
        """
        
        self.run_migration("003", "add_table_partitions", partitions_sql)
    
    def run_all_migrations(self):
        """Run all pending migrations."""
        self.create_migrations_table()
        
        # Get applied migrations
        applied = self.get_applied_migrations()
        
        # Define migrations in order
        migrations = [
            ("001", "initial_schema", self.create_initial_schema),
            ("002", "add_performance_indexes", self.add_indexes),
            ("003", "add_table_partitions", self.add_partitions),
        ]
        
        # Run pending migrations
        for version, name, migration_func in migrations:
            if version not in applied:
                if version == "001":
                    migration_func()
                else:
                    migration_func()
                logger.info(f"Migration {version}: {name} completed")
            else:
                logger.info(f"Migration {version}: {name} already applied")


def setup_database():
    """Setup database with all migrations."""
    migration = DatabaseMigration()
    migration.run_all_migrations()


def reset_database():
    """Reset database by dropping all tables and recreating them."""
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    
    logger.info("Recreating database schema...")
    setup_database()


def check_database_health():
    """Check database health and return status."""
    try:
        # Check connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        
        # Check if tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        required_tables = [
            "users", "data_analyses", "analysis_files", 
            "tool_generations", "system_logs", "cache_entries"
        ]
        
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            return {
                "status": "unhealthy",
                "message": f"Missing tables: {missing_tables}",
                "tables": tables
            }
        
        return {
            "status": "healthy",
            "message": "Database is healthy",
            "tables": tables
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {e}",
            "tables": []
        }


if __name__ == "__main__":
    # Run migrations when script is executed directly
    setup_database()