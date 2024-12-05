from .models import Carrito
from django.utils.html import format_html

def carrito_total(request):
    # Si el usuario no está autenticado, el carrito no es relevante
    if not request.user.is_authenticated:
        return {'total': "$0", 'total_cantidad': 0}

    try:
        carrito = Carrito.objects.prefetch_related('detalles__producto').get(usuario=request.user)
        total_cantidad = sum(detalle.cantidad for detalle in carrito.detalles.all())
        total = f"${carrito.obtener_total():,.0f}".replace(",", ".")  # Removemos los decimales con :,.0f
    except Carrito.DoesNotExist:
        total = "$0"
        total_cantidad = 0

    return {
        'total': total,
        'total_cantidad': total_cantidad,
    }
