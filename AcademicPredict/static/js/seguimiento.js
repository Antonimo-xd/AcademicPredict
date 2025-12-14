/* ============================================
   SEGUIMIENTO JAVASCRIPT
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    console.log('👤 Ficha de Seguimiento cargada');
    
    // Validar formularios
    setupFormValidation();
    
    // Limpiar modales al cerrar
    setupModalCleanup();
});

/**
 * Configura validación de formularios
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Por favor complete todos los campos requeridos');
            }
        });
    });
}

/**
 * Limpia los formularios de los modales al cerrar
 */
function setupModalCleanup() {
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function() {
            const form = this.querySelector('form');
            if (form) {
                form.reset();
                
                // Limpiar clases de validación
                const invalidFields = form.querySelectorAll('.is-invalid');
                invalidFields.forEach(field => {
                    field.classList.remove('is-invalid');
                });
            }
        });
    });
}

console.log('✅ seguimiento.js cargado');