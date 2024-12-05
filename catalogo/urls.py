from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
    path('contacto/', views.contacto, name='contacto'),
    path('login/', views.login_cliente, name='login'),
    path('registro/', views.registro, name='registro'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_producto_carrito, name='agregar_producto_carrito'),
    path('carrito/actualizar/<int:detalle_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('carrito/eliminar/<int:detalle_id>/', views.eliminar_producto_carrito, name='eliminar_producto_carrito'),
    path('carrito/detalles/', views.obtener_detalles_carrito, name='obtener_detalles_carrito'),
    path('producto/detalle/<int:producto_id>/', views.producto_detalle, name='producto_detalle'),
    path('finalizar-compra/', views.finalizar_compra, name='finalizar_compra'),
    path('actualizar-direccion/', views.actualizar_direccion, name='actualizar_direccion'),
    
    
    path('api/orders', views.crear_orden_paypal, name='crear_orden_paypal'),
    path('api/orders/<str:order_id>/capture', views.capturar_orden_paypal, name='capturar_orden_paypal'),
    path('agradecimiento/', views.agradecimiento, name='agradecimiento'),
]
