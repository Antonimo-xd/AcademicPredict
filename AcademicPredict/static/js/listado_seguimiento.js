/* ============================================
   LISTADO SEGUIMIENTO JAVASCRIPT
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    console.log('📋 Listado de Seguimiento cargado');
    
    // Auto-submit filtros
    setupAutoSubmit();
});

/**
 * Configura el auto-submit de filtros
 */
function setupAutoSubmit() {
    const form = document.getElementById('filtrosForm');
    if (!form) return;
    
    const selects = form.querySelectorAll('select');
    selects.forEach(select => {
        select.addEventListener('change', function() {
            form.submit();
        });
    });
}

/**
 * Exporta el listado a Excel
 */
function exportarExcel() {
    const params = new URLSearchParams(window.location.search);
    window.location.href = '/alertas/exportar/seguimiento/?' + params.toString();
}

console.log('✅ listado_seguimiento.js cargado');