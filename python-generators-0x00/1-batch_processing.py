#!/usr/bin/env python3
"""Module that implements batch processing of user data using generators."""

import os
import mysql.connector


def stream_users_in_batches(batch_size):
    """Generator that yields batches of users from the database.
    
    Args:
        batch_size (int): Number of records to fetch in each batch
    
    Yields:
        list: A batch of user records
    """
    config = {
        'host': os.getenv('MYSQL_HOST', '127.0.0.1'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': 'ALX_prodev',
        'port': int(os.getenv('MYSQL_PORT', 3306))
    }

    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)

        # Execute query with limit and offset
        offset = 0
        while True:
            cursor.execute(
                'SELECT user_id, name, email, age FROM user_data LIMIT %s OFFSET %s',
                (batch_size, offset)
            )
            batch = cursor.fetchall()
            
            if not batch:  # No more records
                break
                
            yield batch
            offset += batch_size

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


def batch_processing(batch_size):
    """Process users in batches and filter those over 25 years old.
    
    Args:
        batch_size (int): Size of each batch to process
    """
    # Get batches of users and process them
    for batch in stream_users_in_batches(batch_size):
        # Filter users over 25 and yield them one by one
        for user in batch:
            if user['age'] > 25:
                print(user)
                print()  # Add blank line between users