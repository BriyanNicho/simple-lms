import os
import time
import psycopg2

DATABASE = os.getenv('POSTGRES_DB', 'simple_lms')
USER = os.getenv('POSTGRES_USER', 'simple_user')
PASSWORD = os.getenv('POSTGRES_PASSWORD', 'simple_password')
HOST = os.getenv('DB_HOST', 'simple_db')
PORT = os.getenv('DB_PORT', '5432')

while True:
    try:
        conn = psycopg2.connect(
            dbname=DATABASE,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
        )
        conn.close()
        break
    except psycopg2.OperationalError:
        print("Waiting for PostgreSQL...")
        time.sleep(1)

print("PostgreSQL is ready.")
