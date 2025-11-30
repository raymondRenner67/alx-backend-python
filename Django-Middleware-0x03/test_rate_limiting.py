#!/usr/bin/env python
"""
Test script for OffensiveLanguageMiddleware (Rate Limiting)
"""
import os
import django
from django.test import RequestFactory
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_app.settings')
django.setup()

from chats.middleware import OffensiveLanguageMiddleware
from django.http import HttpResponse

print("=" * 60)
print("Testing OffensiveLanguageMiddleware (Rate Limiting)")
print("=" * 60)

# Create middleware instance
def mock_get_response(req):
    return HttpResponse('Message sent successfully')

middleware = OffensiveLanguageMiddleware(mock_get_response)

# Create a mock request factory
factory = RequestFactory()

# Test 1: Send 5 POST requests (should succeed)
print("\n[Test 1] Sending 5 POST requests from IP 192.168.1.100")
for i in range(5):
    request = factory.post('/api/messages/', data={'content': f'Test message {i+1}'})
    request.META['REMOTE_ADDR'] = '192.168.1.100'
    response = middleware(request)
    print(f"  Request {i+1}: Status {response.status_code} - {'✓ Success' if response.status_code == 200 else '✗ Blocked'}")

# Test 2: Send 6th request (should be blocked - rate limit exceeded)
print("\n[Test 2] Sending 6th POST request (should be BLOCKED)")
request = factory.post('/api/messages/', data={'content': 'Test message 6'})
request.META['REMOTE_ADDR'] = '192.168.1.100'
response = middleware(request)
print(f"  Request 6: Status {response.status_code} - {'✓ Correctly blocked (403)' if response.status_code == 403 else '✗ Should be blocked!'}")
if response.status_code == 403:
    print(f"  Response preview: {response.content.decode()[:100]}...")

# Test 3: GET request should not be rate limited
print("\n[Test 3] Sending GET request (should NOT be rate limited)")
request = factory.get('/api/messages/')
request.META['REMOTE_ADDR'] = '192.168.1.100'
response = middleware(request)
print(f"  GET Request: Status {response.status_code} - {'✓ Success' if response.status_code == 200 else '✗ Error'}")

# Test 4: Different IP address should have separate limit
print("\n[Test 4] Sending 3 POST requests from different IP (192.168.1.200)")
for i in range(3):
    request = factory.post('/api/messages/', data={'content': f'Test from IP2 - {i+1}'})
    request.META['REMOTE_ADDR'] = '192.168.1.200'
    response = middleware(request)
    print(f"  Request {i+1}: Status {response.status_code} - {'✓ Success' if response.status_code == 200 else '✗ Blocked'}")

print("\n" + "=" * 60)
print("Rate Limiting Test Complete!")
print("=" * 60)
