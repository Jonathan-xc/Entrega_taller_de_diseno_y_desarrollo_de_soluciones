from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.html import format_html
from decimal import Decimal

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, nombre=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        if not nombre:
            raise ValueError("El nombre es obligatorio")
        email = self.normalize_email(email)
        usuario = self.model(email=email, nombre=nombre, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password, nombre, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields['rol'] = 'administrador'
        return self.create_user(email, password, nombre, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    rol = models.CharField(max_length=50, choices=[
        ('cliente', 'Cliente'),
        ('vendedor', 'Vendedor'),
        ('empleado_postventa', 'Empleado Postventa'),
        ('administrador', 'Administrador')
    ])
    fecha_registro = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    class Meta:
        db_table = 'usuarios'

# Modelo Producto
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    categoria = models.CharField(max_length=50, choices=[
        ('clasica', 'Clásica'),
        ('moderna', 'Moderna'),
        ('premium', 'Premium')
    ])
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    # Método para formatear el precio en CLP
    def precio_formateado(self):
        return format_html('${:,.0f}'.format(self.precio).replace(',', '.'))
    
    def tiene_stock(self):
        return self.stock > 0

# Modelo principal del carrito
class Carrito(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="carrito")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def obtener_total(self):
        """Calcula el total de todos los productos en el carrito."""
        return sum(detalle.obtener_subtotal() for detalle in self.detalles.all())

    def obtener_total_con_iva(self):
        """Calcula el total con IVA incluido."""
        total = self.obtener_total()
        iva = total * Decimal('0.19')  # Usar Decimal en lugar de float
        return total + iva

    def __str__(self):
        return f"Carrito de {self.usuario.nombre}"


# Modelo de detalle del carrito
class DetalleCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, related_name="detalles", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    def obtener_subtotal(self):
        """Calcula el subtotal de este detalle."""
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad} (Carrito de {self.carrito.usuario.nombre})"

# Modelo Pedido
class Pedido(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=50, choices=[
        ('preparacion', 'En preparación'),
        ('transito', 'En tránsito'),
        ('finalizado', 'Finalizado')
    ], default='preparacion')
    fecha_pedido = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.estado}"

# Modelo DetallePedido
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

# Modelo Transaccion
class Transaccion(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    metodo_pago = models.CharField(max_length=50, choices=[
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('efectivo', 'Efectivo')
    ])
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_transaccion = models.DateTimeField(auto_now_add=True)
