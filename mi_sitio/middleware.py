from django.conf import settings

class CustomSessionMiddleware:
    """
    Middleware para separar las cookies de sesión entre el panel de administración
    y la página pública.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si el usuario accede al panel de administración
        if request.path.startswith('/admin/'):
            settings.SESSION_COOKIE_NAME = getattr(settings, 'ADMIN_SESSION_COOKIE_NAME', 'admin_sessionid')
        else:
            # Para la página pública
            settings.SESSION_COOKIE_NAME = getattr(settings, 'SESSION_COOKIE_NAME', 'public_sessionid')

        response = self.get_response(request)
        return response
