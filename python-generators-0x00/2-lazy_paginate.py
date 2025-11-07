#!/usr/bin/env python3
"""Module that implements lazy pagination using generators."""

import seed


def paginate_users(page_size, offset):
    """Fetch a page of users from the database.
    
    Args:
        page_size (int): Number of records per page
        offset (int): Starting position for fetching records
        
    Returns:
        list: A list of user records for the requested page
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_paginate(page_size):
    """Generator that lazily loads pages of user data.
    
    Args:
        page_size (int): Number of records to fetch per page
        
    Returns:
        generator: Yields one page of users at a time
    """
    offset = 0
    while True:
        # Get the next page of results
        page = paginate_users(page_size, offset)
        
        # If no more results, stop iteration
        if not page:
            return None
            
        # Yield the current page and update offset for next iteration
        yield page
        offset += page_size