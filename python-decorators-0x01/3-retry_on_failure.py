#!/usr/bin/env python3
"""Module implementing decorators for database operations with retry mechanism."""

import time
import sqlite3
import functools


def with_db_connection(func):
    """Decorator that handles database connection lifecycle.

    Args:
        func: The function to wrap that requires a database connection

    Returns:
        wrapper: The wrapped function that handles db connection automatically
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Establish database connection
        conn = sqlite3.connect('users.db')
        try:
            # Call the wrapped function with the connection as first argument
            return func(conn, *args, **kwargs)
        finally:
            # Ensure connection is always closed, even if an error occurs
            conn.close()
    return wrapper


def retry_on_failure(retries=3, delay=2):
    """Decorator that retries a database operation on failure.
    
    Args:
        retries (int): Number of retry attempts (default: 3)
        delay (int): Delay in seconds between retries (default: 2)
    
    Returns:
        decorator: A decorator that implements the retry logic
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            # Try the operation up to retries + 1 times
            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                except sqlite3.Error as e:
                    last_error = e
                    if attempt < retries:
                        print(f"Attempt {attempt + 1} failed: {str(e)}")
                        print(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                    continue
            # If we get here, all attempts failed
            raise last_error
        return wrapper
    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """Fetch all users from the database with retry mechanism.
    
    Args:
        conn: Database connection (provided by decorator)
    
    Returns:
        list: List of user records
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


if __name__ == "__main__":
    try:
        # Attempt to fetch users with automatic retry on failure
        users = fetch_users_with_retry()
        print("Users retrieved successfully:")
        for user in users:
            print(user)
    except sqlite3.Error as e:
        print(f"Failed to fetch users after all retries: {e}")