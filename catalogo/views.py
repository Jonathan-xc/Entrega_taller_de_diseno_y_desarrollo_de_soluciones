import logging
import re, json
from decimal import Decimal
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from .models import Producto, Usuario, Pedido, Carrito, DetalleCarrito, Pedido, DetallePedido, Transaccion
from .forms import ProductoForm, RegistroForm, EditarPerfilForm, CustomPasswordChangeForm, LoginForm
from .decorators import role_required, login_required, login_required_ajax



# Configuración de logging
logger = logging.getLogger(__name__)

#Formatea el precio para los productos en la pantalla principal
def formatear_precio_clp(precio):
    return f"${precio:,.0f}".replace(",", ".")  # Cambia las comas por puntos

#Limpiar el precio para los productos en el filtro de busqueda
def limpiar_precio_formateado(precio):
    if precio:
        return int(precio.replace(".", "").replace("$", ""))
    return None

#------------------------------------------------------------------------------------------------------
# Función para verificar si el usuario puede acceder a las vistas públicas
#------------------------------------------------------------------------------------------------------
def es_usuario_publico(usuario):
    """
    Verifica si el usuario tiene permitido interactuar con la página pública.
    """
    if usuario.is_authenticated and usuario.rol in ['administrador', 'vendedor', 'empleado_postventa']:
        return False
    return True

#------------------------------------------------------------------------------------------------------
#------------------------------  TODAS LAS VISTAS PUBLICAS --------------------------------------------
#------------------------------------------------------------------------------------------------------
def home(request):
    if not es_usuario_publico(request.user):
        return redirect('admin_login')

    
    productos = Producto.objects.all()

    # Capturar y limpiar los parámetros GET
    search_query = request.GET.get('search', '').strip()
    price_min = limpiar_precio_formateado(request.GET.get('price_min'))
    price_max = limpiar_precio_formateado(request.GET.get('price_max'))
    category = request.GET.get('category')

    # Filtrar por búsqueda
    if search_query:
        productos = productos.filter(nombre__icontains=search_query)

    # Filtrar por rango de precios
    if price_min is not None:
        productos = productos.filter(precio__gte=price_min)
    if price_max is not None:
        productos = productos.filter(precio__lte=price_max)

    # Filtrar por categoría
    if category:
        productos = productos.filter(categoria=category)

    # Formatear los precios en CLP
    for producto in productos:
        producto.precio_formateado = formatear_precio_clp(producto.precio)

    # Obtener las categorías únicas
    categories = Producto.objects.values_list('categoria', flat=True).distinct()

    # Verificar si el usuario está autenticado para obtener el carrito
    total_cantidad = 0
    total = "$0"
    if request.user.is_authenticated:
        try:
            carrito = Carrito.objects.get(usuario=request.user)
            total_cantidad = sum(detalle.cantidad for detalle in carrito.detalles.all())
            total = f"${int(carrito.obtener_total()):,}".replace(",", ".")
        except Carrito.DoesNotExist:
            pass

    return render(request, 'catalogo/home.html', {
        'productos': productos,
        'categories': categories,
        'search_query': search_query,
        'total': total,  # Total formateado
        'total_cantidad': total_cantidad,
    })

def quienes_somos(request):
    if not es_usuario_publico(request.user):
        return redirect('admin_login')
    
    return render(request, 'catalogo/quienes_somos.html')

def contacto(request):
    if not es_usuario_publico(request.user):
        return redirect('admin_login')
    
    return render(request, 'catalogo/contacto.html')


