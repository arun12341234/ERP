# Multi-Tenant ERP Platform

A **minimal, production-ready** full-stack scaffold for building cloud-based ERP systems. Built with React + TypeScript (frontend) and FastAPI + Python (backend).

## Features

- ✅ **Authentication**: JWT-based auth with login/register (toggleable)
- ✅ **Multi-tenant**: Optional tenant isolation via `.env` flag
- ✅ **CRUD Scaffold**: Complete Item resource with list/detail/create/edit
- ✅ **Role-based Access**: Admin, User, Viewer roles
- ✅ **Form Validation**: React Hook Form + Zod
- ✅ **API Client**: Axios wrapper with automatic token injection
- ✅ **Database**: SQLite (dev) / PostgreSQL (prod) with SQLAlchemy
- ✅ **Docker Ready**: Full docker-compose setup
- ✅ **Resource Generator**: Script to scaffold new resources
- ✅ **Minimal Dependencies**: Conservative, mainstream packages only

## Quick Start (10 minutes)

### Prerequisites

- Docker & Docker Compose
- Make (optional, for convenience commands)

### 1. Clone and Setup

```bash
# Clone the repo (if not already done)
cd ERP

# Copy environment files
cp backend/.env.template backend/.env
cp frontend/.env.template frontend/.env

# (Optional) Edit backend/.env to change admin credentials
```

### 2. Start the Application

```bash
# Option A: Using Make
make dev

# Option B: Using Docker Compose directly
docker-compose up --build
```

This will start:
- **Backend API**: http://localhost:8000 (docs at http://localhost:8000/docs)
- **Frontend**: http://localhost:5173
- **Database**: PostgreSQL on port 5432

### 3. Seed Database (Optional)

In a new terminal:

```bash
make seed

# Or manually:
docker-compose exec backend python scripts/seed_db.py
```

**Default credentials:**
- Admin: `admin@example.com` / `admin123`
- User: `user@example.com` / `user123`

### 4. Access the Application

1. Open http://localhost:5173
2. Click "Sign in" and use the credentials above
3. Explore the Dashboard and Items CRUD

## Project Structure

```
ERP/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── core/              # Config, database, security
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # API endpoints
│   │   └── main.py            # FastAPI app
│   ├── scripts/
│   │   ├── seed_db.py         # Database seeding
│   │   └── generate_resource.py  # Resource generator
│   ├── tests/                 # Pytest tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.template
│
├── frontend/                   # React TypeScript frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── lib/               # API client
│   │   ├── hooks/             # React hooks
│   │   ├── App.tsx            # Main app with routing
│   │   └── main.tsx           # Entry point
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── .env.template
│
├── docker-compose.yml
├── Makefile
└── README.md
```

## Available Commands

```bash
make dev          # Start development environment
make build        # Build all containers
make up           # Start services in background
make down         # Stop all services
make logs         # View logs
make seed         # Seed database with initial data
make test         # Run tests (backend + frontend)
make clean        # Clean up containers and volumes
make generate     # Generate new resource (usage: make generate name=Product)
```

## Configuration

### Backend (.env)

```env
# Database
DATABASE_URL=sqlite:///./erp.db
# For Postgres: DATABASE_URL=postgresql://user:password@localhost:5432/erp_db

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Features (toggleable)
ENABLE_AUTH=true
ENABLE_TENANCY=false
ENABLE_SUBSCRIPTIONS=false

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

## How to Extend

### 1. Add a New Resource

Use the generator script to create a complete CRUD resource:

```bash
# Generate Product resource
make generate name=Product

