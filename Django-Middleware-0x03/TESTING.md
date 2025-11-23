# Testing Guide for Messaging App API

This guide provides step-by-step instructions for testing the Messaging App API endpoints.

## Server Status

The development server is currently running at: `http://127.0.0.1:8000/`

## Step 1: Access the API Root

Navigate to: `http://127.0.0.1:8000/api/`

You should see the browsable API with links to all available endpoints.

## Step 2: Create Users (via Django Admin)

1. Go to: `http://127.0.0.1:8000/admin/`
2. Log in with your superuser credentials (created during setup)
3. Click on "Users" and create new users with different roles:
   - User 1: First Name: "John", Last Name: "Doe", Email: "john@example.com", Role: "host"
   - User 2: First Name: "Jane", Last Name: "Smith", Email: "jane@example.com", Role: "guest"
   - User 3: First Name: "Admin", Last Name: "User", Email: "admin@example.com", Role: "admin"

Note the UUID of each user - you'll need these for creating conversations and messages.

## Step 3: List All Users

Navigate to: `http://127.0.0.1:8000/api/users/`

You should see all created users with their details in JSON format.

## Step 4: Create a Conversation

1. Go to: `http://127.0.0.1:8000/api/conversations/`
2. Scroll to the bottom and use the form or raw data section
3. In the form, enter:
   ```json
   {
     "participant_ids": ["<user1_uuid>", "<user2_uuid>"]
   }
   ```
4. Click "POST" button
5. A new conversation should be created with those participants

## Step 5: List All Conversations

Navigate to: `http://127.0.0.1:8000/api/conversations/`

You should see all conversations with their participants listed.

## Step 6: Get Conversation Details

Navigate to: `http://127.0.0.1:8000/api/conversations/<conversation_uuid>/`

Replace `<conversation_uuid>` with the UUID of a conversation. You should see:
- All participants in the conversation
- All messages in that conversation

## Step 7: Create a Message

1. Go to: `http://127.0.0.1:8000/api/messages/`
2. Scroll to the bottom and use the form or raw data section
3. Enter:
   ```json
   {
     "sender_id": "<user1_uuid>",
     "conversation": "<conversation_uuid>",
     "message_body": "Hello, this is my first message!"
   }
   ```
4. Click "POST" button
5. The message should be created and returned with a message_id

## Step 8: List All Messages

Navigate to: `http://127.0.0.1:8000/api/messages/`

You should see all messages with their details.

## Step 9: Filter Messages by Conversation

Navigate to: `http://127.0.0.1:8000/api/messages/?conversation_id=<conversation_uuid>`

Replace `<conversation_uuid>` with the UUID of a conversation. You should see only messages from that conversation.

## Step 10: Add Participant to Conversation

1. Go to: `http://127.0.0.1:8000/api/conversations/<conversation_uuid>/add_participant/`
2. Enter:
   ```json
   {
     "user_id": "<user3_uuid>"
   }
   ```
3. Click "POST" button
4. The user should be added to the conversation

## Step 11: Remove Participant from Conversation

1. Go to: `http://127.0.0.1:8000/api/conversations/<conversation_uuid>/remove_participant/`
2. Enter:
   ```json
   {
     "user_id": "<user3_uuid>"
   }
   ```
3. Click "POST" button
4. The user should be removed from the conversation

## Testing with Postman (Alternative)

For more advanced testing, you can use Postman:

### 1. Create a new Postman Collection
- Name: "Messaging App API"

### 2. Create requests for each endpoint:

**GET - List Users**
- URL: `http://127.0.0.1:8000/api/users/`
- Method: GET

**GET - List Conversations**
- URL: `http://127.0.0.1:8000/api/conversations/`
- Method: GET

**POST - Create Conversation**
- URL: `http://127.0.0.1:8000/api/conversations/`
- Method: POST
- Body (JSON):
```json
{
  "participant_ids": ["<user1_uuid>", "<user2_uuid>"]
}
```

**GET - Conversation Detail**
- URL: `http://127.0.0.1:8000/api/conversations/<conversation_uuid>/`
- Method: GET

**POST - Send Message**
- URL: `http://127.0.0.1:8000/api/messages/`
- Method: POST
- Body (JSON):
```json
{
  "sender_id": "<user1_uuid>",
  "conversation": "<conversation_uuid>",
  "message_body": "Test message"
}
```

**GET - List Messages**
- URL: `http://127.0.0.1:8000/api/messages/`
- Method: GET

**GET - Filter Messages**
- URL: `http://127.0.0.1:8000/api/messages/?conversation_id=<conversation_uuid>`
- Method: GET

**POST - Add Participant**
- URL: `http://127.0.0.1:8000/api/conversations/<conversation_uuid>/add_participant/`
- Method: POST
- Body (JSON):
```json
{
  "user_id": "<user3_uuid>"
}
```

**POST - Remove Participant**
- URL: `http://127.0.0.1:8000/api/conversations/<conversation_uuid>/remove_participant/`
- Method: POST
- Body (JSON):
```json
{
  "user_id": "<user3_uuid>"
}
```

## Expected API Responses

### Success Response (201 Created)
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "participants": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440001",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "role": "host",
      "created_at": "2025-11-16T12:27:15.123456Z"
    }
  ],
  "created_at": "2025-11-16T12:30:45.123456Z"
}
```

### Error Response (400 Bad Request)
```json
{
  "error": "user_id is required"
}
```

### Error Response (404 Not Found)
```json
{
  "error": "User not found"
}
```

## Troubleshooting Tests

1. **If you get "User not found"**: Make sure you're using the correct UUID from the users list
2. **If conversation shows no messages**: Send a message first, then refresh
3. **If participants not showing**: Ensure users were added when creating the conversation
4. **If you get CSRF error**: Make sure you're using the browsable API or include CSRF token in requests

## Performance Notes

- All endpoints support pagination (default 10 items per page)
- Add `?page=2` to any list endpoint to see the next page
- Indexes are created on email (User), conversation (Message), and sender (Message) for query optimization

## Database Verification

To verify the database state:

1. Go to Django Admin: `http://127.0.0.1:8000/admin/`
2. Click on the model you want to inspect:
   - Users
   - Conversations
   - Messages
3. View all records and their relationships

---

**Last Updated**: November 16, 2025
**API Version**: 1.0
**Django Version**: 5.2.7
