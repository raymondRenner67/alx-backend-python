#!/usr/bin/env python3
"""Module implementing decorators for database connection and transaction handling."""

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


def transactional(func):
    """Decorator that manages database transactions.
    
    Wraps database operations in a transaction, committing on success
    and rolling back on any exception.

    Args:
        func: The function to wrap with transaction management

    Returns:
        wrapper: The wrapped function with transaction handling
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Execute the function
            result = func(conn, *args, **kwargs)
            # If successful, commit the transaction
            conn.commit()
            return result
        except Exception as e:
            # On error, rollback the transaction and re-raise
            conn.rollback()
            raise e
    return wrapper


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """Update a user's email address.
    
    Args:
        conn: Database connection (provided by decorator)
        user_id: The ID of the user to update
        new_email: The new email address
    """
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))


if __name__ == "__main__":
    # Update user's email with automatic transaction handling
    try:
        update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
        print("Email updated successfully")
    except Exception as e:
        print(f"Error updating email: {e}")