document.addEventListener('DOMContentLoaded', function () {
    // ==============================
    // Confirmación para eliminar
    // ==============================
    const deleteButtons = document.querySelectorAll('.btn-delete');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            const confirmDelete = confirm('¿Estás seguro de que deseas eliminar este elemento?');
            if (!confirmDelete) {
                event.preventDefault();
            }
        });
    });

    // ==============================
    // Ocultar mensajes de éxito automáticamente después de unos segundos
    // ==============================
    const successMessage = document.querySelector('.success-message');
    if (successMessage) {
        setTimeout(() => {
            successMessage.style.display = 'none';
        }, 5000); // Ocultar mensaje después de 5 segundos
    }

    // ==============================
    // Manejo de pestañas para Administración de Productos
    // ==============================
    function initProductosTabs() {
        const productosTabs = document.querySelectorAll('.productos-tabs-container a'); // Selección de pestañas de productos
        const productosTabContents = document.querySelectorAll('.productos-tab-content'); // Contenidos de pestañas de productos

        if (productosTabs.length > 0) {
            productosTabs.forEach(tab => {
                tab.addEventListener('click', function (event) {
                    event.preventDefault();

                    // Desactivar todas las pestañas y secciones
                    productosTabs.forEach(t => t.classList.remove('tab-active'));
                    productosTabContents.forEach(content => content.classList.remove('active-tab'));

                    // Activar la pestaña y la sección correspondiente
                    this.classList.add('tab-active');
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) target.classList.add('active-tab');
                });
            });
        }
    }

    // ==============================
    // Manejo de pestañas para Órdenes de Compra
    // ==============================
    const orderTabs = document.querySelectorAll('.tabs-container a.tab-link'); // Pestañas de órdenes
    const orderTabContents = document.querySelectorAll('.tab-content'); // Contenido de pestañas de órdenes

    orderTabs.forEach(tab => {
        tab.addEventListener('click', function (event) {
            event.preventDefault(); // Prevenir comportamiento predeterminado
            orderTabs.forEach(t => t.classList.remove('tab-active')); // Quitar clase activa de todas las pestañas
            orderTabContents.forEach(content => content.classList.remove('active-tab')); // Quitar contenido activo

            this.classList.add('tab-active'); // Activar pestaña seleccionada
            const targetId = this.getAttribute('href').substring(1); // Obtener ID del contenido
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add('active-tab'); // Mostrar contenido correspondiente
            }
        });
    });

    // Mostrar la primera pestaña por defecto si no hay ninguna activa
    if (orderTabs.length > 0 && orderTabContents.length > 0) {
        orderTabs[0].classList.add('tab-active');
        orderTabContents[0].classList.add('active-tab');
    }

    // ==============================
    // Manejo de pestañas para Gestión de Usuarios
    // ==============================
    function initUsuariosTabs() {
        const usuariosTabs = document.querySelectorAll('.tabs-container a'); // Pestañas de usuarios
        const usuariosTabContents = document.querySelectorAll('.tab-content'); // Contenidos de pestañas de usuarios

        usuariosTabs.forEach(tab => {
            tab.addEventListener('click', function (event) {
                event.preventDefault(); // Prevenir comportamiento predeterminado
                usuariosTabs.forEach(t => t.classList.remove('tab-active')); // Quitar clase activa de todas las pestañas
                usuariosTabContents.forEach(content => content.classList.remove('active-tab')); // Quitar contenido activo

                this.classList.add('tab-active'); // Activar pestaña seleccionada
                const targetId = this.getAttribute('href').substring(1); // Obtener ID del contenido
                const targetContent = document.getElementById(targetId);
                if (targetContent) {
                    targetContent.classList.add('active-tab'); // Mostrar contenido correspondiente
                }
            });
        });

        // Mostrar la primera pestaña por defecto si no hay ninguna activa
        if (usuariosTabs.length > 0 && usuariosTabContents.length > 0) {
            usuariosTabs[0].classList.add('tab-active');
            usuariosTabContents[0].classList.add('active-tab');
        }
    }

    // ==============================
    // Inicializar funciones
    // ==============================
    initProductosTabs(); // Inicializar pestañas de productos
    initOrdenesTabs(); // Inicializar pestañas de órdenes
    initUsuariosTabs(); // Inicializar pestañas de usuarios
});

// Validacion del formulario de AGREGAR USUARIO
document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.add-user-form');
    const emailField = document.getElementById('id_email');
    const passwordField = document.getElementById('id_contraseña');

    form.addEventListener('submit', function (event) {
        // Validar email
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailRegex.test(emailField.value)) {
            alert('El correo electrónico no es válido. Por favor, incluye un dominio válido.');
            event.preventDefault();
            return;
        }

        // Validar contraseña
        const password = passwordField.value;
        if (password.length < 8) {
            alert('La contraseña debe tener al menos 8 caracteres.');
            event.preventDefault();
            return;
        }

        if (!/[0-9]/.test(password)) {
            alert('La contraseña debe contener al menos un número.');
            event.preventDefault();
            return;
        }

        if (!/[!@#$%^&*()-_=+[\]{};:,.<>?]/.test(password)) {
            alert('La contraseña debe contener al menos un carácter especial (!@#$%^&* etc.).');
            event.preventDefault();
            return;
        }
    });
});

