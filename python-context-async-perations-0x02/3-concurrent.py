#!/usr/bin/env python3
"""Module implementing concurrent asynchronous database queries."""

import asyncio
import aiosqlite


async def async_fetch_users():
    """Fetch all users from the database asynchronously.
    
    Returns:
        list: All user records
    """
    async with aiosqlite.connect('users.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()


async def async_fetch_older_users():
    """Fetch users older than 40 from the database asynchronously.
    
    Returns:
        list: User records where age > 40
    """
    async with aiosqlite.connect('users.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            return await cursor.fetchall()


async def fetch_concurrently():
    """Execute both fetch queries concurrently using asyncio.gather.
    
    Returns:
        tuple: Contains results from both queries (all_users, older_users)
    """
    return await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )


def display_user(user):
    """Helper function to format and display a user record."""
    return (f"User(id={user['id']}, name='{user['name']}', "
            f"email='{user['email']}', age={user['age']})")


async def main():
    """Main async function that runs and displays results of concurrent queries."""
    try:
        # Execute both queries concurrently
        all_users, older_users = await fetch_concurrently()

        # Display all users
        print("\nAll users:")
        print("-" * 40)
        for user in all_users:
            print(display_user(user))

        # Display older users
        print("\nUsers over 40:")
        print("-" * 40)
        for user in older_users:
            print(display_user(user))

    except aiosqlite.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())