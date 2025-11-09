#!/usr/bin/env python3
"""Module implementing concurrent asynchronous database queries."""

import asyncio
import aiosqlite
from typing import List, Tuple, Any


async def async_fetch_users() -> List[Tuple[Any, ...]]:
    """Fetch all users from the database asynchronously.
    
    Returns:
        List[Tuple]: List of all user records
    """
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()


async def async_fetch_older_users() -> List[Tuple[Any, ...]]:
    """Fetch users older than 40 from the database asynchronously.
    
    Returns:
        List[Tuple]: List of user records for users over 40
    """
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            return await cursor.fetchall()


async def fetch_concurrently() -> Tuple[List[Tuple[Any, ...]], List[Tuple[Any, ...]]]:
    """Execute both fetch queries concurrently using asyncio.gather.
    
    Returns:
        Tuple[List[Tuple], List[Tuple]]: Results from both queries
            (all users, older users)
    """
    # Use gather to run both queries concurrently
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    return all_users, older_users


async def main():
    """Main async function to demonstrate concurrent query execution."""
    try:
        # Execute queries concurrently
        all_users, older_users = await fetch_concurrently()
        
        # Print results
        print("All users:")
        for user in all_users:
            print(f"  {user}")
            
        print("\nUsers over 40:")
        for user in older_users:
            print(f"  {user}")
            
    except aiosqlite.Error as e:
        print(f"Database error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())