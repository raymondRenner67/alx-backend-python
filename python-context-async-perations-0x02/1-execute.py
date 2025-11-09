#!/usr/bin/env python3
"""Module implementing a reusable query execution context manager."""

import sqlite3
from typing import Any, List, Tuple


class ExecuteQuery:
    """A context manager for executing parameterized SQL queries.
    
    This class implements the context manager protocol to handle
    database connections and query execution in a single context.
    
    Attributes:
        db_name (str): Name of the SQLite database file
        query (str): SQL query to execute
        params (tuple): Query parameters
        conn (sqlite3.Connection): The database connection
        cursor (sqlite3.Cursor): The database cursor
        results (List[Tuple]): Query results
    """
    
    def __init__(self, query: str, params: tuple = None, db_name: str = 'users.db'):
        """Initialize the context manager.
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Query parameters
            db_name (str, optional): Database file name (default: 'users.db')
        """
        self.db_name = db_name
        self.query = query
        self.params = params if params is not None else ()
        self.conn = None
        self.cursor = None
        self.results = []
    
    def __enter__(self) -> List[Tuple[Any, ...]]:
        """Set up the database connection and execute the query.
        
        Returns:
            List[Tuple]: Query results
        """
        # Establish connection and create cursor
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        
        # Execute query with parameters
        self.cursor.execute(self.query, self.params)
        self.results = self.cursor.fetchall()
        
        return self.results
    
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


def main():
    """Demonstrate usage of the ExecuteQuery context manager."""
    try:
        # Use the context manager to find users over 25
        query = "SELECT * FROM users WHERE age > ?"
        with ExecuteQuery(query, (25,)) as results:
            print("Users over 25:")
            for user in results:
                print(user)
                
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()