#!/bin/bash
# Production Database Migration Script
# Run this script to migrate the production database

set -e  # Exit on error

echo "=========================================="
echo "Phase 3 Chatbot - Production Migration"
echo "=========================================="
echo ""

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "ERROR: .env.production file not found!"
    echo "Please copy .env.production.example to .env.production and configure it."
    exit 1
fi

# Load production environment
export $(cat .env.production | grep -v '^#' | xargs)

echo "Environment: $ENVIRONMENT"
echo "Database: $DATABASE_URL"
echo ""

# Backup database first
echo "Step 1: Creating database backup..."
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${BACKUP_DATE}.sql"

# Extract database connection details
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\(.*\):.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\(.*\)?.*/\1/p' | sed 's/?.*//')

echo "Backing up to: $BACKUP_FILE"
pg_dump "$DATABASE_URL" > "backups/$BACKUP_FILE"
echo "✓ Backup created successfully"
echo ""

# Show current migration status
echo "Step 2: Checking current migration status..."
alembic current
echo ""

# Show pending migrations
echo "Step 3: Checking pending migrations..."
alembic heads
echo ""

# Confirm before proceeding
read -p "Do you want to proceed with migration? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Migration cancelled."
    exit 0
fi

# Run migrations
echo ""
echo "Step 4: Running migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Migration completed successfully!"
    echo ""
    echo "New migration status:"
    alembic current
else
    echo ""
    echo "✗ Migration failed!"
    echo ""
    echo "To rollback, run: alembic downgrade -1"
    echo "To restore from backup: psql $DATABASE_URL < backups/$BACKUP_FILE"
    exit 1
fi

# Verify migration
echo ""
echo "Step 5: Verifying migration..."
python scripts/verify_migration.py

echo ""
echo "=========================================="
echo "Migration Complete!"
echo "=========================================="
