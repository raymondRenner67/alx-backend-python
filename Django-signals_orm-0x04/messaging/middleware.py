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


class OffensiveLanguageMiddleware:
    """
    Middleware that limits the number of chat messages a user can send
    within a certain time window, based on their IP address.
    Prevents spam by enforcing a rate limit (e.g., 5 messages per minute).
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        
        Args:
            get_response: The next middleware or view in the stack
        """
        self.get_response = get_response
        # Store message counts per IP: {ip_address: [(timestamp1, timestamp2, ...)]}
        self.message_tracker = {}
        # Rate limit settings
        self.max_messages = 5  # Maximum messages allowed
        self.time_window = 60  # Time window in seconds (1 minute)
    
    def __call__(self, request):
        """
        Track POST requests (messages) from each IP address and enforce rate limits.
        
        Args:
            request: The HTTP request object
            
        Returns:
            HttpResponseForbidden (403) if rate limit exceeded,
            otherwise the response from the next middleware or view
        """
        # Only track POST requests (message sending)
        if request.method == 'POST':
            # Get client IP address
            ip_address = self.get_client_ip(request)
            current_time = timezone.now()
            
            # Initialize tracker for this IP if not exists
            if ip_address not in self.message_tracker:
                self.message_tracker[ip_address] = []
            
            # Remove timestamps older than the time window
            cutoff_time = current_time.timestamp() - self.time_window
            self.message_tracker[ip_address] = [
                timestamp for timestamp in self.message_tracker[ip_address]
                if timestamp > cutoff_time
            ]
            
            # Check if rate limit exceeded
            if len(self.message_tracker[ip_address]) >= self.max_messages:
                return HttpResponseForbidden(
                    "<h1>403 Forbidden</h1>"
                    f"<p>Rate limit exceeded. You can only send {self.max_messages} messages per minute.</p>"
                    "<p>Please wait before sending more messages.</p>"
                    f"<p>Your IP: {ip_address}</p>"
                )
            
            # Add current timestamp to tracker
            self.message_tracker[ip_address].append(current_time.timestamp())
        
        # Continue processing the request
        response = self.get_response(request)
        
        return response
    
    def get_client_ip(self, request):
        """
        Extract client IP address from request, considering proxies.
        
        Args:
            request: The HTTP request object
            
        Returns:
            str: The client's IP address
        """
        # Check for X-Forwarded-For header (proxy/load balancer)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP in the list
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            # Direct connection
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RolePermissionMiddleware:
    """
    Middleware that checks the user's role before allowing access to specific actions.
    Only allows admin or moderator users to access certain endpoints.
    Returns 403 Forbidden for users without proper permissions.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        
        Args:
            get_response: The next middleware or view in the stack
        """
        self.get_response = get_response
        # Define allowed roles
        self.allowed_roles = ['admin', 'moderator']
    
    def __call__(self, request):
        """
        Check the user's role and enforce permissions.
        
        Args:
            request: The HTTP request object
            
        Returns:
            HttpResponseForbidden (403) if user doesn't have required role,
            otherwise the response from the next middleware or view
        """
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Get user's role (assuming the User model has a 'role' field)
            user_role = getattr(request.user, 'role', None)
            
            # Check if user has an allowed role
            if user_role not in self.allowed_roles:
                return HttpResponseForbidden(
                    "<h1>403 Forbidden</h1>"
                    "<p>Access denied. You do not have the required permissions.</p>"
                    f"<p>Your role: {user_role or 'No role assigned'}</p>"
                    f"<p>Required roles: {', '.join(self.allowed_roles)}</p>"
                )
        else:
            # Unauthenticated users are denied
            return HttpResponseForbidden(
                "<h1>403 Forbidden</h1>"
                "<p>Authentication required. Please log in to access this resource.</p>"
            )
        
        # User has proper permissions - continue processing
        response = self.get_response(request)
        
        return response
