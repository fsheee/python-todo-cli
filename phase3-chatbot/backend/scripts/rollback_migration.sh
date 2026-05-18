#!/bin/bash
# Rollback Database Migration Script

set -e

echo "=========================================="
echo "Database Migration Rollback"
echo "=========================================="
echo ""

# Load production environment
if [ ! -f ".env.production" ]; then
    echo "ERROR: .env.production file not found!"
    exit 1
fi

export $(cat .env.production | grep -v '^#' | xargs)

echo "Current migration status:"
alembic current
echo ""

read -p "How many migrations to rollback? (default: 1): " STEPS
STEPS=${STEPS:-1}

echo ""
echo "WARNING: This will rollback the last $STEPS migration(s)!"
read -p "Are you sure? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Rollback cancelled."
    exit 0
fi

echo ""
echo "Rolling back $STEPS migration(s)..."

for ((i=1; i<=STEPS; i++)); do
    echo "Rollback step $i..."
    alembic downgrade -1
done

echo ""
echo "New migration status:"
alembic current

echo ""
echo "✓ Rollback complete!"
