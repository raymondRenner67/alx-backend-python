import sqlite3
import functools
from datetime import datetime

#### decorator to lof SQL queries

def log_queries(func):
    """Decorator that logs the SQL query before executing the wrapped function.

    The decorator looks for a `query` argument passed either as a keyword or
    as the first positional argument and prints it before calling the function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Prefer keyword 'query' if provided

        query = kwargs.get('query')
        # Fallback to first positional argument
        if query is None and len(args) > 0:
            query = args[0]

    print(f"[{datetime.now().isoformat()}] Executing query: {query}")
        return func(*args, **kwargs)

    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")