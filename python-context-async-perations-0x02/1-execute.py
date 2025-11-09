#!/usr/bin/env python3
"""Module implementing a reusable query execution context manager."""

import sqlite3


class ExecuteQuery:
    """A context manager for executing queries to find users over a specific age."""
    
    def __init__(self):
        """Initialize the context manager with the database name."""
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        """Set up database connection and execute the specific query.
        
        Returns:
            list: Query results for users over age 25
        """
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        
        # Execute the specific query for users over 25
        self.cursor.execute("SELECT * FROM users WHERE age > ?", (25,))
        return self.cursor.fetchall()
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Clean up database resources.
        
        Args:
            exc_type: Type of exception that occurred (if any)
            exc_value: Exception instance (if any)
            traceback: Traceback object (if any)
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            if exc_type is None:
                # Only commit if no exception occurred
                self.conn.commit()
            self.conn.close()


if __name__ == "__main__":
    # Demonstrate the context manager
    try:
        with ExecuteQuery() as results:
            print("Users over age 25:")
            for user in results:
                print(user)
    except sqlite3.Error as e:
        print(f"Database error: {e}")