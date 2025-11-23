#!/usr/bin/env python
"""
Test script for RestrictAccessByTimeMiddleware
"""
import os
import django
from django.test import RequestFactory
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_app.settings')
django.setup()

from chats.middleware import RestrictAccessByTimeMiddleware
from django.http import HttpResponse

# Create a mock request
factory = RequestFactory()
request = factory.get('/')

# Create middleware instance with a mock get_response
def mock_get_response(req):
    return HttpResponse('Success')

middleware = RestrictAccessByTimeMiddleware(mock_get_response)

# Test the middleware
response = middleware(request)
current_time = timezone.now()
current_hour = current_time.hour

print(f"Current server time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"Current hour: {current_hour}")
print(f"Response status: {response.status_code}")

if response.status_code == 403:
    print("✓ ACCESS DENIED (outside 6PM-9PM) - Status 403 Forbidden")
    print(f"Response content: {response.content.decode()[:100]}...")
elif response.status_code == 200:
    print("✓ ACCESS ALLOWED (within 6PM-9PM) - Status 200 OK")
else:
    print(f"? Unexpected status code: {response.status_code}")
