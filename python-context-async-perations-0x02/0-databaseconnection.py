#!/usr/bin/env python3
"""Module implementing a context manager for database connections."""

import sqlite3


class DatabaseConnection:
    """A context manager for handling SQLite database connections.
    
    This class implements the context manager protocol to ensure proper
    handling of database connections and automatic cleanup.
    
    Attributes:
        db_name (str): Name of the SQLite database file
        conn (sqlite3.Connection): The database connection object
    """
    
    def __init__(self, db_name='users.db'):
        """Initialize the context manager.
        
        Args:
            db_name (str): Name of the database file (default: 'users.db')
        """
        self.db_name = db_name
        self.conn = None
    
    def __enter__(self):
        """Establish database connection when entering context.
        
        Returns:
            sqlite3.Connection: The active database connection
        """
        self.conn = sqlite3.connect(self.db_name)
        return self.conn
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Close database connection when exiting context.
        
        Args:
            exc_type: Type of exception that occurred (if any)
            exc_value: Exception instance (if any)
            traceback: Traceback object (if any)
        """
        if self.conn:
            self.conn.close()
            self.conn = None


def main():
    """Demonstrate usage of the DatabaseConnection context manager."""
    try:
        # Use the context manager with 'with' statement
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            
            print("Users in database:")
            for user in results:
                print(user)
                
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()