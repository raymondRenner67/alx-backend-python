import logging
import sys
from datetime import datetime

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
