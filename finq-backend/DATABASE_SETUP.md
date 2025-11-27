# 🗄️ Database Setup Guide

## Quick Setup for Supabase PostgreSQL

### Step 1: Install PostgreSQL Driver

```bash
cd finq-backend
source venv/bin/activate  # Activate virtual environment
pip install psycopg2-binary
```

### Step 2: Set Database URL

**Important**: Always quote the connection string in zsh/bash!

```bash
# Correct way (with quotes):
export DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres"

# Wrong way (without quotes - will cause errors):
export DATABASE_URL=postgresql://postgres:password@db.ref.supabase.co:5432/postgres
```

### Step 3: Test Connection

```bash
python -c "from sqlalchemy import create_engine; engine = create_engine('$DATABASE_URL'); conn = engine.connect(); print('✅ Connected!'); conn.close()"
```

### Step 4: Run Migrations

```bash
alembic upgrade head
```

### Step 5: Verify Tables

```bash
python -c "from app.database import SessionLocal; from sqlalchemy import inspect; db = SessionLocal(); inspector = inspect(db.bind); print('Tables:', inspector.get_table_names()); db.close()"
```

## Expected Tables

After running migrations, you should see:
- `user_profiles`
- `friends`
- `posts`
- `post_likes`
- `post_comments`
- `insights`
- `chat_sessions`
- `chat_messages`
- `alembic_version`

## Troubleshooting

### "ModuleNotFoundError: No module named 'psycopg2'"

**Solution**: Install psycopg2-binary
```bash
pip install psycopg2-binary
```

### "zsh: no matches found"

**Solution**: Quote the connection string
```bash
# Wrong:
export DATABASE_URL=postgresql://...

# Correct:
export DATABASE_URL="postgresql://..."
```

### Connection Timeout

**Solution**: 
- Check Supabase project is running
- Verify connection string is correct
- Check if IP allowlist is enabled (disable for now)

### Migration Errors

**Solution**:
```bash
# Check current migration status
alembic current

# View migration history
alembic history

# If needed, rollback and re-run
alembic downgrade -1
alembic upgrade head
```

## For Railway Deployment

When deploying to Railway, set the `DATABASE_URL` environment variable in Railway dashboard (no need to quote there, Railway handles it).

