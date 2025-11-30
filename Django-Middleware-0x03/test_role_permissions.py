#!/usr/bin/env python
"""
Test script for RolePermissionMiddleware
"""
import os
import django
from django.test import RequestFactory
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_app.settings')
django.setup()

from chats.middleware import RolePermissionMiddleware
from django.http import HttpResponse

print("=" * 60)
print("Testing RolePermissionMiddleware (Role-Based Access Control)")
print("=" * 60)

# Create middleware instance
def mock_get_response(req):
    return HttpResponse('Access granted')

middleware = RolePermissionMiddleware(mock_get_response)

# Create a mock request factory
factory = RequestFactory()
User = get_user_model()

# Create mock user objects (not saved to DB, just for testing)
class MockUser:
    def __init__(self, username, role, is_authenticated=True):
        self.username = username
        self.role = role
        self.is_authenticated = is_authenticated

# Test 1: Admin user (should be allowed)
print("\n[Test 1] Admin user accessing endpoint")
request = factory.get('/api/messages/')
request.user = MockUser(username='admin_user', role='admin')
response = middleware(request)
print(f"  Admin User: Status {response.status_code} - {'✓ Access granted' if response.status_code == 200 else '✗ Access denied'}")

# Test 2: Moderator user (should be allowed)
print("\n[Test 2] Moderator user accessing endpoint")
request = factory.get('/api/messages/')
request.user = MockUser(username='mod_user', role='moderator')
response = middleware(request)
print(f"  Moderator User: Status {response.status_code} - {'✓ Access granted' if response.status_code == 200 else '✗ Access denied'}")

# Test 3: Guest user (should be denied - 403)
print("\n[Test 3] Guest user accessing endpoint (should be DENIED)")
request = factory.get('/api/messages/')
request.user = MockUser(username='guest_user', role='guest')
response = middleware(request)
print(f"  Guest User: Status {response.status_code} - {'✓ Correctly denied (403)' if response.status_code == 403 else '✗ Should be denied!'}")
if response.status_code == 403:
    print(f"  Response preview: {response.content.decode()[:100]}...")

# Test 4: User with no role (should be denied - 403)
print("\n[Test 4] User with no role (should be DENIED)")
request = factory.get('/api/messages/')
request.user = MockUser(username='norole_user', role=None)
response = middleware(request)
print(f"  No Role User: Status {response.status_code} - {'✓ Correctly denied (403)' if response.status_code == 403 else '✗ Should be denied!'}")

# Test 5: Unauthenticated user (should be denied - 403)
print("\n[Test 5] Unauthenticated user (should be DENIED)")
request = factory.get('/api/messages/')
request.user = MockUser(username='anon', role=None, is_authenticated=False)
response = middleware(request)
print(f"  Unauthenticated: Status {response.status_code} - {'✓ Correctly denied (403)' if response.status_code == 403 else '✗ Should be denied!'}")
if response.status_code == 403:
    print(f"  Response preview: {response.content.decode()[:100]}...")

print("\n" + "=" * 60)
print("Role Permission Test Complete!")
print("=" * 60)
