#!/bin/bash
set -e

# Wait for the database to be ready
echo "Waiting for database to be ready..."
python -c "
import time
import psycopg2
import os

host = os.getenv('POSTGRES_SERVER', 'db')
user = os.getenv('POSTGRES_USER', 'postgres')
password = os.getenv('POSTGRES_PASSWORD', 'postgres')
dbname = os.getenv('POSTGRES_DB', 'aiaudio')

while True:
    try:
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=dbname
        )
        conn.close()
        break
    except psycopg2.OperationalError:
        print('Database not ready yet. Waiting...')
        time.sleep(1)
"

echo "Database is ready!"

# Run migrations
echo "Running database migrations..."
cd /app
alembic upgrade head

# Seed initial data if needed
echo "Checking if database needs seeding..."
KEYWORD_COUNT=$(python -c "
import psycopg2
import os

host = os.getenv('POSTGRES_SERVER', 'db')
user = os.getenv('POSTGRES_USER', 'postgres')
password = os.getenv('POSTGRES_PASSWORD', 'postgres')
dbname = os.getenv('POSTGRES_DB', 'aiaudio')

conn = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    dbname=dbname
)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM keywords')
count = cur.fetchone()[0]
print(count)
cur.close()
conn.close()
")

if [ "$KEYWORD_COUNT" -eq "0" ]; then
    echo "Seeding database with initial data..."
    python /app/scripts/init_keywords.py
else
    echo "Database already has data, skipping seeding."
fi

# Start the application
echo "Starting the application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
