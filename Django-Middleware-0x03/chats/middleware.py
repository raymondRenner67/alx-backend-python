import logging
import sys
from datetime import datetime
from django.http import HttpResponseForbidden
from django.utils import timezone

class RequestLoggingMiddleware:
    """
    Middleware that logs each user's requests to a file.
    Logs timestamp, user, and request path.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        
        Args:
            get_response: The next middleware or view in the stack
        """
        self.get_response = get_response
        # Get the logger configured in settings.py
        self.logger = logging.getLogger('request_logger')
    
    def __call__(self, request):
        """
        Process the request and log user information.
        
        Args:
            request: The HTTP request object
            
        Returns:
            The response from the next middleware or view
        """
        # Get user information
        user = request.user.username if request.user.is_authenticated else 'AnonymousUser'
        
        # Log the request information
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_message)
        
        # Flush the handlers to ensure the message is written immediately
        for handler in self.logger.handlers:
            handler.flush()
        
        # Call the next middleware or view
        response = self.get_response(request)
        
        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware that restricts access to messaging app during certain hours.
    Allows access only between 6PM (18:00) and 9PM (21:00).
    Returns 403 Forbidden for requests outside this window.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        
        Args:
            get_response: The next middleware or view in the stack
        """
        self.get_response = get_response
        # Define allowed time window: 6PM (18:00) to 9PM (21:00)
        self.start_hour = 18  # 6PM
        self.end_hour = 21    # 9PM
    
    def __call__(self, request):
        """
        Check if current time is within allowed access window.
        Return 403 Forbidden if outside 6PM-9PM window.
        
        Args:
            request: The HTTP request object
            
        Returns:
            HttpResponseForbidden (403) if outside allowed hours,
            otherwise the response from the next middleware or view
        """
        # Get current server time
        current_time = timezone.now()
        current_hour = current_time.hour
        
        # Check if current hour is within allowed window (6PM to 9PM)
        # Allow access if hour is 18, 19, or 20 (not including 21:00 and beyond)
        if current_hour < self.start_hour or current_hour >= self.end_hour:
            # Access denied - outside allowed hours
            return HttpResponseForbidden(
                "<h1>403 Forbidden</h1>"
                "<p>Chat access is restricted. Please access between 6PM and 9PM.</p>"
                f"<p>Current server time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}</p>"
            )
        
        # Access allowed - call the next middleware or view
        response = self.get_response(request)
        
        return response
