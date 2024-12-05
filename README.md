# New House Dreams SPA - Venta de Casas Prefabricadas

¡Bienvenido al proyecto **New House Dreams SPA**! Este sistema de e-commerce está diseñado para la venta de casas prefabricadas, ofreciendo una plataforma eficiente y moderna que cumple con las mejores prácticas de desarrollo web. Incluye funcionalidades como gestión de usuarios, carrito de compras, seguimiento de pedidos y más.

## 📜 Descripción del Proyecto

Este proyecto está desarrollado en **Django**, implementando el modelo MVC para garantizar una separación clara entre las vistas, la lógica de negocio y el modelo de datos. Además, cuenta con una interfaz responsiva y adaptable, lo que lo hace funcional en diferentes dispositivos.

---

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 4.0.1, Python
- **Frontend**: HTML5, CSS3, Bootstrap
- **Base de Datos**: MySQL
- **Control de Versiones**: Git y GitHub
- **Librerías**:
  - `django-widget-tweaks`
  - `requests`

---

## 🚀 Funcionalidades Principales

### Cliente:
1. Registro e inicio de sesión.
2. Visualización de catálogo de productos.
3. Gestión del carrito de compras.
4. Realización de compras (incluyendo integración con PayPal).
5. Seguimiento de pedidos.

### Administrador:
1. Gestión de productos (agregar, editar, eliminar).
2. Gestión de usuarios.
3. Visualización de transacciones.
4. Actualización de estados de pedidos.

---

## 📋 Requisitos Previos

1. **Instalar Python**: Asegúrate de tener Python 3.9 o superior instalado en tu máquina.
2. **Base de datos MySQL**: Configura MySQL con el usuario y contraseña definidos.

---

## 🔧 Cómo Iniciar el Proyecto

### Paso 1: Configuración de la Base de Datos
1. Revisa el archivo `settings.py` y actualiza la configuración de la base de datos si es necesario:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'casasprefabricadas',
           'USER': 'root',  # Ajusta según tu configuración
           'PASSWORD': 'root',  # Ajusta según tu configuración
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }

## Abre tu gestor de base de datos y ejecuta los siguientes comandos SQL:
CREATE DATABASE Casasprefabricadas CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE Casasprefabricadas;


## Preparar las Migraciones
Dirígete a la carpeta del proyecto donde se encuentra el archivo manage.py.
Ejecuta los siguientes comandos en tu terminal:
python manage.py makemigrations
python manage.py migrate

## Iniciar el Servidor
Ejecuta:
python manage.py runserver

Accede al proyecto desde tu navegador en: http://127.0.0.1:8000

## Instalar Dependencias
Instala las siguientes librerías:
pip install django-widget-tweaks
pip install requests