# Or manually:
docker-compose exec backend python scripts/generate_resource.py Product
```

This creates:
- Backend: `models/product.py`, `schemas/product.py`, `routers/products.py`
- Frontend: `pages/ProductList.tsx` (you can create Detail/Form manually or copy from Item)

**Then:**

1. Add router to `backend/app/main.py`:
   ```python
   from app.routers import products
   app.include_router(products.router, prefix=settings.API_V1_STR)
   ```

2. Add routes to `frontend/src/App.tsx`:
   ```tsx
   <Route path="/products" element={<ProductList />} />
   <Route path="/products/:id" element={<ProductDetail />} />
   <Route path="/products/new" element={<ProductForm />} />
   <Route path="/products/:id/edit" element={<ProductForm />} />
   ```

3. Restart the backend:
   ```bash
   docker-compose restart backend
   ```

### 2. Enable Multi-Tenancy

1. Edit `backend/.env`:
   ```env
   ENABLE_TENANCY=true
   ```

2. Restart services:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

3. Multi-tenant fields (`tenant_id`) are now active in User and Item models
4. Tenant filtering is automatically applied in routers

**Note:** You'll need to create a Tenant management UI and seed tenants manually.

### 3. Switch to PostgreSQL

1. Edit `backend/.env`:
   ```env
   DATABASE_URL=postgresql://erp_user:erp_pass@db:5432/erp_db
   ```

2. Restart services:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

Database tables will be created automatically on startup.

### 4. Enable Subscriptions

1. Edit `backend/.env`:
   ```env
   ENABLE_SUBSCRIPTIONS=true
   ```

2. Implement subscription models and payment integration:
   - Create `models/subscription.py`
   - Create `routers/subscriptions.py`
   - Integrate with Stripe/Razorpay

3. Add subscription checks to protected endpoints

### 5. Add Migrations (Optional)

For production, use Alembic for database migrations:

```bash
# Install Alembic
docker-compose exec backend pip install alembic

# Initialize
docker-compose exec backend alembic init alembic

# Create migration
docker-compose exec backend alembic revision --autogenerate -m "Add new table"

# Apply migration
docker-compose exec backend alembic upgrade head
```

### 6. Add Tests

**Backend:**

```bash
# Run existing tests
docker-compose exec backend pytest tests/

# Add new test file: backend/tests/test_items.py
```

**Frontend:**

```bash
# Install dependencies locally
cd frontend && npm install

# Run tests
npm test
```

### 7. Deploy to Production

**Option A: Docker**

```bash
# Build for production
docker-compose -f docker-compose.prod.yml up -d

# Use environment-specific .env files
# Set SECRET_KEY to a strong random value
# Use PostgreSQL DATABASE_URL
# Set CORS_ORIGINS to your domain
```

**Option B: Cloud Platforms**

- **Backend**: Deploy to Heroku, Railway, Render, AWS ECS
- **Frontend**: Deploy to Vercel, Netlify, Cloudflare Pages
- **Database**: Use managed PostgreSQL (RDS, Supabase, Neon)

**Production Checklist:**
- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set `ADMIN_PASSWORD` to a secure value
- [ ] Update `CORS_ORIGINS` to your domain
- [ ] Enable HTTPS
- [ ] Set up monitoring and logging
- [ ] Configure backups
- [ ] Run migrations properly
- [ ] Use environment variables (never commit `.env`)

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example API Calls

```bash
# Health check
curl http://localhost:8000/api/v1/healthz

# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -F "username=admin@example.com" \
  -F "password=admin123"

# List items (requires token)
curl http://localhost:8000/api/v1/items \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation
- **Python-JOSE** - JWT tokens
- **Passlib** - Password hashing
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router v6** - Routing
- **Tailwind CSS** - Styling
- **React Hook Form** - Form management
- **Zod** - Schema validation
- **Axios** - HTTP client

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **PostgreSQL** - Production database
- **SQLite** - Development database

## Security

- ✅ Password hashing with bcrypt
- ✅ JWT token authentication
- ✅ Token expiry and rotation
- ✅ CORS protection
- ✅ Input validation (Pydantic + Zod)
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ XSS protection (React auto-escaping)

**TODO (for production):**
- Add rate limiting
- Add CSRF protection
- Implement refresh tokens
- Add 2FA/MFA
- Set up SSL/TLS
- Add audit logging

## Testing

```bash
# Backend tests
make test

# Or manually:
docker-compose exec backend pytest tests/ -v

# Frontend tests (requires local setup)
cd frontend
npm test
```

## Troubleshooting

### Port already in use
```bash
# Change ports in docker-compose.yml
# Or stop conflicting services
```

### Database connection errors
```bash
# Check DATABASE_URL in backend/.env
# Ensure db service is healthy:
docker-compose ps
```

### Frontend can't reach backend
```bash
# Check VITE_API_URL in frontend/.env
# Ensure backend is running:
curl http://localhost:8000/api/v1/healthz
```

### Permission errors in Docker
```bash
# On Linux, you may need to fix file permissions:
sudo chown -R $USER:$USER .
```

## Contributing

This is a scaffold/template project. Fork and customize for your needs.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use this scaffold for any project.

## Support

- **Documentation**: See this README
- **API Docs**: http://localhost:8000/docs
- **Issues**: Open a GitHub issue

---

**Built with ❤️ for minimal complexity and maximum extensibility.**