#------------------------------------------------------------------------------------------------------
#---------------  VISTAS PARA EL FORMULARIO DE LOGIN CLIENTE (login_cliente.html) ---------------------
#------------------------------------------------------------------------------------------------------
def login_cliente(request):
    if not es_usuario_publico(request.user):
        return redirect('admin_login')
    
    # Capturar el parámetro `next` para redirigir después del login
    next_url = request.GET.get('next', '/')

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                if user.rol == 'cliente':  # Solo permitir clientes
                    login(request, user)
                    messages.success(request, "¡Inicio de sesión exitoso!", extra_tags="login")
                    # Validar si la URL `next` es segura para redirigir
                    if url_has_allowed_host_and_scheme(next_url, allowed_hosts=request.get_host()):
                        return redirect(next_url)
                    return redirect('home')
                else:
                    messages.error(request, "Solo los clientes pueden iniciar sesión aquí.", extra_tags="error")
            else:
                messages.error(request, "Credenciales incorrectas. Inténtelo nuevamente.", extra_tags="error")
        else:
            messages.error(request, "Verifica los datos ingresados.", extra_tags="error")
    else:
        form = LoginForm()

    return render(request, 'catalogo/login_cliente.html', {
        'form': form,
        'next': next_url,  # Pasar `next` al contexto para mantenerlo en el formulario
    })

#------------------------------------------------------------------------------------------------------
#---------------  VISTAS PARA EL CLIENTE YA LOGEADO SU PANEL (login.html) -----------------------------
#------------------------------------------------------------------------------------------------------
@login_required
def profile_view(request):
    if not es_usuario_publico(request.user):
        return redirect('admin_login')
    
    return render(request, 'catalogo/profile.html', {'user': request.user})

#------------------------------------------------------------------------------------------------------
#---------------  VISTAS PARA EL FORMULARIO DE REGISTRO CLIENTE (registro.html) -----------------------
#------------------------------------------------------------------------------------------------------
def registro(request):
    if not es_usuario_publico(request.user):
        return redirect('admin_login')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registro exitoso. Ahora puede iniciar sesión.")
            return redirect('login')  # Redirige a la página de inicio de sesión
        else:
            messages.error(request, "Hubo errores en el formulario. Por favor, corrígelos.")
    else:
        form = RegistroForm()
    return render(request, 'catalogo/registro.html', {'form': form})



#------------ VISTA PARA CERRAR SESION -------------------
def logout_view(request):
    if not es_usuario_publico(request.user):
        return redirect('admin_login')
    
    logout(request)
    return redirect('home')

#------------------------------------------------------------------------------------------------------
#-------------  VISTAS PARA EL FORMULARIO DE EDITAR PERFIL (editar_perfil.html) -----------------------
#------------------------------------------------------------------------------------------------------

@login_required
def editar_perfil(request):
    if not es_usuario_publico(request.user):
        return redirect('admin_login')
    
    usuario = request.user
    if request.method == 'POST':
        form = EditarPerfilForm(instance=usuario, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Tu perfil ha sido actualizado exitosamente!")
            return redirect('profile')  # Redirigir a la página de perfil
        else:
            messages.error(request, "Hubo un error al actualizar tu perfil. Revisa los campos.")
    else:
        form = EditarPerfilForm(instance=usuario)
    return render(request, 'catalogo/editar_perfil.html', {'form': form})

#------------------------------------------------------------------------------------------------------
#-------  VISTAS PARA EL FORMULARIO DE CAMBIAR CONTRASEÑA (cambiar_contraseña.html) -------------------
#------------------------------------------------------------------------------------------------------

@login_required
def cambiar_contrasena(request):
    if not es_usuario_publico(request.user):
        return redirect('admin_login')
    
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()  # Cambia la contraseña del usuario
            update_session_auth_hash(request, form.user)  # Mantiene la sesión activa
            messages.success(
                request,
                '¡Tu contraseña se ha cambiado correctamente!',
                extra_tags='success'
            )
            return redirect('profile')  # Redirige a la página de perfil
        else:
            messages.error(request, 'Hubo un error al cambiar la contraseña. Revisa los campos.')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'catalogo/cambiar_contrasena.html', {'form': form})

#------------------------------------------------------------------------------------------------------
#--------------------------------  VISTAS PARA EL CARRITO (carrito.html) ------------------------------
#------------------------------------------------------------------------------------------------------

