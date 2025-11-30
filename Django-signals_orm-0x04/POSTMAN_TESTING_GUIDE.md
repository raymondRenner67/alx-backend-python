# Postman Testing Guide - Messaging App API

## Overview
This guide provides step-by-step instructions for testing the Messaging App API using the provided Postman collection (`postman_collection.json`).

## Prerequisites
1. **Postman** installed ([Download](https://www.postman.com/downloads/))
2. **Django development server** running: `python manage.py runserver`
3. **Superuser account** created: `python manage.py createsuperuser`

## Setup Instructions

### 1. Import Collection
1. Open Postman
2. Click **Import** (top-left)
3. Select **Upload Files**
4. Choose `postman_collection.json` from the messaging_app directory
5. Click **Import**

### 2. Create Environment (Optional but Recommended)
1. Click **Environments** (left sidebar)
2. Click **Create New**
3. Name: `Messaging App Dev`
4. Add these variables:
   - `base_url`: `http://127.0.0.1:8000`
   - `access_token`: (will be auto-filled)
   - `user1_id`: (will be auto-filled)
   - `user2_id`: (will be auto-filled)
   - `conversation_id`: (will be auto-filled)
   - `message_id`: (will be auto-filled)
5. Click **Save**

### 3. Create Test Users in Django Admin
1. Navigate to `http://127.0.0.1:8000/admin/`
2. Log in with your superuser credentials
3. Click **Users** under the Chats section
4. Click **Add User** and create at least 3 test users:
   - **User 1**: first_name=John, last_name=Doe, email=john@example.com, password=test123, role=host
   - **User 2**: first_name=Jane, last_name=Smith, email=jane@example.com, password=test123, role=guest
   - **User 3**: first_name=Bob, last_name=Johnson, email=bob@example.com, password=test123, role=admin

## Testing Workflow

### Phase 1: Authentication

#### Test 1.1: Obtain JWT Token
1. In Postman, go to **Authentication → 2. Obtain JWT Token**
2. Update the request body with your superuser credentials:
   ```json
   {
     "username": "your_superuser_username",
     "password": "your_superuser_password"
   }
   ```
3. Click **Send**
4. **Expected**: Status 200 with `access` and `refresh` tokens
5. **Result**: Tokens are automatically saved to environment variables

#### Test 1.2: Test Unauthorized Access
1. Go to **Authentication → 4. Test Unauthorized Access (No Token)**
2. Click **Send**
3. **Expected**: Status 401 or 403 (Unauthorized)

### Phase 2: User Management

#### Test 2.1: List All Users
1. Go to **User Management → 1. List All Users**
2. Click **Send**
3. **Expected**: Status 200 with array of users
4. **Result**: First user's ID is saved to `user1_id` variable

#### Test 2.2: Get User Details
1. Go to **User Management → 2. Get User Details**
2. Click **Send**
3. **Expected**: Status 200 with user details

### Phase 3: Conversations

#### Test 3.1: Create Conversation
1. Go to **Conversations → 1. Create Conversation**
2. **Note**: You need to manually set `user1_id` and `user2_id` in the environment variables first
   - From Phase 2 results, get two user IDs and set them
3. Update request body if needed with the correct user IDs
4. Click **Send**
5. **Expected**: Status 201 with `conversation_id`
6. **Result**: Conversation ID is saved to environment

#### Test 3.2: List Conversations
1. Go to **Conversations → 2. List Conversations**
2. Click **Send**
3. **Expected**: Status 200 with array of conversations

#### Test 3.3: Get Conversation Details
1. Go to **Conversations → 3. Get Conversation Details**
2. Click **Send**
3. **Expected**: Status 200 with conversation details including messages array

#### Test 3.4: Add Participant
1. Go to **Conversations → 4. Add Participant to Conversation**
2. Set `user3_id` in environment first
3. Click **Send**
4. **Expected**: Status 200 with updated conversation

#### Test 3.5: Test Unauthorized Access
1. Go to **Conversations → 6. Test Unauthorized Conversation Access**
2. Set `non_participant_token` to a token from a user not in the conversation
3. Click **Send**
4. **Expected**: Status 403 Forbidden

### Phase 4: Messages

#### Test 4.1: Send Message
1. Go to **Messages → 1. Send Message**
2. Click **Send**
3. **Expected**: Status 201 with `message_id`
4. **Result**: Message ID is saved to environment

#### Test 4.2: List Messages (Pagination)
1. Go to **Messages → 2. List Messages (All)**
2. Click **Send**
3. **Expected**: Status 200 with paginated response showing:
   - `count`: total number of messages
   - `results`: array of 20 messages (or less on last page)
   - `next`/`previous`: links to other pages
   - `total_pages`: total number of pages

#### Test 4.3: Filter by Conversation
1. Go to **Messages → 4. Filter Messages by Conversation**
2. Click **Send**
3. **Expected**: Status 200 with only messages from that conversation

#### Test 4.4: Filter by Sender
1. Go to **Messages → 5. Filter Messages by Sender**
2. Click **Send**
3. **Expected**: Status 200 with only messages from that sender

#### Test 4.5: Filter by Time Range
1. Go to **Messages → 6. Filter Messages by Time Range**
2. Update dates as needed (current date range in request)
3. Click **Send**
4. **Expected**: Status 200 with messages in that time range

#### Test 4.6: Filter Last N Days
1. Go to **Messages → 7. Filter Messages from Last N Days**
2. Click **Send**
3. **Expected**: Status 200 with messages from last 7 days

#### Test 4.7: Search Messages
1. Go to **Messages → 8. Search Messages by Content**
2. Update search term in URL parameter
3. Click **Send**
4. **Expected**: Status 200 with matching messages

#### Test 4.8: Update Message
1. Go to **Messages → 10. Update Message**
2. Click **Send**
3. **Expected**: Status 200 with updated message

#### Test 4.9: Delete Message
1. Go to **Messages → 11. Delete Message**
2. Click **Send**
3. **Expected**: Status 204 No Content

#### Test 4.10: Test Unauthorized Message Access
1. Go to **Messages → 12. Test Unauthorized Message Access**
2. Click **Send**
3. **Expected**: Status 403 Forbidden

### Phase 5: Security Tests

#### Test 5.1: Unauthorized Conversation Creation
1. Go to **Permission & Security Tests → 1. Test Unauthorized Conversation Creation**
2. Click **Send** (no auth header)
3. **Expected**: Status 401 Unauthorized

#### Test 5.2: Non-Participant Cannot Send Message
1. Go to **Permission & Security Tests → 2. Test Non-Participant Cannot Send Message**
2. Use a token from a different user
3. Click **Send**
4. **Expected**: Status 403 Forbidden

#### Test 5.3: Non-Participant Cannot Delete Message
1. Go to **Permission & Security Tests → 3. Test Non-Participant Cannot Delete Message**
2. Use a token from a different user
3. Click **Send**
4. **Expected**: Status 403 Forbidden

## Common Issues & Solutions

### Issue: "401 Unauthorized" on authenticated requests
**Solution**: 
1. Ensure your access token is valid and not expired
2. Refresh the token using **Authentication → 3. Refresh JWT Token**
3. Verify the `Authorization` header is set to `Bearer {{access_token}}`

### Issue: "400 Bad Request" when creating conversation
**Solution**:
1. Ensure `user1_id` and `user2_id` are valid UUIDs
2. Check that both users exist in the system
3. Verify the request body format is correct

### Issue: Pagination not showing 20 messages
**Solution**:
1. Check if you have at least 20 messages in the database
2. Verify `page_size` is set to 20 in `chats/pagination.py`
3. Try adding `?page_size=20` to the URL

### Issue: Filters not working
**Solution**:
1. Ensure `django-filter` is installed: `pip install django-filter`
2. Verify `django_filters` is in `INSTALLED_APPS` in settings.py
3. Check filter field names match exactly: `sender`, `conversation`, `sent_after`, `sent_before`, `message_body`

## Response Examples

### Successful Token Obtain (201)
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "admin@example.com",
  "role": "admin"
}
```

### Create Conversation (201)
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440001",
  "participants": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440002",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "role": "host"
    }
  ],
  "created_at": "2025-11-23T12:30:45.123456Z"
}
```

### List Messages with Pagination (200)
```json
{
  "count": 150,
  "next": "http://127.0.0.1:8000/api/messages/?page=2",
  "previous": null,
  "page_size": 20,
  "total_pages": 8,
  "current_page": 1,
  "results": [
    {
      "message_id": "550e8400-e29b-41d4-a716-446655440003",
      "sender": {
        "user_id": "550e8400-e29b-41d4-a716-446655440002",
        "email": "john@example.com"
      },
      "conversation": "550e8400-e29b-41d4-a716-446655440001",
      "message_body": "Hello!",
      "sent_at": "2025-11-23T12:35:00.123456Z"
    }
  ]
}
```

### Unauthorized Response (403)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

## Testing Checklist

- [ ] JWT token obtained successfully
- [ ] Unauthorized access rejected (401)
- [ ] Users listed and individual user retrieved
- [ ] Conversation created with multiple participants
- [ ] Conversation details retrieved with messages
- [ ] Participant added to conversation
- [ ] Participant removed from conversation
- [ ] Non-participant cannot access conversation (403)
- [ ] Message sent to conversation
- [ ] Messages listed with pagination (20 per page)
- [ ] Messages filtered by conversation
- [ ] Messages filtered by sender
- [ ] Messages filtered by time range
- [ ] Messages filtered by last N days
- [ ] Message content searched
- [ ] Message updated
- [ ] Message deleted
- [ ] Non-participant cannot access message (403)
- [ ] Non-participant cannot send message (403)
- [ ] Unauthorized conversation creation rejected (401)

## Advanced Testing

### Batch Operations
1. Create multiple conversations
2. Send multiple messages to each
3. Test pagination across pages
4. Use combined filters (conversation + sender + time range)

### Load Testing
1. Create hundreds of messages
2. Test pagination performance
3. Test filtering performance with large datasets

### Concurrent Access
1. Simulate multiple users accessing same conversation
2. Test message ordering and consistency

## Support
For issues or questions, refer to the API documentation in `README.md` or check Django logs:
```bash
python manage.py runserver  # Shows request/response logs
```
