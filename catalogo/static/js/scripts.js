//-----------------------------------------------------------------------------------------------------------
//--------------------------------- JAVA PARA EL FORMULARIO DE REGISTRO -------------------------------------
//-----------------------------------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.querySelector(".registro-container form");

    // Validación del formulario de registro
    if (registerForm) {
        registerForm.addEventListener("submit", function (e) {
            const nombre = document.querySelector("#id_nombre").value.trim();
            const email = document.querySelector("#id_email").value.trim();
            const direccion = document.querySelector("#id_direccion").value.trim();
            const telefono = document.querySelector("#id_telefono").value.trim();
            const password = document.querySelector("#id_password").value;
            const passwordConfirm = document.querySelector("#id_confirm_password").value;

            // Validar Nombre
            if (nombre.length < 3 || nombre.length > 100 || !/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(nombre)) {
                e.preventDefault();
                alert("El nombre debe tener entre 3 y 100 caracteres y solo puede contener letras.");
                return;
            }

            // Validar Correo Electrónico
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                e.preventDefault();
                alert("Ingrese un correo electrónico válido (e.g., ejemplo@dominio.com).");
                return;
            }

            // Validar Dirección
            if (direccion.length === 0 || direccion.length > 255) {
                e.preventDefault();
                alert("La dirección es obligatoria y no debe superar los 255 caracteres.");
                return;
            }

            // Validar Teléfono
            const phoneRegex = /^\+?\d{7,15}$/;
            if (!phoneRegex.test(telefono)) {
                e.preventDefault();
                alert("El número de teléfono debe contener entre 7 y 15 dígitos, opcionalmente con un prefijo '+'.");
                return;
            }

            // Validar Contraseñas (Confirmación)
            if (password !== passwordConfirm) {
                e.preventDefault();
                alert("Las contraseñas no coinciden.");
                return;
            }

            // Validar Contraseña (Reglas de Seguridad)
            const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()\-_=+])[A-Za-z\d!@#$%^&*()\-_=+]{8,}$/;
            if (!passwordRegex.test(password)) {
                e.preventDefault();
                alert(
                    "La contraseña debe tener al menos 8 caracteres, una letra mayúscula, un número y un carácter especial."
                );
                return;
            }
        });
    }

    // Mostrar modal de éxito en registro
    const successMessage = document.querySelector(".alert-success");
    if (successMessage) {
        const modal = new bootstrap.Modal(document.getElementById("successModal"));
        modal.show();
    }
});


