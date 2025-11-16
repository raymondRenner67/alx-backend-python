# Messaging App - Django REST Framework API

A robust REST API built with Django and Django REST Framework for managing conversations and messages between users.

## Project Overview

This project implements a messaging system with the following core features:
- User management with role-based access (guest, host, admin)
- Conversation management with multiple participants
- Message creation and retrieval within conversations
- RESTful API endpoints for all operations

## Project Structure

```
messaging_app/
├── messaging_app/          # Main project settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL routing
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
├── chats/                  # Main app for messaging functionality
│   ├── models.py          # Data models (User, Conversation, Message)
│   ├── views.py           # API ViewSets
│   ├── serializers.py     # DRF Serializers
│   ├── urls.py            # App URL routing
│   ├── admin.py           # Django Admin configuration
│   └── migrations/        # Database migrations
├── manage.py              # Django management command
└── db.sqlite3            # SQLite database
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Django 5.2.7
- Django REST Framework 3.14+

### Setup Instructions

1. **Create a virtual environment** (if not already done):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install django djangorestframework
   ```

3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser** (for Django Admin):
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/api/`

## Data Models

### User Model
Extends Django's AbstractUser with additional fields:
- `user_id` (UUID): Primary key
- `first_name`: User's first name
- `last_name`: User's last name
- `email`: Unique email address
- `phone_number`: Optional phone number
- `role`: User role (guest, host, admin)
- `created_at`: Timestamp of creation

**Constraints:**
- Email is unique and indexed
- All required fields are not nullable
- UUID primary key for distributed systems support

### Conversation Model
Represents a conversation between multiple users:
- `conversation_id` (UUID): Primary key
- `participants`: Many-to-many relationship with Users
- `created_at`: Timestamp of creation

**Relationships:**
- Many-to-many with User model for flexible multi-party conversations

### Message Model
Represents a single message in a conversation:
- `message_id` (UUID): Primary key
- `sender`: Foreign key to User
- `conversation`: Foreign key to Conversation
- `message_body`: Text content of the message
- `sent_at`: Timestamp of message creation

**Constraints:**
- Foreign key constraints on sender_id and conversation_id
- Indexed on conversation and sender for query performance

## API Endpoints

### Users
- `GET /api/users/` - List all users
- `GET /api/users/{user_id}/` - Retrieve a specific user

### Conversations
- `GET /api/conversations/` - List all conversations
- `POST /api/conversations/` - Create a new conversation
  - Request body: `{"participant_ids": [uuid1, uuid2, ...]}`
- `GET /api/conversations/{conversation_id}/` - Retrieve conversation with all messages
- `PUT /api/conversations/{conversation_id}/` - Update conversation participants
- `DELETE /api/conversations/{conversation_id}/` - Delete a conversation
- `POST /api/conversations/{conversation_id}/add_participant/` - Add a user to conversation
  - Request body: `{"user_id": uuid}`
- `POST /api/conversations/{conversation_id}/remove_participant/` - Remove a user from conversation
  - Request body: `{"user_id": uuid}`

### Messages
- `GET /api/messages/` - List all messages (supports filtering by conversation_id)
  - Query params: `?conversation_id=uuid`
- `POST /api/messages/` - Create a new message
  - Request body: `{"sender_id": uuid, "conversation": uuid, "message_body": "text"}`
- `GET /api/messages/{message_id}/` - Retrieve a specific message
- `PUT /api/messages/{message_id}/` - Update a message
- `DELETE /api/messages/{message_id}/` - Delete a message

## API Usage Examples

### Create a User (via Django Admin)
1. Go to `http://127.0.0.1:8000/admin/`
2. Log in with superuser credentials
3. Navigate to Users and create new users

### Create a Conversation
```bash
curl -X POST http://127.0.0.1:8000/api/conversations/ \
  -H "Content-Type: application/json" \
  -d '{
    "participant_ids": ["uuid1", "uuid2"]
  }'
```

### Send a Message
```bash
curl -X POST http://127.0.0.1:8000/api/messages/ \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "uuid1",
    "conversation": "conversation_uuid",
    "message_body": "Hello, this is a message!"
  }'
```

### List Messages in a Conversation
```bash
curl http://127.0.0.1:8000/api/messages/?conversation_id=conversation_uuid
```

## Best Practices Implemented

### Project Structure
- ✅ Modular app structure with reusable components
- ✅ Consistent naming conventions
- ✅ Organized folder structure with clear separation of concerns

### Models
- ✅ Extended AbstractUser for custom user model
- ✅ UUID primary keys for distributed systems
- ✅ Proper constraints and indexes for performance
- ✅ Related names for reverse relationships
- ✅ Descriptive string representations

### Routing
- ✅ RESTful URL conventions
- ✅ DefaultRouter for automatic endpoint generation
- ✅ Namespaced routes for clarity
- ✅ Versioned API path (/api/)

### Serialization
- ✅ Separate serializers for list and detail views
- ✅ Nested relationships handling
- ✅ Read-only and write-only fields properly configured
- ✅ Proper validation and error handling

### Views
- ✅ ViewSets for standard CRUD operations
- ✅ Custom actions for specialized operations
- ✅ Filtering capabilities (e.g., by conversation_id)
- ✅ Proper HTTP status codes

### Security
- ✅ Custom User model configured as AUTH_USER_MODEL
- ✅ UUID for non-sequential IDs
- ✅ Proper foreign key constraints with on_delete=CASCADE

## Testing

You can test the API using:
1. **DRF Browsable API**: Navigate to `http://127.0.0.1:8000/api/` in your browser
2. **Postman**: Import the endpoints and test them
3. **curl**: Use command-line requests as shown above

## Migration Instructions

To apply changes to models:

1. Make changes to `chats/models.py`
2. Run: `python manage.py makemigrations`
3. Review the generated migration file
4. Run: `python manage.py migrate`

## Django Admin

Access the admin panel at `http://127.0.0.1:8000/admin/` with your superuser credentials to:
- Manage users and their roles
- View and manage conversations
- Monitor messages in the system
- Perform administrative tasks

## Troubleshooting

### No migrations applied
Ensure you run `python manage.py migrate` after `makemigrations`

### Database locked error
Delete `db.sqlite3` and run migrations again (for development only)

### CustomUser issues
Verify `AUTH_USER_MODEL = 'chats.User'` is set in settings.py

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Django Models and Relationships](https://docs.djangoproject.com/en/5.2/topics/db/models/)

## License

This project is part of the ALX Backend Python curriculum.
