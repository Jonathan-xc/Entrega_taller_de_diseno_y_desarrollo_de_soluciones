document.addEventListener("DOMContentLoaded", function () {
    const carritoCantidad = document.getElementById("carrito-cantidad");
    const carritoTotal = document.getElementById("carrito-total");
    const listaCarrito = document.getElementById("lista-carrito");

    // Datos iniciales del carrito
    let carrito = [];

    // Actualizar la visualización del carrito
    function actualizarCarrito() {
        let totalProductos = 0;
        let totalPrecio = 0;

        // Limpiar la lista del carrito
        listaCarrito.innerHTML = "";

        carrito.forEach(item => {
            totalProductos += item.cantidad;
            totalPrecio += item.precio * item.cantidad;

            // Crear un elemento para cada producto
            const li = document.createElement("li");
            li.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");
            li.innerHTML = `
                ${item.nombre} - ${item.cantidad} x ${item.precio} $
                <button class="btn btn-danger btn-sm" data-id="${item.id}">Eliminar</button>
            `;
            listaCarrito.appendChild(li);
        });

        // Actualizar los totales en el ícono del carrito
        carritoCantidad.textContent = totalProductos;
        carritoTotal.textContent = `${totalPrecio} $`;
    }

    // Agregar un producto al carrito
    function agregarAlCarrito(producto) {
        const existente = carrito.find(item => item.id === producto.id);
        if (existente) {
            existente.cantidad += producto.cantidad;
        } else {
            carrito.push(producto);
        }
        actualizarCarrito();
    }

    // Eliminar un producto del carrito
    listaCarrito.addEventListener("click", function (e) {
        if (e.target.classList.contains("btn-danger")) {
            const id = parseInt(e.target.getAttribute("data-id"));
            carrito = carrito.filter(item => item.id !== id);
            actualizarCarrito();
        }
    });

    // Inicializar el carrito vacío
    actualizarCarrito();
});
