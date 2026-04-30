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
            # 1. Always allow authenticated staff members
            if request.user.is_authenticated and request.user.is_staff:
                return self.get_response(request)
                
            # 2. Allow the login page for everyone (so they can become staff)
            if 'login' in request.path:
                return self.get_response(request)
                
            # 3. If not authenticated, redirect to login
            if not request.user.is_authenticated:
                return redirect(f"{admin_path}login/")
                
            # 4. If authenticated but not staff, block with 404
            if not request.user.is_staff:
                raise Http404
        
        return self.get_response(request)

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
