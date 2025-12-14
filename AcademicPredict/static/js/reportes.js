/* ============================================
   REPORTES JAVASCRIPT
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Reportes cargado');
    
    // Validar formulario de generación
    setupFormValidation();
    
    // Habilitar/deshabilitar opciones según selección
    setupConditionalOptions();
});

/**
 * Validación del formulario de generación de reportes
 */
function setupFormValidation() {
    const form = document.querySelector('form[action*="generar-reporte"]');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        const tipoReporte = form.querySelector('select[name="tipo_reporte"]').value;
        const formato = form.querySelector('select[name="formato"]').value;
        
        if (!tipoReporte || !formato) {
            e.preventDefault();
            alert('Por favor seleccione el tipo de reporte y formato');
            return;
        }
        
        // Mostrar loading
        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generando...';
        btn.disabled = true;
        
        // Restaurar después de 3 segundos (por si falla)
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }, 3000);
    });
}

/**
 * Habilita/deshabilita opciones según el formato seleccionado
 */
function setupConditionalOptions() {
    const formatoSelect = document.querySelector('select[name="formato"]');
    const incluirGraficos = document.getElementById('incluirGraficos');
    
    if (!formatoSelect || !incluirGraficos) return;
    
    formatoSelect.addEventListener('change', function() {
        // Solo habilitar "Incluir gráficos" si el formato es PDF
        if (this.value === 'pdf') {
            incluirGraficos.disabled = false;
            incluirGraficos.parentElement.classList.remove('text-muted');
        } else {
            incluirGraficos.disabled = true;
            incluirGraficos.checked = false;
            incluirGraficos.parentElement.classList.add('text-muted');
        }
    });
    
    // Ejecutar al cargar para establecer estado inicial
    formatoSelect.dispatchEvent(new Event('change'));
}

console.log('✅ reportes.js cargado');