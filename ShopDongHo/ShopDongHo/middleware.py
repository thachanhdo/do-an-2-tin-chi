"""
Middleware to serve media files in production when using Gunicorn
"""
import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.utils._os import safe_join


class ServeMediaMiddleware:
    """
    Middleware to serve media files from MEDIA_ROOT in production.
    This is necessary because Django's static() helper doesn't work with Gunicorn.

    In production, you should use a proper web server like Nginx, but for
    simple deployments, this middleware allows Gunicorn to serve media files.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.media_url = settings.MEDIA_URL
        self.media_root = settings.MEDIA_ROOT

    def __call__(self, request):
        # Check if this is a media file request
        if request.path.startswith(self.media_url):
            # Get the relative path after MEDIA_URL
            relative_path = request.path[len(self.media_url):]

            # Build the full file path
            try:
                file_path = safe_join(self.media_root, relative_path)
            except ValueError:
                # Invalid path (e.g., contains ..)
                raise Http404("Invalid media path")

            # Check if file exists
            if os.path.isfile(file_path):
                # Serve the file
                return FileResponse(open(file_path, 'rb'))
            else:
                raise Http404("Media file not found")

        # Not a media request, continue normally
        response = self.get_response(request)
        return response
