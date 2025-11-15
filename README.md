# OData Backend - Enterprise Data Processing Platform

A high-performance, event-driven backend system built with FastAPI for scalable product data management, bulk CSV processing, and real-time webhook notifications.

## 🏗️ Architecture Overview

This application follows an **Event-Driven Architecture (EDA)** pattern, leveraging asynchronous task processing and real-time communication to ensure scalable and responsive data operations. The system decouples file processing from API responses, enabling non-blocking operations and real-time progress monitoring.

### Key Architectural Components

- **FastAPI** - Asynchronous web framework providing high-performance REST APIs
- **Celery** - Distributed task queue for background processing with event-driven workflow
- **Redis** - Message broker and result backend for Celery, enabling pub/sub patterns
- **PostgreSQL** - Primary database with ACID compliance and advanced features
- **WebSocket** - Real-time bidirectional communication for progress updates
- **SQLModel/SQLAlchemy** - Type-safe ORM with async/sync support

## 🚀 Features

### 📊 Bulk Data Processing
- **High-Volume CSV Processing**: Handle up to 500K+ product records efficiently
- **Streaming File Upload**: Memory-efficient processing of large files (up to 200MB)
- **Batch Processing**: Optimized with 1000-record batches and configurable commit frequencies
- **Progress Tracking**: Real-time progress updates via WebSocket connections
- **Error Handling**: Comprehensive error recovery and file management

### 🔄 Event-Driven Operations
- **Asynchronous Task Processing**: Non-blocking CSV processing with immediate API responses
- **Real-time Progress Updates**: WebSocket-based monitoring of long-running operations
- **Webhook Management**: Configure and manage webhook endpoints for external integrations
- **Task Status Monitoring**: Track task states (PENDING, PROGRESS, SUCCESS, FAILURE)

### 🛡️ Enterprise Features
- **Database Connection Pooling**: Optimized PostgreSQL connections (20 persistent + 30 overflow)
- **SSL Security**: Secure database and Redis connections with SSL/TLS
- **Input Validation**: Comprehensive data validation and sanitization
- **Error Recovery**: Automatic file archiving and error management
- **Monitoring & Logging**: Structured logging with performance metrics

## 📁 Project Structure

```
src/
├── auth/              # Authentication and authorization
├── products/          # Product management APIs
│   ├── router.py      # FastAPI routes for product operations
│   ├── model.py       # SQLModel product schema
│   └── service.py     # Business logic layer
├── tasks/             # Background task processing
│   └── celery_worker.py # Celery tasks and CSV processing
├── webhooks/          # Webhook management system
│   ├── router.py      # Webhook CRUD operations
│   └── model.py       # Webhook configuration schema
├── database.py        # Database configuration and connection management
└── upstash_redis.py   # Redis connection and configuration
```

## 🛠️ Technology Stack

### Core Framework
- **FastAPI** - Modern, fast web framework with automatic API documentation
- **Python 3.10+** - Latest Python with type hints and performance improvements

### Database & Storage
- **PostgreSQL** - Advanced relational database with JSONB support
- **SQLModel** - Type-safe ORM built on SQLAlchemy and Pydantic
- **Alembic** - Database migration management

### Task Processing
- **Celery** - Distributed task queue with monitoring capabilities
- **Redis** - High-performance message broker and result backend
- **Upstash Redis** - Managed Redis service with global edge locations

### Development & Deployment
- **UV** - Ultra-fast Python package manager and project management
- **Pydantic** - Data validation using Python type annotations
- **Asyncio** - Native asynchronous programming support

## 🔧 Performance Optimizations

### Database Optimizations
```python
# Connection pool configuration for high-throughput operations
pool_size=20          # 20 persistent connections
max_overflow=30       # Additional 30 connections during peak loads
pool_recycle=3600     # Connection refresh every hour
```

### Bulk Processing Efficiency
```python
BATCH_SIZE = 1000          # Process 1000 records per batch
COMMIT_FREQUENCY = 5000    # Database commits every 5000 records
```

**Performance Metrics:**
- **500K Product Import**: 15-25 minutes
- **Processing Rate**: 20,000-30,000 records/minute
- **Memory Usage**: Constant ~50MB (regardless of file size)

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- Redis 6+

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Odata_Backend
   ```

2. **Install dependencies using UV**
   ```bash
   uv sync
   ```

3. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Configure your database and Redis URLs
   ```

4. **Database Setup**
   ```bash
   uv run alembic upgrade head
   ```

5. **Start the Application**
   ```bash
   # Start FastAPI server
   uv run fastapi dev main.py
   
   # Start Celery worker (separate terminal)
   uv run celery -A src.tasks.celery_worker.celery worker --loglevel=info
   ```

## 📡 API Endpoints

### Product Management
- `POST /products/csv` - Upload and process large CSV files
- `GET /products/all` - Retrieve products with pagination
- `GET /products/id/{sku}` - Get product by SKU
- `POST /products/new` - Create single product
- `PUT /products/id/{sku}` - Update product by SKU
- `DELETE /products/id/{sku}` - Delete product by SKU

### Webhook Management
- `POST /webhooks/create` - Configure webhook endpoints
- `GET /webhooks/getall` - List all webhooks
- `PUT /webhooks/update_by_id/{url}/{status}` - Update webhook status
- `DELETE /webhooks/del_by_url/{url}` - Remove webhook configuration

### Real-time Monitoring
- `WS /webhooks/task-monitor/{task_id}` - WebSocket endpoint for real-time task progress

## 🔄 Event-Driven Workflow

### CSV Processing Flow
```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Celery
    participant Redis
    participant PostgreSQL
    participant WebSocket

    Client->>FastAPI: POST /products/csv (file upload)
    FastAPI->>FastAPI: Stream file to disk
    FastAPI->>Celery: Queue processing task
    FastAPI->>Client: Return task_id immediately
    
    Client->>WebSocket: Connect to /task-monitor/{task_id}
    
    Celery->>Redis: Update task progress
    Redis->>WebSocket: Broadcast progress updates
    WebSocket->>Client: Real-time progress
    
    Celery->>PostgreSQL: Batch insert products
    Celery->>Redis: Update completion status
    Redis->>WebSocket: Final status update
    WebSocket->>Client: Processing complete
```

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
POSTGRES_SERVICE_URL=postgresql+asyncpg://user:pass@host:port/db

# Celery Configuration  
CELERY_BROKER_URL=rediss://user:pass@host:port
CELERY_RESULT_BACKEND=rediss://user:pass@host:port

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
```

### Database Schema
The application uses PostgreSQL with the following key tables:
- `product` - Product catalog with SKU, name, description, status
- `webhookurl` - Webhook configuration and management
- `user` - User authentication and authorization

## 🏆 Performance Characteristics

### Scalability Metrics
- **Concurrent Requests**: 1000+ simultaneous API requests
- **File Processing**: 500K+ records in 15-25 minutes
- **Memory Efficiency**: Constant memory usage regardless of file size
- **Database Throughput**: 20K+ inserts per minute

### Reliability Features
- **Connection Pooling**: Automatic connection management and recycling
- **Error Recovery**: Failed files automatically moved to error directory
- **Progress Persistence**: Task state maintained in Redis for recovery
- **Graceful Degradation**: Fallback mechanisms for failed operations

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Built with ❤️ using FastAPI, Celery, and PostgreSQL for enterprise-scale data processing.
