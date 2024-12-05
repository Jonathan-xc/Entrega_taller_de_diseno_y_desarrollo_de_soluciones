from django.contrib import admin
from .models import Usuario, Producto

# Configuración para Usuario en el panel de administración
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'nombre', 'rol', 'is_staff', 'is_active')
    list_filter = ('rol', 'is_staff', 'is_active')
    search_fields = ('email', 'nombre')
    ordering = ('email',)

# Configuración para Producto en el panel de administración
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'fecha_creacion')
    search_fields = ('nombre', 'categoria')
    list_filter = ('categoria', 'fecha_creacion')
    ordering = ('nombre',)
