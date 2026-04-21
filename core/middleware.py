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
            # Only allow authenticated staff/superusers
            if not request.user.is_authenticated or not request.user.is_staff:
                # Return a 404 instead of a redirect to hide the portal
                raise Http404
        
        response = self.get_response(request)
        return response
