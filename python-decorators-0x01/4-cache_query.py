#!/usr/bin/env python3
"""Module implementing decorators for database operations with query caching."""

import time
import sqlite3
import functools


# Global cache dictionary to store query results
query_cache = {}


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


def cache_query(func):
    """Decorator that caches query results to avoid redundant database calls.
    
    The cache key is the query string. Results are stored in the global
    query_cache dictionary.
    
    Args:
        func: The function to wrap with caching functionality
        
    Returns:
        wrapper: The wrapped function that implements caching
    """
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        # Use query string as cache key
        if query in query_cache:
            print(f"Cache hit! Using cached results for query: {query}")
            return query_cache[query]
            
        # Cache miss - execute query and store results
        print(f"Cache miss! Executing query: {query}")
        results = func(conn, query, *args, **kwargs)
        query_cache[query] = results
        return results
        
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """Fetch users from database with caching.
    
    Args:
        conn: Database connection (provided by decorator)
        query: SQL query string
        
    Returns:
        list: Query results (from cache or database)
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


if __name__ == "__main__":
    # First call will cache the result
    print("First call - should hit database:")
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Retrieved {len(users)} users\n")
    
    # Second call will use the cached result
    print("Second call - should use cache:")
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Retrieved {len(users_again)} users\n")
    
    # Different query will miss cache
    print("Different query - should hit database:")
    active_users = fetch_users_with_cache(
        query="SELECT * FROM users WHERE active = 1"
    )
    print(f"Retrieved {len(active_users)} active users")