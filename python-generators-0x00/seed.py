#!/usr/bin/env python3
"""
seed.py

Functions:
- connect_db(): connect to MySQL server (no specific database)
- create_database(conn): create ALX_prodev if not exists
- connect_to_prodev(): connect specifically to ALX_prodev
- create_table(conn): create user_data table if not exists
- insert_data(conn, csv_path): read CSV and insert rows (idempotent)
- stream_user_rows(conn): generator that yields rows one by one
"""

import os
import csv
import uuid
import mysql.connector
from mysql.connector import errorcode

# Read MySQL connection info from environment variables (or defaults)
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")

DB_NAME = "ALX_prodev"
TABLE_NAME = "user_data"

def connect_db():
    """
    Connect to MySQL server (not a database) and return connection object.
    Uses env vars MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_PORT.
    """
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            port=MYSQL_PORT,
            autocommit=True
        )
        return conn
    except mysql.connector.Error as err:
        print("Error connecting to MySQL:", err)
        return None

def create_database(connection):
    """
    Create the ALX_prodev database if it does not exist.
    """
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
        # Set default character set and collation (optional but good)
        cursor.execute(f"ALTER DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print(f"Database {DB_NAME} created or already exists.")
    except mysql.connector.Error as err:
        print("Failed creating database:", err)
    finally:
        cursor.close()

def connect_to_prodev():
    """
    Connect to the ALX_prodev database and return connection.
    """
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=DB_NAME,
            port=MYSQL_PORT,
            autocommit=True
        )
        return conn
    except mysql.connector.Error as err:
        print("Error connecting to ALX_prodev:", err)
        return None

def create_table(connection):
    """
    Create user_data table if not exists with the columns:
    - user_id CHAR(36) PRIMARY KEY
    - name VARCHAR(255) NOT NULL
    - email VARCHAR(255) NOT NULL
    - age DECIMAL(5,0) NOT NULL
    """
    cursor = connection.cursor()
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        user_id CHAR(36) NOT NULL,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL(5,0) NOT NULL,
        PRIMARY KEY (user_id)
    ) ENGINE=InnoDB;
    """
    try:
        cursor.execute(create_table_sql)
        # Ensure an index on email if you want fast email lookups (optional)
        # Create index if it doesn't exist (checking first to avoid errors)
        cursor.execute(f"SHOW INDEX FROM {TABLE_NAME} WHERE Key_name = 'idx_{TABLE_NAME}_email';")
        if not cursor.fetchone():
            cursor.execute(f"CREATE INDEX idx_{TABLE_NAME}_email ON {TABLE_NAME} (email);")
        print(f"Table {TABLE_NAME} created successfully")
    except mysql.connector.Error as err:
        print("Error creating table:", err)
    finally:
        cursor.close()

def insert_data(connection, csv_path):
    """
    Insert records from csv_path into the user_data table.
    This function is idempotent: it won't create duplicate PKs.
    The CSV is expected to have columns: user_id,name,email,age
    """
    inserted = 0
    skipped = 0
    cursor = connection.cursor()
    # Uses ON DUPLICATE KEY UPDATE to avoid duplicate primary key inserts
    insert_sql = f"""
    INSERT INTO {TABLE_NAME} (user_id, name, email, age)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE user_id = user_id;
    """
    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Always generate a new UUID since our CSV doesn't have user_id
                uid = str(uuid.uuid4())
                name = row.get('name', '').strip().strip('"')  # Remove quotes if present
                email = row.get('email', '').strip().strip('"')  # Remove quotes if present
                age_raw = row.get('age', '').strip().strip('"')  # Remove quotes if present
                # Convert age to int-like decimal; fallback to 0 if invalid
                try:
                    age = int(float(age_raw))
                except Exception:
                    age = 0

                try:
                    cursor.execute(insert_sql, (uid, name, email, age))
                    inserted += 1
                except mysql.connector.Error as err:
                    print(f"Error inserting row {uid}: {err}")
                    skipped += 1
        print(f"Inserted {inserted} rows, skipped {skipped} rows.")
    except FileNotFoundError:
        print(f"CSV file not found: {csv_path}")
    finally:
        cursor.close()

def stream_user_rows(connection):
    """
    Generator that yields rows from user_data one by one.
    Use like: for row in stream_user_rows(conn): ...
    This avoids loading all rows into memory at once.
    """
    cursor = connection.cursor(dictionary=True)  # dictionary=True returns dicts (optional)
    try:
        cursor.execute(f"SELECT user_id, name, email, age FROM {TABLE_NAME};")
        # Fetch row by row
        row = cursor.fetchone()
        while row:
            yield row
            row = cursor.fetchone()
    finally:
        cursor.close()

# OPTIONAL: helper main for quick manual runs
if __name__ == "__main__":
    conn = connect_db()
    if not conn:
        print("Could not connect to MySQL server. Exiting.")
        exit(1)
    create_database(conn)
    conn.close()
    conn2 = connect_to_prodev()
    if not conn2:
        print("Could not connect to ALX_prodev database. Exiting.")
        exit(1)
    create_table(conn2)
    # Use absolute path to CSV file
    csv_path = os.path.join(os.path.dirname(__file__), "user_data.csv")
    insert_data(conn2, csv_path)
    # Example: streaming first 5 rows
    gen = stream_user_rows(conn2)
    for i, r in enumerate(gen):
        if i >= 5:
            break
        print(r)
    conn2.close()
