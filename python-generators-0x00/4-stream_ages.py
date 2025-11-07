#!/usr/bin/env python3
"""Module that implements memory-efficient age aggregation using generators."""

import seed


def stream_user_ages():
    """Generator that yields user ages one by one.
    
    Returns:
        generator: Yields one age at a time
    """
    connection = seed.connect_to_prodev()
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Using cursor as iterator to avoid loading all records at once
        cursor.execute("SELECT age FROM user_data")
        
        # Yield ages one by one
        for row in cursor:
            yield row['age']
            
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


def calculate_average_age():
    """Calculate average age using the age generator.
    
    Returns:
        float: The average age of all users
    """
    total_age = 0
    count = 0
    
    # Use the generator to process ages one at a time
    for age in stream_user_ages():
        total_age += int(age)
        count += 1
    
    # Calculate and format average
    average_age = total_age / count if count > 0 else 0
    print(f"Average age of users: {average_age:.2f}")


if __name__ == "__main__":
    calculate_average_age()