//-----------------------------------------------------------------------------------------------------------
//------------------------------------ JAVA PARA EL FORMULARIO DE LOGIN -------------------------------------
//-----------------------------------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
    // Selección de elementos comunes
    const carritoCantidad = document.querySelector(".cart-badge");
    const totalItemsElement = document.getElementById("carrito-total-items");
    const totalElement = document.getElementById("carrito-total-sin-iva");
    const totalIVAElement = document.getElementById("carrito-total-iva");
    const navTotalElement = document.querySelector("#carrito-icon #carrito-total"); // Total en el nav

    // Función para actualizar los valores visuales del carrito
    function actualizarCarritoVisual(totalItems, totalPrice, totalPriceWithIVA) {
        if (carritoCantidad) {
            carritoCantidad.textContent = totalItems || 0;
        }
        if (totalItemsElement) {
            totalItemsElement.textContent = totalItems || 0;
        }
        if (totalElement) {
            totalElement.textContent = formatPriceCLP(totalPrice || 0); // Total sin IVA
        }
        if (totalIVAElement) {
            totalIVAElement.textContent = formatPriceCLP(totalPriceWithIVA || 0); // Total con IVA
        }
        if (navTotalElement) {
            navTotalElement.textContent = formatPriceCLP(totalPrice || 0); // Total en el nav
        }
    }

    // Función para formatear un número como pesos chilenos (CLP)
    function formatPriceCLP(price) {
        // Asegurarse de que no haya doble símbolo "$"
        if (typeof price === "string" && price.trim().startsWith("$")) {
            return price;
        }
        return `$${parseFloat(price).toLocaleString("es-CL", {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        })}`;
    }

    // Función para obtener el token CSRF
    function getCsrfToken() {
        const token = document.querySelector("[name=csrfmiddlewaretoken]");
        return token ? token.value : "";
    }

    // Función para manejar errores del servidor
    function manejarError(error, input, maxStock) {
        alert(error || "Error al procesar la solicitud.");
        if (input && maxStock) {
            input.value = maxStock; // Restablece al máximo permitido
        }
    }

    // Formatear los valores del carrito al cargar la página
    function inicializarValoresCarrito() {
        if (navTotalElement) {
            const rawTotal = navTotalElement.getAttribute("data-raw-total");
            if (rawTotal) {
                navTotalElement.textContent = formatPriceCLP(rawTotal);
            }
        }
        if (totalElement) {
            const rawTotalSinIVA = totalElement.getAttribute("data-raw-total");
            if (rawTotalSinIVA) {
                totalElement.textContent = formatPriceCLP(rawTotalSinIVA);
            }
        }
        if (totalIVAElement) {
            const rawTotalConIVA = totalIVAElement.getAttribute("data-raw-total");
            if (rawTotalConIVA) {
                totalIVAElement.textContent = formatPriceCLP(rawTotalConIVA);
            }
        }
    }

    // Inicializar valores del carrito al cargar la página
    inicializarValoresCarrito();

    // Evento para "Añadir al carrito"
    document.querySelectorAll(".add-to-cart-btn").forEach((button) => {
        button.addEventListener("click", function (e) {
            e.preventDefault();
            const productoId = this.dataset.productoId;
    
            fetch(`/carrito/agregar/${productoId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCsrfToken(),
                },
            })
                .then((response) => {
                    if (response.status === 302 || response.redirected) {
                        // Si el servidor responde con una redirección, redirigir al usuario
                        window.location.href = "/login/?next=" + encodeURIComponent(window.location.pathname);
                        return;
                    }
                    if (response.status === 401) {
                        // Si el usuario no está autenticado, redirigir al login
                        window.location.href = "/login/";
                        return;
                    }
                    if (response.ok) {
                        return response.json();
                    } else {
                        return response.json().then((data) => {
                            throw new Error(data.error || "Error al añadir producto.");
                        });
                    }
                })
                .then((data) => {
                    if (data) {
                        actualizarCarritoVisual(data.total_items, data.total_price);
                        console.log(data.message || "Producto añadido al carrito.");
                    }
                })
                .catch((error) => {
                    console.error("Error:", error.message);
                });
        });
    });

    // Evento para actualizar cantidades en el carrito
    document.querySelectorAll(".carrito-cantidad-input").forEach((input) => {
        input.addEventListener("change", function () {
            const detalleId = this.dataset.detalleId;
            const nuevaCantidad = parseInt(this.value, 10);

            fetch(`/carrito/actualizar/${detalleId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCsrfToken(),
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ cantidad: nuevaCantidad }),
            })
                .then((response) => {
                    if (!response.ok) {
                        return response.json().then((data) => {
                            manejarError(data.error, this, data.max_stock);
                            throw new Error(data.error);
                        });
                    }
                    return response.json();
                })
                .then((data) => {
                    actualizarCarritoVisual(data.total_items, data.total_price, data.total_price_with_iva);
                })
                .catch((error) => {
                    console.error("Error:", error);
                });
        });
    });

    // Validar entradas de tipo CLP
    const clpInputs = document.querySelectorAll(".clp-input");
    clpInputs.forEach((input) => {
        input.addEventListener("input", function (e) {
            let value = e.target.value.replace(/\D/g, ""); // Elimina caracteres no numéricos
            value = new Intl.NumberFormat("es-CL", {
                style: "currency",
                currency: "CLP",
                minimumFractionDigits: 0,
            })
                .format(value)
                .replace("CLP", "")
                .trim();
            e.target.value = value;
        });
        input.addEventListener("blur", function (e) {
            if (e.target.value.trim() === "") {
                e.target.value = "";
            }
        });
    });
});

