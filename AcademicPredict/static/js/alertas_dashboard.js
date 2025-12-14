/* ============================================
   ALERTAS DASHBOARD JAVASCRIPT
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Dashboard de Alertas cargado');
    
    // Inicializar tooltips de Bootstrap
    initTooltips();
    
    // Auto-submit filtros al cambiar
    setupAutoSubmit();
});

/**
 * Inicializa los tooltips de Bootstrap
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

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
 * Exporta las alertas a Excel
 */
function exportarExcel() {
    const params = new URLSearchParams(window.location.search);
    window.location.href = '/alertas/exportar/excel/?' + params.toString();
}

console.log('✅ alertas_dashboard.js cargado');