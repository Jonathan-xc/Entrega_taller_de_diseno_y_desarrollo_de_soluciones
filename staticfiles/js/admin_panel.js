document.addEventListener('DOMContentLoaded', function () {
    // Confirmación para eliminar
    const deleteButtons = document.querySelectorAll('.btn-delete');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            const confirmDelete = confirm('¿Estás seguro de que deseas eliminar este elemento?');
            if (!confirmDelete) {
                event.preventDefault();
            }
        });
    });

    // Ocultar mensajes de éxito automáticamente después de unos segundos
    const successMessage = document.querySelector('.success-message');
    if (successMessage) {
        setTimeout(() => {
            successMessage.style.display = 'none';
        }, 5000); // Ocultar mensaje después de 5 segundos
    }

    // Formatear campo de precio como moneda chilena
    const precioInput = document.getElementById('id_precio'); // Asegúrate de que el ID coincida con el campo del formulario
    if (precioInput) {
        precioInput.addEventListener('input', function () {
            // Eliminar caracteres no numéricos y formatear como CLP
            let value = precioInput.value.replace(/[^0-9]/g, ''); // Mantener solo números
            if (value) {
                value = new Intl.NumberFormat('es-CL', {
                    style: 'currency',
                    currency: 'CLP',
                    maximumFractionDigits: 0
                }).format(value); // Formatear como CLP
            }
            precioInput.value = value; // Actualizar el valor del campo
        });
    }

    // Manejo de pestañas para las páginas
    const tabs = document.querySelectorAll('.tabs-container a'); // Selecciona las pestañas
    const tabContents = document.querySelectorAll('.tab-content'); // Selecciona el contenido de cada pestaña

    tabs.forEach(tab => {
        tab.addEventListener('click', function (event) {
            if (this.classList.contains('tab-link')) { // Solo aplica a pestañas
                event.preventDefault();
                tabs.forEach(t => t.classList.remove('tab-active'));
                tabContents.forEach(content => content.classList.remove('active-tab'));
                this.classList.add('tab-active');
                const targetId = this.getAttribute('href').substring(1);
                const targetContent = document.getElementById(targetId);
                if (targetContent) {
                    targetContent.classList.add('active-tab');
                }
            }
        });
    });

    // Mostrar la primera pestaña por defecto
    if (tabs.length > 0 && tabContents.length > 0) {
        tabs[0].classList.add('tab-active');
        tabContents[0].classList.add('active-tab');
    }
});
