#!/usr/bin/env python3
"""Module implementing a decorator for automatic database connection handling."""

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
            # and any additional args/kwargs
            return func(conn, *args, **kwargs)
        finally:
            # Ensure connection is always closed, even if an error occurs
            conn.close()
    return wrapper


@with_db_connection
def get_user_by_id(conn, user_id):
    """Fetch a user from the database by their ID.
    
    Args:
        conn: Database connection (provided by decorator)
        user_id: The ID of the user to fetch
        
    Returns:
        tuple: User record or None if not found
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()
    


if __name__ == "__main__":
    # Fetch user by ID with automatic connection handling
    user = get_user_by_id(user_id=1)
    print(user)