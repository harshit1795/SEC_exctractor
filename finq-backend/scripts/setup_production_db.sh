#!/bin/bash

# Production Database Setup Script
# This script helps set up the production database with Supabase

set -e  # Exit on error

echo "🚀 Setting up Production Database..."

# Check if DATABASE_URL is provided
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL environment variable is not set"
    echo ""
    echo "Usage:"
    echo "  export DATABASE_URL='postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres'"
    echo "  ./scripts/setup_production_db.sh"
    echo ""
    echo "Or run directly:"
    echo "  DATABASE_URL='your-connection-string' ./scripts/setup_production_db.sh"
    exit 1
fi

# Test database connection
echo "📡 Testing database connection..."
python -c "
from sqlalchemy import create_engine
import sys

try:
    engine = create_engine('$DATABASE_URL')
    conn = engine.connect()
    print('✅ Database connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
" || exit 1

# Run migrations
echo ""
echo "📦 Running database migrations..."
alembic upgrade head

echo ""
echo "✅ Database setup complete!"
echo ""
echo "Next steps:"
echo "1. Verify tables were created in Supabase dashboard"
echo "2. Deploy backend to Railway with this DATABASE_URL"
echo "3. Continue with frontend deployment"

