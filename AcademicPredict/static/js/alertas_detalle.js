/* ============================================
   ALERTAS DETALLE JAVASCRIPT
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 Detalle de Alerta cargado');
    
    // Confirmar cambios de estado
    setupConfirmaciones();
});

/**
 * Configura confirmaciones para acciones importantes
 */
function setupConfirmaciones() {
    const formularios = document.querySelectorAll('form[action*="cambiar-estado"]');
    
    formularios.forEach(form => {
        form.addEventListener('submit', function(e) {
            const select = form.querySelector('select[name="estado"]');
            const nuevoEstado = select.options[select.selectedIndex].text;
            
            if (!confirm(`¿Confirmar cambio de estado a "${nuevoEstado}"?`)) {
                e.preventDefault();
            }
        });
    });
}

console.log('✅ alertas_detalle.js cargado');