@login_required
def ver_carrito(request):
    if not es_usuario_publico(request.user):
        return redirect('admin_login')
    
    try:
        carrito = Carrito.objects.prefetch_related('detalles__producto').get(usuario=request.user)
        detalles = carrito.detalles.all()
        total = carrito.obtener_total()
        total_con_iva = carrito.obtener_total_con_iva()

        # Formatear los valores para mostrarlos como CLP
        total_formateado = f"${int(total):,}".replace(",", ".")
        total_con_iva_formateado = f"${int(total_con_iva):,}".replace(",", ".")
        total_cantidad = sum(detalle.cantidad for detalle in detalles)
    except Carrito.DoesNotExist:
        carrito = None
        detalles = []
        total_formateado = "$0"
        total_con_iva_formateado = "$0"
        total_cantidad = 0

    return render(request, 'catalogo/carrito.html', {
        'carrito': carrito,
        'detalles': detalles,
        'total': total_formateado,  # Enviar el total ya formateado
        'total_con_iva': total_con_iva_formateado,  # Enviar total con IVA formateado
        'total_cantidad': total_cantidad,
    })

@login_required_ajax
def agregar_producto_carrito(request, producto_id):
    if not es_usuario_publico(request.user):
        return redirect('admin_login')
    
    producto = get_object_or_404(Producto, id=producto_id)
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

    # Verificar stock
    if producto.stock <= 0:
        return JsonResponse({"error": "El producto no tiene stock disponible."}, status=400)

    detalle, creado = DetalleCarrito.objects.get_or_create(carrito=carrito, producto=producto)

    if not creado:
        if detalle.cantidad + 1 > producto.stock:
            return JsonResponse({"error": f"Solo puedes añadir hasta {producto.stock} unidades."}, status=400)
        detalle.cantidad += 1
    else:
        if 1 > producto.stock:
            return JsonResponse({"error": f"Solo puedes añadir hasta {producto.stock} unidades."}, status=400)
        detalle.cantidad = 1

    detalle.save()

    total_items = sum(d.cantidad for d in carrito.detalles.all())
    total_price = carrito.obtener_total()

    return JsonResponse({
        "message": f"{producto.nombre} agregado al carrito.",
        "total_items": total_items,
        "total_price": f"${total_price:,.0f}".replace(",", "."),
    })

@login_required
def actualizar_cantidad(request, detalle_id):
    if not es_usuario_publico(request.user):
        return redirect('admin_login')
    
    if request.method == "POST":
        # Obtén el detalle del carrito
        detalle = get_object_or_404(DetalleCarrito, id=detalle_id, carrito__usuario=request.user)
        
        try:
            # Parsear la cantidad desde el JSON del request
            data = json.loads(request.body)
            nueva_cantidad = int(data.get("cantidad", 1))
        except (ValueError, TypeError):
            return JsonResponse({"error": "Cantidad inválida."}, status=400)

        if nueva_cantidad <= 0:
            return JsonResponse({"error": "La cantidad debe ser mayor a 0."}, status=400)

        if nueva_cantidad > detalle.producto.stock:
            return JsonResponse({"error": f"Solo puedes añadir hasta {detalle.producto.stock} unidades.", "max_stock": detalle.producto.stock}, status=400)

        # Actualiza la cantidad en el detalle
        detalle.cantidad = nueva_cantidad
        detalle.save()

        # Calcula los totales
        carrito = detalle.carrito
        total_price = carrito.obtener_total()
        total_price_with_iva = carrito.obtener_total_con_iva()
        total_items = sum(item.cantidad for item in carrito.detalles.all())

        # Respuesta JSON
        return JsonResponse({
            "message": "Cantidad actualizada.",
            "total_items": total_items,
            "total_price": total_price,  
            "total_price_with_iva": total_price_with_iva,
            "max_stock": detalle.producto.stock  # Enviamos el stock máximo como referencia
        })

    return JsonResponse({"error": "Método no permitido."}, status=405)

