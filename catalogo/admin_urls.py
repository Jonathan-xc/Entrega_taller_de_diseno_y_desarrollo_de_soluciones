from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('productos/', views.listar_productos, name='listar_productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/agregar/', views.agregar_usuario, name='agregar_usuario'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('usuarios/editar/<int:user_id>/', views.edit_user, name='edit_user'),
    path('usuarios/eliminar/<int:user_id>/', views.delete_user, name='delete_user'),
    path('ordenes/', views.ordenes, name='ordenes'),
    path('transacciones/', views.listar_transacciones, name='transacciones'),
    
    path('admin_panel/ordenes/<int:pedido_id>/detalles/', views.ver_detalles_pedido, name='ver_detalles_pedido'),
    path('admin_panel/ordenes/<int:pedido_id>/actualizar_estado/', views.actualizar_estado_pedido, name='actualizar_estado_pedido'),
]
