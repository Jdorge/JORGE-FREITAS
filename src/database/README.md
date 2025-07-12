# Database Module

This module provides a comprehensive database layer for the microservices architecture, supporting both PostgreSQL and Redis for caching.

## Features

- **SQLAlchemy ORM**: Full ORM support with PostgreSQL
- **Redis Caching**: High-performance caching layer
- **Repository Pattern**: Clean separation of data access logic
- **Migration System**: Database schema versioning and migrations
- **Connection Pooling**: Optimized database connections
- **Data Validation**: Input sanitization and validation
- **Logging**: Comprehensive system logging

## Structure

```
src/database/
├── __init__.py          # Package initialization
├── config.py            # Database configuration and settings
├── models.py            # SQLAlchemy models
├── session.py           # Database session management
├── repositories.py      # Repository pattern implementation
├── migrations.py        # Database migration utilities
├── cache.py            # Redis caching layer
└── utils.py            # Database utility functions
```

## Models

### Core Models

- **User**: User authentication and management
- **DataAnalysis**: Data analysis requests and results
- **AnalysisFile**: Files associated with analyses
- **ToolGeneration**: Interactive tool generation requests
- **SystemLog**: System events and logging
- **CacheEntry**: Database-backed cache entries

### Relationships

- Users have many DataAnalyses and ToolGenerations
- DataAnalyses have many AnalysisFiles
- All models include audit fields (created_at, updated_at)

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/microservices_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=microservices_db
DATABASE_USER=user
DATABASE_PASSWORD=password

# Redis
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Connection Pool
POOL_SIZE=20
MAX_OVERFLOW=30
POOL_TIMEOUT=30
POOL_RECYCLE=3600
```

## Usage

### Basic Database Operations

```python
from src.database.session import get_db
from src.database.repositories import user_repo, data_analysis_repo

# Get database session
db = next(get_db())

# Create a user
user = user_repo.create(db, 
    username="john_doe",
    email="john@example.com",
    hashed_password="hashed_password"
)

# Get user by ID
user = user_repo.get_by_id(db, user_id)

# Update user
user_repo.update(db, user_id, email="new_email@example.com")

# Delete user
user_repo.delete(db, user_id)
```

### Caching Operations

```python
from src.database.cache import get_cache_manager

cache = get_cache_manager()

# Cache analysis result
cache.cache_analysis_result("analysis_123", {"result": "data"}, ttl=3600)

# Get cached result
result = cache.get_cached_analysis_result("analysis_123")

# Cache user data
cache.cache_user_data("user_123", {"name": "John"}, ttl=1800)

# Invalidate user cache
cache.invalidate_user_cache("user_123")
```

### Database Migrations

```python
from src.database.migrations import setup_database, reset_database

# Setup database with all migrations
setup_database()

# Reset database (drop all tables and recreate)
reset_database()

# Check database health
from src.database.migrations import check_database_health
health = check_database_health()
print(health["status"])  # "healthy" or "unhealthy"
```

### Data Validation

```python
from src.database.utils import validate_user_data, validate_analysis_data

# Validate user data
user_data = {"username": "john", "email": "john@example.com"}
validation = validate_user_data(user_data)

if validation["valid"]:
    # Use sanitized data
    sanitized_data = validation["data"]
else:
    # Handle errors
    errors = validation["errors"]
```

## Repository Pattern

Each model has a corresponding repository class that provides:

- **CRUD Operations**: Create, Read, Update, Delete
- **Query Methods**: Custom queries for specific use cases
- **Pagination**: Built-in pagination support
- **Filtering**: Flexible filtering options

### Available Repositories

- `UserRepository`: User management
- `DataAnalysisRepository`: Data analysis operations
- `AnalysisFileRepository`: File management
- `ToolGenerationRepository`: Tool generation operations
- `SystemLogRepository`: System logging
- `CacheEntryRepository`: Cache management

## Caching Strategy

### Cache Layers

1. **Redis Cache**: High-performance in-memory caching
2. **Database Cache**: Persistent cache entries
3. **Application Cache**: In-memory application caching

### Cache Keys

- `user:{user_id}`: User data
- `user_analyses:{user_id}`: User's analysis list
- `analysis_result:{analysis_id}`: Analysis results
- `tool_generation:{tool_id}`: Tool generation results
- `system_stats`: System statistics
- `api:{endpoint}:{hash}`: API response caching

## Performance Optimization

### Indexes

The database includes optimized indexes for:

- User lookups (username, email)
- Analysis queries (user_id, status, created_at)
- File queries (analysis_id, file_type)
- Tool queries (user_id, status, tool_type)
- Log queries (service, level, created_at)

### Connection Pooling

- **Pool Size**: 20 connections
- **Max Overflow**: 30 additional connections
- **Timeout**: 30 seconds
- **Recycle**: 1 hour

### Partitioning

System logs are partitioned by date for better performance with large datasets.

## Monitoring and Logging

### System Events

```python
from src.database.utils import log_system_event

log_system_event(
    db=db,
    service="data_analyzer",
    level="INFO",
    message="Analysis completed",
    details={"analysis_id": "123", "duration": 5.2}
)
```

### Database Statistics

```python
from src.database.utils import get_database_stats

stats = get_database_stats(db)
print(f"Total users: {stats['users']}")
print(f"Recent analyses: {stats['recent_analyses']}")
```

## Maintenance

### Cleanup Operations

```python
from src.database.utils import cleanup_old_data

# Clean up data older than 30 days
cleanup_stats = cleanup_old_data(db, days=30)
print(f"Cleaned up {cleanup_stats['system_logs']} old logs")
```

### Backup Operations

```python
from src.database.utils import backup_database_data

# Create backup
success = backup_database_data(db, "backup.json")
if success:
    print("Backup created successfully")
```

## Error Handling

The database module includes comprehensive error handling:

- **Connection Errors**: Automatic retry and fallback
- **Validation Errors**: Detailed error messages
- **Transaction Errors**: Automatic rollback
- **Cache Errors**: Graceful degradation

## Testing

### Database Testing

```python
import pytest
from src.database.session import get_db
from src.database.repositories import user_repo

@pytest.fixture
def db_session():
    return next(get_db())

def test_create_user(db_session):
    user = user_repo.create(db_session, 
        username="test_user",
        email="test@example.com",
        hashed_password="hashed"
    )
    assert user.username == "test_user"
```

## Security Considerations

- **Password Hashing**: Use bcrypt or similar for password storage
- **SQL Injection**: SQLAlchemy provides protection
- **Input Validation**: All inputs are validated and sanitized
- **Connection Security**: Use SSL for database connections
- **Access Control**: Implement proper user permissions

## Dependencies

- **SQLAlchemy**: ORM and database abstraction
- **psycopg2**: PostgreSQL adapter
- **redis**: Redis client
- **pydantic**: Data validation
- **passlib**: Password hashing

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Initialize database:
```python
from src.database.migrations import setup_database
setup_database()
```

## Contributing

When adding new models or modifying existing ones:

1. Update the model in `models.py`
2. Create corresponding repository methods
3. Add validation functions in `utils.py`
4. Update migrations if needed
5. Add tests for new functionality
6. Update documentation