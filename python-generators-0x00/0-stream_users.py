#!/usr/bin/env python3
"""Module that uses a generator to fetch rows from a MySQL database."""

import os
import mysql.connector


def stream_users():
    """Generator function that yields one row at a time from user_data table."""
    # Database configuration
    config = {
        'host': os.getenv('MYSQL_HOST', '127.0.0.1'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': 'ALX_prodev',
        'port': int(os.getenv('MYSQL_PORT', 3306))
    }

    try:
        # Connect to the database
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)  # Returns rows as dictionaries

        # Execute the query
        cursor.execute('SELECT user_id, name, email, age FROM user_data')

        # Use yield to return one row at a time
        for row in cursor:
            yield row

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        yield {}  # Return empty dict in case of error
    finally:
        # Clean up resources
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()