from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.views import redirect_to_login

def login_required(view_func):
    """
    Decorador para proteger vistas que requieren que el usuario esté autenticado.
    Si el usuario no está autenticado, será redirigido a la página de inicio de sesión.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('login'))  # Redirigir al login si no está autenticado.
    return _wrapped_view

def role_required(required_roles):
    """
    Decorador para proteger vistas según el rol del usuario.
    :param required_roles: Lista de roles permitidos para acceder a la vista.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and hasattr(request.user, 'rol') and request.user.rol in required_roles:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
        return _wrapped_view
    return decorator

def login_required_ajax(view_func):
    """Maneja solicitudes AJAX y no AJAX para redireccionar al login."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Respuesta JSON específica para solicitudes AJAX
                return JsonResponse({
                    "error": "Usuario no autenticado",
                    "redirect": "/login/?next=" + request.path
                }, status=401)
            # Para solicitudes normales, redirigir al login
            return redirect_to_login(request.get_full_path())
        return view_func(request, *args, **kwargs)
    return wrapper