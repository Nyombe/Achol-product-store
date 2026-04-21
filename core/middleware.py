from django.shortcuts import redirect
from django.urls import reverse
from django.http import Http404

class AdminAccessMiddleware:
    """
    Middleware to strictly abstract regular users from the administration portal.
    If a non-staff user attempts to access the administration URL, they receive 
    a 404 error, effectively hiding the portal's existence.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define the obfuscated administrative path
        admin_path = '/management/'
        
        if request.path.startswith(admin_path):
            # 1. Always allow the login page and the root path (so it can redirect to login)
            if request.path == admin_path or 'login' in request.path:
                return self.get_response(request)
                
            # 2. Strictly block non-staff from all other management paths (Dashboard, Products, etc.)
            if not request.user.is_authenticated or not request.user.is_staff:
                # Return a 404 instead of a redirect to hide the portal's existence
                raise Http404
        

class SecurityHeadersMiddleware:
    """
    Middleware to add security-related headers to responses, 
    including Content Security Policy (CSP).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        from django.conf import settings
        
        # Apply Content Security Policy if defined in settings
        csp = getattr(settings, 'SECURE_CONTENT_SECURITY_POLICY', None)
        if csp:
            csp_header = []
            for directive, values in csp.items():
                csp_header.append(f"{directive} {' '.join(values)}")
            response['Content-Security-Policy'] = '; '.join(csp_header)
            
        return response