@login_required
def eliminar_producto_carrito(request, detalle_id):
    if not es_usuario_publico(request.user):
        return redirect('admin_login')
    
    detalle = get_object_or_404(DetalleCarrito, id=detalle_id, carrito__usuario=request.user)
    detalle.delete()

    carrito = detalle.carrito
    total_price = carrito.obtener_total()
    total_items = sum(item.cantidad for item in carrito.detalles.all())

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            "message": "Producto eliminado.",
            "total_items": total_items,
            "total_price": f"${total_price:,.0f} CLP",
        })

    messages.success(request, "Producto eliminado del carrito.")
    return redirect('ver_carrito')

@login_required
def obtener_detalles_carrito(request):
    if not es_usuario_publico(request.user):
        return redirect('admin_login')
    
    carrito = Carrito.objects.prefetch_related("detalles__producto").get(usuario=request.user)
    detalles = [
        {
            "id": detalle.id,
            "nombre": detalle.producto.nombre,
            "cantidad": detalle.cantidad,
            "precio": f"${detalle.producto.precio:,.0f}".replace(",", "."),
        }
        for detalle in carrito.detalles.all()
    ]
    total_precio = f"${carrito.obtener_total():,.0f}".replace(",", ".")
    total_cantidad = sum(detalle.cantidad for detalle in carrito.detalles.all())

    return JsonResponse({"detalles": detalles, "total_precio": total_precio, "total_cantidad": total_cantidad})

#------------------------------------------------------------------------------------------------------
#-------------------  VISTAS para el modal de cada producto (base.html) -------------------------------
#------------------------------------------------------------------------------------------------------
def producto_detalle(request, producto_id):
    if not es_usuario_publico(request.user):
        return redirect('admin_login')
    
    """
    Devuelve los detalles de un producto en formato JSON.
    """
    producto = get_object_or_404(Producto, id=producto_id)
    data = {
        "id": producto.id,
        "nombre": producto.nombre,
        "precio": f"${int(producto.precio):,}".replace(",", "."),
        "stock": producto.stock,
        "disponibilidad": "Disponible" if producto.stock > 0 else "No Disponible",
        "descripcion": producto.descripcion if producto.descripcion else "",
        "imagen": producto.imagen.url,
    }
    return JsonResponse(data)

#------------------------------------------------------------------------------------------------------
#-------------------  VISTAS PARA FINALIZAR COMPRA (finalizar_compra.html) ----------------------------
#------------------------------------------------------------------------------------------------------

@login_required
def finalizar_compra(request):
    if not es_usuario_publico(request.user):
        return redirect('admin_login')
    
    try:
        carrito = Carrito.objects.prefetch_related('detalles__producto').get(usuario=request.user)
        detalles = carrito.detalles.all()
        detalles_con_totales = []
        for detalle in detalles:
            detalles_con_totales.append({
                "producto": detalle.producto,
                "cantidad": detalle.cantidad,
                "total": formatear_precio_clp(detalle.producto.precio * detalle.cantidad)
            })
        total = formatear_precio_clp(carrito.obtener_total())
        total_con_iva = formatear_precio_clp(carrito.obtener_total_con_iva())
        direccion = request.user.direccion  # Campo dirección del usuario
    except Carrito.DoesNotExist:
        detalles_con_totales = []
        total = formatear_precio_clp(0)
        total_con_iva = formatear_precio_clp(0)
        direccion = "No hay dirección registrada."

    return render(request, 'catalogo/finalizar_compra.html', {
        'detalles': detalles_con_totales,
        'total': total,
        'total_con_iva': total_con_iva,
        'direccion': direccion,
    })

@login_required
def actualizar_direccion(request):
    if not es_usuario_publico(request.user):
        return redirect('admin_login')
    
    if request.method == 'POST':
        nueva_direccion = request.POST.get('direccion', '').strip()

        if nueva_direccion:
            # Guardar la nueva dirección
            request.user.direccion = nueva_direccion
            request.user.save()
            messages.success(request, "Dirección actualizada correctamente.")
        else:
            messages.error(request, "La dirección no puede estar vacía.")

        return redirect('finalizar_compra')
    return JsonResponse({'error': 'Método no permitido.'}, status=405)


