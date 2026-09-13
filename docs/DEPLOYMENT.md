# Deployment Guide

Step-by-step instructions for deploying the AI-Powered Inventory Management System.

---

## 1. Prerequisites

### System Requirements
| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 4 GB | 8 GB+ |
| CPU | 2 cores | 4+ cores |
| Disk | 10 GB | 20 GB+ |
| OS | Linux, macOS, Windows | Linux (Ubuntu 22.04+) |

### Software Requirements
| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend build |
| PostgreSQL | 15+ | Database |
| Docker | 24+ | Containerized deployment (optional) |
| Docker Compose | 2.20+ | Multi-container orchestration (optional) |

### Verify Installations
```bash
python --version    # Should show 3.11+
node --version      # Should show 18+
psql --version      # Should show 15+
docker --version    # Should show 24+
docker compose version  # Should show 2.20+
```

---

## 2. Docker Deployment (Recommended)

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd Project2

# Start all services
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Services Started
| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 8000 | http://localhost:8000 |
| Swagger Docs | 8000 | http://localhost:8000/docs |
| ReDoc Docs | 8000 | http://localhost:8000/redoc |
| PostgreSQL | 5432 | localhost:5432 |

### Docker Compose Services

#### PostgreSQL Database
```yaml
postgres:
  image: postgres:15
  ports: "5432:5432"
  environment:
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
    POSTGRES_DB: inventory_db
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

#### FastAPI Backend
```yaml
backend:
  build: ./backend
  ports: "8000:8000"
  environment:
    DATABASE_URL: postgresql://postgres:postgres@postgres:5432/inventory_db
  depends_on:
    postgres: condition: service_healthy
  volumes:
    - ./backend:/app
    - model_data:/app/models
```

#### React Frontend
```yaml
frontend:
  build: ./frontend
  ports: "3000:3000"
  environment:
    REACT_APP_API_URL: http://localhost:8000/api
  depends_on:
    - backend
```

### Useful Docker Commands
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v

# Rebuild a single service
docker-compose up --build backend

# View service logs
docker-compose logs backend
docker-compose logs postgres

# Enter a running container
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres -d inventory_db
```

---

## 3. Manual Deployment

### Step 1: Set Up PostgreSQL

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE inventory_db;

# Verify
\l

# Exit
\q
```

### Step 2: Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy example environment file
cp ../.env.example .env

# Edit .env with your settings
```

**Required Environment Variables:**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/inventory_db
SECRET_KEY=your-super-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
```

### Step 4: Start Backend Server

```bash
cd backend

# Development (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 5: Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Development
npm start

# Production build
npm run build
```

### Step 6: Serve Frontend (Production)

For production, serve the built frontend with a reverse proxy:

```nginx
# nginx.conf example
server {
    listen 80;

    location / {
        root /app/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 4. Environment Variables

### Backend Variables

| Variable | Default | Description | Security |
|----------|---------|-------------|----------|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/inventory_db` | PostgreSQL connection string | Required |
| `SECRET_KEY` | `your-secret-key-change-in-production` | JWT signing key (min 32 chars) | **Must change in production** |
| `ALGORITHM` | `HS256` | JWT algorithm | Default OK |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiration time | Adjust as needed |
| `API_HOST` | `0.0.0.0` | API bind address | Default OK |
| `API_PORT` | `8000` | API port | Default OK |
| `DEBUG` | `true` | Enable debug logging | **Set to false in production** |

### Frontend Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | `http://localhost:8000/api` | Backend API base URL |

---

## 5. Database Setup

### Automatic Schema Creation
The database schema is automatically created on application startup:
```python
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
```

### Database Tables
| Table | Description |
|-------|-------------|
| `users` | User accounts and authentication |
| `categories` | Product categories |
| `suppliers` | Supplier information |
| `products` | Product catalog |
| `sales` | Sales transactions |
| `inventory_transactions` | Stock movements (inbound/outbound/adjustment) |
| `forecasts` | Generated forecast data |
| `model_results` | ML model training results |
| `alerts` | System alerts |
| `dataset_uploads` | Uploaded dataset tracking |

### Manual Schema Creation (Optional)
```bash
# Connect to database
psql -U postgres -d inventory_db

# The application handles table creation automatically
# No manual SQL needed
```

### Database Backup
```bash
# Backup
pg_dump -U postgres inventory_db > backup.sql

# Restore
psql -U postgres inventory_db < backup.sql

# Docker backup
docker-compose exec postgres pg_dump -U postgres inventory_db > backup.sql

# Docker restore
docker-compose exec -T postgres psql -U postgres inventory_db < backup.sql
```

---

## 6. Production Considerations

### Security

#### Change Default Credentials
```env
# NEVER use these in production
SECRET_KEY=change-this-to-a-random-32-char-string
POSTGRES_PASSWORD=change-this-password
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### CORS Configuration
The default CORS configuration allows all origins (`*`). For production:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

#### HTTPS
Always use HTTPS in production. Configure with:
- Nginx/Caddy reverse proxy with SSL termination
- AWS ALB with ACM certificates
- Cloudflare tunnel

### Performance

#### Database Connection Pooling
SQLAlchemy is configured with `pool_pre_ping=True` for connection health checks. For high traffic:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)
```

#### Uvicorn Workers
```bash
# Run with multiple workers (recommended: 2-4 x CPU cores)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Caching
Consider adding Redis for:
- Session caching
- Dashboard data caching
- Forecast result caching

### Monitoring

#### Health Check
```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

#### Logging
- Backend uses Python's `logging` module
- Set `DEBUG=false` in production to reduce log verbosity
- Consider structured logging (JSON format) for log aggregation

#### Metrics
- Monitor API response times
- Track ML model prediction accuracy over time
- Set up alerts for high error rates

### Scaling

#### Horizontal Scaling
```bash
# Multiple backend instances behind a load balancer
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
```

#### Database Scaling
- Read replicas for dashboard queries
- Connection pooling with PgBouncer
- Partitioning for large sales tables

#### ML Model Scaling
- Model training can be offloaded to a background worker (Celery/RQ)
- Models can be served via TensorFlow Serving for LSTM
- Batch predictions for large product catalogs

### Data Backup Strategy

| Frequency | Method | Retention |
|-----------|--------|-----------|
| Daily | pg_dump automated | 7 days |
| Weekly | Full backup + WAL | 4 weeks |
| Monthly | Offsite backup | 12 months |

---

## 7. Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `Connection refused` on PostgreSQL | Database not running | Start PostgreSQL service |
| `JWT decode error` | Wrong SECRET_KEY | Ensure consistent SECRET_KEY |
| `ModuleNotFoundError` | Missing dependencies | Run `pip install -r requirements.txt` |
| `CORS error` in browser | Backend not accessible | Check backend is running on port 8000 |
| `ECONNREFUSED` in frontend | API URL wrong | Check `REACT_APP_API_URL` |
| `password authentication failed` | Wrong DB credentials | Verify DATABASE_URL matches PostgreSQL |

### Viewing Logs
```bash
# Docker
docker-compose logs -f backend
docker-compose logs -f postgres

# Manual (check terminal output)
# Backend logs are printed to stdout
```

### Resetting the System
```bash
# Full reset (Docker)
docker-compose down -v
docker-compose up --build

# Manual reset
psql -U postgres -c "DROP DATABASE inventory_db;"
psql -U postgres -c "CREATE DATABASE inventory_db;"
# Restart backend
```