// Validacion del formulario de AGREGAR PRODUCTO
document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.add-product-form');
    form.addEventListener('submit', function (event) {
        const nombre = document.getElementById('id_nombre').value;
        const descripcion = document.getElementById('id_descripcion').value;
        const precio = document.getElementById('id_precio').value.replace(/[^0-9]/g, '');
        const stock = document.getElementById('id_stock').value;

        let errores = [];

        if (nombre.length > 100) {
            errores.push('El nombre del producto no puede superar los 100 caracteres.');
        }

        if (descripcion.length > 1000) {
            errores.push('La descripción no puede superar los 1000 caracteres.');
        }

        if (parseFloat(precio) <= 0 || isNaN(parseFloat(precio))) {
            errores.push('El precio debe ser un número positivo.');
        }

        if (parseInt(stock) < 0 || parseInt(stock) > 99 || isNaN(parseInt(stock))) {
            errores.push('El stock debe ser un número entre 0 y 99.');
        }

        if (errores.length > 0) {
            alert('Errores:\n' + errores.join('\n'));
            event.preventDefault(); // Evitar que el formulario se envíe
        }
    });

    // Formatear campo de precio como moneda chilena
    const precioInput = document.getElementById('id_precio');
    if (precioInput) {
        precioInput.addEventListener('input', function () {
            let value = precioInput.value.replace(/[^0-9]/g, ''); // Mantener solo números
            if (value) {
                value = new Intl.NumberFormat('es-CL', {
                    style: 'currency',
                    currency: 'CLP',
                    maximumFractionDigits: 0
                }).format(value);
            }
            precioInput.value = value; // Actualizar el valor del campo
        });
    }
});

// Validacion del formulario de EDITAR PRODUCTO
document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const precioInput = document.getElementById('precio');

    form.addEventListener('submit', function (event) {
        const nombre = document.getElementById('nombre').value;
        const descripcion = document.getElementById('descripcion').value;
        let precio = precioInput.value.replace(/\D/g,''); // Elimina todo lo que no sea dígitos
        const stock = document.getElementById('stock').value;

        let errores = [];

        if (nombre.length > 100) {
            errores.push('El nombre del producto no puede superar los 100 caracteres.');
        }

        if (descripcion.length > 1000) {
            errores.push('La descripción no puede superar los 1000 caracteres.');
        }

        if (parseFloat(precio) <= 0 || isNaN(parseFloat(precio))) {
            errores.push('El precio debe ser un número positivo.');
        }

        if (parseInt(stock) < 0 || parseInt(stock) > 99 || isNaN(parseInt(stock))) {
            errores.push('El stock debe ser un número entre 0 y 99.');
        }

        if (errores.length > 0) {
            alert('Errores:\n' + errores.join('\n'));
            event.preventDefault(); // Evitar que el formulario se envíe
        } else {
            precioInput.value = precio; // Asegura que el valor enviado es solo numérico
        }
    });

    // Formatear campo de precio como moneda chilena durante la entrada
    if (precioInput) {
        precioInput.addEventListener('input', function () {
            let value = this.value.replace(/\D/g, ''); // Mantener solo números
            if (value) {
                value = new Intl.NumberFormat('es-CL', {
                    style: 'currency',
                    currency: 'CLP',
                    maximumFractionDigits: 0
                }).format(parseInt(value));
            }
            this.value = value; // Actualizar el valor del campo con formato
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const editForm = document.querySelector('.edit-user-form');
    const roleField = document.getElementById('id_rol');

    if (roleField) {
        // Eliminar la opción "Administrador" si accidentalmente está en el HTML
        [...roleField.options].forEach(option => {
            if (option.value === 'administrador') {
                option.remove();
            }
        });
    }

    if (editForm) {
        const emailField = document.getElementById('id_email');
        const nameField = document.getElementById('id_nombre');
        const roleField = document.getElementById('id_rol');

        editForm.addEventListener('submit', function (event) {
            let errores = [];

            // Validar Nombre
            if (nameField.value.trim().length > 100) {
                errores.push('El nombre no puede superar los 100 caracteres.');
            }

            // Validar Correo Electrónico
            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailRegex.test(emailField.value.trim())) {
                errores.push('El correo electrónico no es válido. Por favor, incluye un dominio válido.');
            }

            // Validar Rol
            const validRoles = ['vendedor', 'empleado_postventa', 'administrador'];
            if (!validRoles.includes(roleField.value.trim())) {
                errores.push('Selecciona un rol válido.');
            }

            // Mostrar Errores
            if (errores.length > 0) {
                alert('Errores:\n' + errores.join('\n'));
                event.preventDefault(); // Detener envío del formulario
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.querySelector('form');

    if (loginForm) {
        loginForm.addEventListener('submit', function (event) {
            const emailField = document.getElementById('email');
            const passwordField = document.getElementById('password');
            let errores = [];

            // Validar correo electrónico
            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailRegex.test(emailField.value.trim())) {
                errores.push('El correo electrónico no es válido.');
            }

            // Validar dominio específico
            if (!emailField.value.trim().endsWith('@miempresa.com')) {
                errores.push('El correo debe pertenecer al dominio "miempresa.com".');
            }

            // Validar contraseña
            if (passwordField.value.trim().length < 8) {
                errores.push('La contraseña debe tener al menos 8 caracteres.');
            }

            // Mostrar errores
            if (errores.length > 0) {
                alert('Errores:\n' + errores.join('\n'));
                event.preventDefault(); // Detener envío del formulario
            }
        });
    }
});