#------------------------------------------------------------------------------------------------------
#-------------------  VISTAS PARA EL PROCESO DE PAGO CON PAYPAL ---------------------------------------
#------------------------------------------------------------------------------------------------------
from django.views.decorators.csrf import csrf_exempt
from .paypal_config import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_ENVIRONMENT
import requests

def crear_orden_paypal(request):
    if request.method == "POST":
        try:
            # Obtener token de acceso de PayPal
            auth_url = f"https://api-m.{PAYPAL_ENVIRONMENT}.paypal.com/v1/oauth2/token"
            auth_response = requests.post(auth_url, auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET), data={"grant_type": "client_credentials"})
            
            if auth_response.status_code != 200:
                return JsonResponse({"error": "Error al obtener token de PayPal."}, status=500)

            access_token = auth_response.json().get("access_token")
            if not access_token:
                return JsonResponse({"error": "No se pudo obtener el token de acceso de PayPal."}, status=500)

            # Crear una orden de PayPal
            create_order_url = f"https://api-m.{PAYPAL_ENVIRONMENT}.paypal.com/v2/checkout/orders"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
            body = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": "USD",
                            "value": "100.00",  # Cambia este valor al total dinámico
                        }
                    }
                ]
            }
            response = requests.post(create_order_url, headers=headers, json=body)

            if response.status_code != 201:
                return JsonResponse({"error": "Error al crear orden en PayPal."}, status=500)

            return JsonResponse(response.json())
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def capturar_orden_paypal(request, order_id):
    if request.method == "POST":
        try:
            carrito = Carrito.objects.get(usuario=request.user)

            # Obtener token de acceso de PayPal
            auth_url = f"https://api-m.{PAYPAL_ENVIRONMENT}.paypal.com/v1/oauth2/token"
            auth_response = requests.post(auth_url, auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET), data={"grant_type": "client_credentials"})
            
            if auth_response.status_code != 200:
                return JsonResponse({"error": "Error al obtener token de PayPal."}, status=500)

            access_token = auth_response.json().get("access_token")
            if not access_token:
                return JsonResponse({"error": "No se pudo obtener el token de acceso de PayPal."}, status=500)

            # Capturar orden
            capture_url = f"https://api-m.{PAYPAL_ENVIRONMENT}.paypal.com/v2/checkout/orders/{order_id}/capture"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
            response = requests.post(capture_url, headers=headers)
            capture_data = response.json()

            # Crear pedido y detalle del pedido en la base de datos
            pedido = Pedido.objects.create(usuario=request.user, total=carrito.obtener_total_con_iva())
            for detalle in carrito.detalles.all():
                # Reducir el stock del producto
                if detalle.producto.stock < detalle.cantidad:
                    return JsonResponse({"error": f"Stock insuficiente para el producto {detalle.producto.nombre}."}, status=400)
                
                detalle.producto.stock -= detalle.cantidad
                detalle.producto.save()

                # Crear el detalle del pedido
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=detalle.producto,
                    cantidad=detalle.cantidad,
                    precio_unitario=detalle.producto.precio,
                )

            # Registrar la transacción
            Transaccion.objects.create(
                pedido=pedido,
                metodo_pago="PayPal",
                monto=carrito.obtener_total_con_iva(),
            )

            # Vaciar el carrito
            carrito.detalles.all().delete()

            return JsonResponse({"success": True, "pedido_id": pedido.id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


def agradecimiento(request):
    return render(request, "catalogo/agradecimiento.html")





#------------------------------------------------------------------------------------------------------
#-------------------  VISTAS PARA EL PANEL DE ADMINISTRACION (admin_panel.html) -----------------------
#------------------------------------------------------------------------------------------------------
def admin_login(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # Validaciones del lado del servidor
        if not email or not password:
            messages.error(request, "Correo y contraseña son requeridos.")
            return render(request, 'admin_panel/login_admin.html')

        # Validar formato de correo electrónico
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            messages.error(request, "El formato del correo electrónico no es válido.")
            return render(request, 'admin_panel/login_admin.html')

        # Validar dominio específico
        if not email.endswith('@miempresa.com'):
            messages.error(request, "El correo debe pertenecer al dominio 'miempresa.com'.")
            return render(request, 'admin_panel/login_admin.html')

        # Autenticación
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if user.rol == 'administrador':
                return redirect('admin_dashboard')
            elif user.rol == 'vendedor':
                return redirect('listar_productos')
            elif user.rol == 'empleado_postventa':
                return redirect('ordenes')
            else:
                messages.error(request, "No tiene permisos para acceder al panel.")
        else:
            # Manejo de errores específicos
            if not Usuario.objects.filter(email=email).exists():
                messages.error(request, "El correo no está registrado.")
            else:
                messages.error(request, "La contraseña es incorrecta.")
            return render(request, 'admin_panel/login_admin.html')

    return render(request, 'admin_panel/login_admin.html')


def admin_logout(request):
    logout(request)
    return redirect('home')  

# Vista del panel de administración
def admin_dashboard(request):
    user_roles = {
        'is_admin_or_vendor': request.user.rol in ['administrador', 'vendedor'],
        'is_admin_or_postventa': request.user.rol in ['administrador', 'empleado_postventa'],
        'is_admin': request.user.rol == 'administrador',
    }
    return render(request, 'admin_panel/dashboard.html', user_roles)

# Vista para listar usuarios y filtrar por roles
@role_required(['administrador'])
def listar_usuarios(request):
    rol_filtrado = request.GET.get('rol')  # Captura el filtro del rol desde la URL
    if rol_filtrado == 'vendedor':
        usuarios = Usuario.objects.filter(rol='vendedor')
    elif rol_filtrado == 'empleado_postventa':
        usuarios = Usuario.objects.filter(rol='empleado_postventa')
    else:  # Mostrar todos los vendedores y empleados_postventa
        usuarios = Usuario.objects.filter(rol__in=['vendedor', 'empleado_postventa'])

    context = {
        'usuarios': usuarios,
        'rol_filtrado': rol_filtrado,  # Pasar el rol filtrado al contexto para resaltar el botón activo
    }
    return render(request, 'admin_panel/listar_usuarios.html', context)

# Gestión de usuarios (solo para administradores)
@role_required(['administrador'])
def agregar_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        contraseña = request.POST.get('contraseña')
        rol = request.POST.get('rol')

        # Validación del nombre
        if len(nombre) > 100:
            messages.error(request, 'El nombre no puede superar los 100 caracteres.')
            return redirect('agregar_usuario')

        # Validación del correo
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            messages.error(request, 'El formato del correo es inválido. Asegúrate de incluir un dominio válido.')
            return redirect('agregar_usuario')

        # Validación de duplicados de correo
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'El correo ya está registrado.')
            return redirect('agregar_usuario')

        # Validación de la contraseña
        if len(contraseña) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return redirect('agregar_usuario')

        if not any(char.isdigit() for char in contraseña):
            messages.error(request, 'La contraseña debe contener al menos un número.')
            return redirect('agregar_usuario')

        if not any(char in "!@#$%^&*()-_=+[]{};:,.<>?" for char in contraseña):
            messages.error(request, 'La contraseña debe contener al menos un carácter especial (!@#$%^&* etc.).')
            return redirect('agregar_usuario')

        # Validación del rol
        if rol not in ['vendedor', 'empleado_postventa']:
            messages.error(request, 'Rol no válido.')
            return redirect('agregar_usuario')

        # Crear el usuario
        Usuario.objects.create_user(email=email, password=contraseña, nombre=nombre, rol=rol)
        messages.success(request, 'Usuario creado exitosamente.')

        return redirect('listar_usuarios')

    return render(request, 'admin_panel/agregar_usuario.html')

# Gestión de productos (administradores y vendedores)
@role_required(['administrador', 'vendedor'])
def listar_productos(request):
    productos = Producto.objects.all()  # Consulta para obtener todos los productos
    return render(request, 'admin_panel/productos.html', {'productos': productos})

@role_required(['administrador', 'vendedor'])
def crear_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre').strip()
        precio_formateado = request.POST.get('precio').strip()  # Precio con formato CLP
        stock = request.POST.get('stock').strip()
        categoria = request.POST.get('categoria').strip()
        descripcion = request.POST.get('descripcion').strip()
        imagen = request.FILES.get('imagen')  # Imagen si se sube

        # Validaciones avanzadas
        errores = []
        if not nombre:
            errores.append('El nombre del producto no puede estar vacío.')
        if len(nombre) > 100:
            errores.append('El nombre del producto no puede superar los 100 caracteres.')

        try:
            precio_limpio = float(precio_formateado.replace('$', '').replace('.', '').replace(',', '.'))
            if precio_limpio <= 0:
                errores.append('El precio debe ser un número positivo.')
        except ValueError:
            errores.append('El precio debe ser un número válido.')

        try:
            stock_int = int(stock)
            if stock_int < 0:
                errores.append('El stock no puede ser negativo.')
        except ValueError:
            errores.append('El stock ingresado no es válido.')

        if len(descripcion) > 1000:
            errores.append('La descripción no puede superar los 1000 caracteres.')

        # Validación de categoría
        categorias_validas = [c[0] for c in Producto._meta.get_field('categoria').choices]
        if categoria not in categorias_validas:
            errores.append('La categoría seleccionada no es válida.')

        if Producto.objects.filter(nombre=nombre, categoria=categoria).exists():
            errores.append('Ya existe un producto con el mismo nombre en esta categoría.')

        if imagen:
            if imagen.size > 5 * 1024 * 1024:
                errores.append('La imagen no debe superar los 5 MB.')
            if not imagen.name.endswith(('.png', '.jpg', '.jpeg')):
                errores.append('Solo se admiten imágenes en formato JPG o PNG.')

        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'admin_panel/crear_producto.html')

        # Crear el producto con el precio limpio y demás datos validados
        Producto.objects.create(
            nombre=nombre,
            precio=precio_limpio,
            stock=stock_int,
            categoria=categoria,
            descripcion=descripcion,
            imagen=imagen
        )
        messages.success(request, 'Producto creado exitosamente.')
        return redirect('listar_productos')

    return render(request, 'admin_panel/crear_producto.html')

@role_required(['administrador', 'vendedor'])
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('listar_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'admin_panel/editar_producto.html', {'form': form, 'producto': producto})

@role_required(['administrador', 'vendedor'])
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('listar_productos')
    return render(request, 'admin_panel/eliminar_producto.html', {'producto': producto})

# Editar usuarios (solo administradores)
@role_required(['administrador'])
def edit_user(request, user_id):
    user_to_edit = get_object_or_404(Usuario, pk=user_id)

    if request.method == 'POST':
        nombre = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        rol = request.POST.get('role', '').strip()

        # Validaciones
        if len(nombre) > 100:
            messages.error(request, 'El nombre no puede superar los 100 caracteres.')
            return redirect('edit_user', user_id=user_id)

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            messages.error(request, 'El formato del correo es inválido.')
            return redirect('edit_user', user_id=user_id)

        if Usuario.objects.filter(email=email).exclude(pk=user_id).exists():
            messages.error(request, 'El correo ya está registrado.')
            return redirect('edit_user', user_id=user_id)

        # Validar que solo se pueda asignar "vendedor" o "empleado_postventa"
        if rol not in ['vendedor', 'empleado_postventa']:
            messages.error(request, 'Rol no válido. Solo se permite "Vendedor" o "Empleado Postventa".')
            return redirect('edit_user', user_id=user_id)

        # Guardar cambios
        user_to_edit.nombre = nombre
        user_to_edit.email = email
        user_to_edit.rol = rol
        user_to_edit.save()
        messages.success(request, 'Usuario actualizado con éxito.')
        return redirect('listar_usuarios')

    return render(request, 'admin_panel/editar_usuario.html', {'user_to_edit': user_to_edit})

# Eliminar usuarios (solo administradores)
@role_required(['administrador'])
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(Usuario, pk=user_id)

    if request.method == 'POST':
        user_to_delete.delete()
        messages.success(request, 'Usuario eliminado con éxito.')
        return redirect('listar_usuarios')

    return render(request, 'admin_panel/eliminar_usuario.html', {
        'user': user_to_delete,  # Usuario que se está eliminando
        'request_user': request.user  # Usuario autenticado
    })
    
    
#------------------------------------------------------------------------------------------------------
#-------------  VISTAS PARA ORDENES Y TRANSACCIONES DEL PANEL DE ADMINISTRACION -----------------------
#------------------------------------------------------------------------------------------------------

# Gestión de órdenes (todos los roles permitidos)
@role_required(['administrador', 'vendedor', 'empleado_postventa'])
def ordenes(request):
    
    pedidos_preparacion = Pedido.objects.filter(estado='preparacion')
    pedidos_transito = Pedido.objects.filter(estado='transito')
    pedidos_finalizado = Pedido.objects.filter(estado='finalizado')

    # Formatear precios
    for pedido in pedidos_preparacion:
        pedido.total_formateado = formatear_precio_clp(pedido.total)
    for pedido in pedidos_transito:
        pedido.total_formateado = formatear_precio_clp(pedido.total)
    for pedido in pedidos_finalizado:
        pedido.total_formateado = formatear_precio_clp(pedido.total)

    return render(request, 'admin_panel/ordenes.html', {
        'pedidos_preparacion': pedidos_preparacion,
        'pedidos_transito': pedidos_transito,
        'pedidos_finalizado': pedidos_finalizado,
    })

@role_required(['administrador', 'empleado_postventa'])
def ver_detalles_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = pedido.detallepedido_set.all()

    detalles_con_subtotal = []
    for detalle in detalles:
        subtotal = detalle.cantidad * detalle.precio_unitario
        detalles_con_subtotal.append({
            "producto": detalle.producto,
            "cantidad": detalle.cantidad,
            "precio_unitario_formateado": formatear_precio_clp(detalle.precio_unitario),
            "subtotal_formateado": formatear_precio_clp(subtotal),
        })

    return render(request, "admin_panel/detalles_pedido.html", {
        "pedido": pedido,
        "detalles": detalles_con_subtotal,
        "total_formateado": formatear_precio_clp(pedido.total),
    })

@role_required(['administrador', 'empleado_postventa'])
def actualizar_estado_pedido(request, pedido_id):
    if request.method == "POST":
        pedido = get_object_or_404(Pedido, id=pedido_id)
        nuevo_estado = request.POST.get("estado")
        if nuevo_estado in ["preparacion", "transito", "finalizado"]:
            pedido.estado = nuevo_estado
            pedido.save()
            return JsonResponse({"mensaje": "Estado actualizado correctamente"})
        return JsonResponse({"error": "Estado inválido"}, status=400)
    return JsonResponse({"error": "Método no permitido"}, status=405)


# Gestión de transacciones (solo administradores)
@role_required(['administrador'])
def listar_transacciones(request):
    if request.user.rol != "administrador":  # Asegurarse de que solo el admin acceda
        return redirect("admin_dashboard")
    
    transacciones = Transaccion.objects.all()

    # Formatear los montos
    for transaccion in transacciones:
        transaccion.monto_formateado = formatear_precio_clp(transaccion.monto)

    return render(request, "admin_panel/transacciones.html", {
        "transacciones": transacciones,
    })