//----------------------------------- SCRIPT PARA EL MODAL DE CADA PRODUCTO -----------------------------------
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".product-card").forEach((card) => {
        card.addEventListener("click", function (e) {
            if (e.target.classList.contains("add-to-cart-btn")) return;

            const productId = this.getAttribute("data-product-id");

            fetch(`/producto/detalle/${productId}/`)
                .then((response) => response.json())
                .then((data) => {
                    // Rellenar los datos del modal
                    document.getElementById("modal-product-image").src = data.imagen;
                    document.getElementById("modal-product-name").textContent = data.nombre;
                    document.getElementById("modal-product-price").textContent = data.precio;

                    const stockStatus = document.getElementById("stock-status");
                    stockStatus.textContent = data.disponibilidad;
                    stockStatus.className = `badge ${data.disponibilidad === "Disponible" ? "badge-success" : "badge-danger"}`;

                    // Mostrar la descripción del producto
                    document.getElementById("modal-product-description").textContent = data.descripcion;

                    // Mostrar el modal
                    const modal = new bootstrap.Modal(document.getElementById("productModal"));
                    modal.show();
                })
                .catch((error) => console.error("Error al obtener detalles del producto:", error));
        });
    });
});


//----------------------------------- SCRIPT PARA LA SECCION FINALIZAR COMPRA -----------------------------------

document.addEventListener("DOMContentLoaded", function () {
    // Función para manejar el flujo del acordeón
    const nextButtons = document.querySelectorAll(".btn-primary");

    nextButtons.forEach((btn) => {
        btn.addEventListener("click", function () {
            const parentAccordion = btn.closest(".accordion-collapse");
            const nextAccordion = parentAccordion.parentElement.nextElementSibling;

            // Minimiza la sección actual
            parentAccordion.classList.remove("show");
            const parentButton = parentAccordion.previousElementSibling.querySelector(".accordion-button");
            parentButton.classList.add("collapsed");

            // Expande la siguiente sección si existe
            if (nextAccordion) {
                const nextCollapse = nextAccordion.querySelector(".accordion-collapse");
                const nextButton = nextAccordion.querySelector(".accordion-button");
                nextCollapse.classList.add("show");
                nextButton.classList.remove("collapsed");
            }
        });
    });

    // Función para abrir el formulario de dirección (en caso de edición)
    document.getElementById("edit-address-btn")?.addEventListener("click", function () {
        const addressForm = document.getElementById("form-direccion");
        if (addressForm) {
            addressForm.classList.toggle("d-none");
        }
    });
});



//----------------------------------- SCRIPT PARA EL MANEJO DEL PAGO DE PAYPAL -----------------------------------
// Obtener el token CSRF desde la metaetiqueta en el HTML
function getCsrfToken() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    return csrfToken;
}

document.addEventListener("DOMContentLoaded", function () {
    paypal.Buttons({
        createOrder: function (data, actions) {
            return fetch("/api/orders", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
            })
                .then((response) => response.json())
                .then((orderData) => {
                    if (orderData.error) {
                        throw new Error(orderData.error);
                    }
                    return orderData.id; // Devuelve el ID de la orden
                });
        },
        onApprove: function (data, actions) {
            return fetch(`/api/orders/${data.orderID}/capture`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
            })
                .then((response) => response.json())
                .then((captureData) => {
                    if (captureData.error) {
                        throw new Error(captureData.error);
                    }
                    alert("Pago completado. ID de transacción: " + captureData.id);
                    window.location.href = "/agradecimiento/";
                });
        },
        onError: function (err) {
            console.error("Error en el pago:", err);
            alert("Hubo un error al procesar el pago.");
        },
    }).render("#paypal-button-container");
});