#!/bin/bash

# Check if uv is installed
if ! command -v uv &> /dev/null
then
    echo "uv could not be found. Please install it first."
    exit 1
fi

echo "Running maintenance on Miyori..."
# Backup database
BACKUP_DIR="/mnt/e/_projects/Miyori_Backups"
DATE=$(date +%Y%m%d)
BACKUP_FILE="memory.db$DATE"

if [ -f "./memory.db" ]; then
    echo "Backing up memory.db to $BACKUP_DIR/$BACKUP_FILE..."
    mkdir -p "$BACKUP_DIR"
    cp "./memory.db" "$BACKUP_DIR/$BACKUP_FILE"
else
    echo "Warning: ./memory.db not found, skipping backup."
fi

# Using 'uv run' handles venv activation automatically
uv run python -m miyori.utils.run_consolidation
