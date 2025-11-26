# 🚀 Phase 1 Setup Guide

## What We've Built So Far

✅ **Project Structure**: Complete FastAPI project structure created
✅ **Configuration**: Environment-based configuration system
✅ **Database Models**: Insight model for storing chat analysis
✅ **API Endpoints**: Placeholder endpoints for financial and chat APIs
✅ **Services**: DataSourceManager service structure (needs implementation)
✅ **Testing**: Basic test infrastructure

## Next Steps

### 1. Set Up Database (Required)

You have three options:

#### Option A: Supabase (Recommended for Quick Start)
1. Go to [supabase.com](https://supabase.com)
2. Create a free account
3. Create a new project
4. Copy the connection string from Settings → Database
5. Format: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`

#### Option B: Local PostgreSQL
1. Install PostgreSQL locally
2. Create database: `createdb finq_db`
3. Connection string: `postgresql://user:password@localhost:5432/finq_db`

#### Option C: SQLite (Development Only)
For quick testing, you can use SQLite:
- Update `DATABASE_URL` in `.env` to: `sqlite:///./finq.db`

### 2. Configure Environment

```bash
cd finq-backend
cp .env.example .env
```

Edit `.env` with your values:
- `DATABASE_URL`: Your PostgreSQL connection string
- `GEMINI_API_KEY`: Your Google Generative AI API key
- `FRED_API_KEY`: Your FRED API key

### 3. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Set Up Database Migrations

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Create insights table"

# Apply migration
alembic upgrade head
```

### 5. Test the API

```bash
# Run the API
python -m app.main

# Or with uvicorn
uvicorn app.main:app --reload
```

Visit:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

### 6. Run Tests

```bash
pytest
```

## Current Status

### ✅ Completed
- [x] FastAPI project structure
- [x] Configuration management
- [x] Database models (Insight)
- [x] API endpoint structure
- [x] Service layer structure
- [x] Basic tests

### 🚧 In Progress
- [ ] Database setup and migrations
- [ ] DataSourceManager full implementation
- [ ] Financial endpoints implementation
- [ ] Chat API implementation

### 📋 Next Tasks
1. **Complete DataSourceManager**: Finish migrating all methods from Streamlit
2. **Implement Financial Endpoints**: Connect endpoints to DataSourceManager
3. **Migrate FinancialAnalyzer**: Move AI analysis logic to service
4. **Create Chat API**: Implement chat endpoints with database persistence
5. **Integration Testing**: Test with Streamlit app

## Troubleshooting

### Import Errors
If you get import errors, make sure you're in the `finq-backend` directory and have activated the virtual environment.

### Database Connection Errors
- Check your `DATABASE_URL` in `.env`
- Ensure PostgreSQL is running (if using local)
- Verify credentials are correct

### API Key Errors
- Ensure all API keys are set in `.env`
- Check that keys are valid and have proper permissions

## Getting Help

- Check the [Phase 1 Implementation Plan](../docs/architecture/PHASE1_IMPLEMENTATION_PLAN.md)
- Review [Migration Assessment](../docs/architecture/MIGRATION_ASSESSMENT.md)
- See [README.md](README.md) for more details

---

**Remember**: Quality over speed. Take time to understand each component before moving to the next.


