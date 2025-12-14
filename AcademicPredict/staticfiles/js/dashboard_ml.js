// ============================================
// DASHBOARD ML - JAVASCRIPT
// ============================================

// CSRF Token (Django)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Ejecutar Detección ML
function ejecutarDeteccion() {
    // Confirmación
    if (!confirm('¿Ejecutar nueva detección ML?\n\nEsto puede tomar 2-5 minutos y procesará todos los estudiantes.\n\n¿Deseas continuar?')) {
        return;
    }
    
    // Mostrar modal de loading
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    loadingModal.show();
    
    // Deshabilitar botón
    const btnEjecutar = document.getElementById('btn-ejecutar');
    btnEjecutar.disabled = true;
    btnEjecutar.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Ejecutando...';
    
    // Obtener CSRF token
    const csrftoken = getCookie('csrftoken');
    
    // Llamar a API
    fetch('/ml/ejecutar/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Cerrar modal
        loadingModal.hide();
        
        if (data.success) {
            // Mostrar mensaje de éxito
            const mensaje = `✅ Detección completada exitosamente!\n\n` +
                `📊 Estudiantes procesados: ${data.estudiantes_procesados}\n` +
                `🔴 Riesgo crítico: ${data.criticos}\n` +
                `🟠 Riesgo alto: ${data.altos}\n\n` +
                `La página se recargará para mostrar los nuevos resultados.`;
            
            alert(mensaje);
            
            // Recargar página
            location.reload();
        } else {
            // Mostrar error
            alert('❌ Error: ' + data.error);
            
            // Rehabilitar botón
            btnEjecutar.disabled = false;
            btnEjecutar.innerHTML = '<i class="fas fa-sync-alt me-2"></i>Ejecutar Detección';
        }
    })
    .catch(error => {
        // Cerrar modal
        loadingModal.hide();
        
        // Mostrar error
        console.error('Error ejecutando detección:', error);
        alert('❌ Error ejecutando detección:\n\n' + error.message + '\n\nRevisa la consola para más detalles.');
        
        // Rehabilitar botón
        btnEjecutar.disabled = false;
        btnEjecutar.innerHTML = '<i class="fas fa-sync-alt me-2"></i>Ejecutar Detección';
    });
}

// Inicializar tooltips de Bootstrap
document.addEventListener('DOMContentLoaded', function() {
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Animar KPIs al cargar
    animateKPIs();
    
    // Animar barras de probabilidad
    animateProbabilityBars();
});

// Animar KPIs con conteo
function animateKPIs() {
    const kpiValues = document.querySelectorAll('.kpi-value');
    
    kpiValues.forEach(kpi => {
        const originalText = kpi.textContent.trim();
        console.log('📊 Parseando KPI:', originalText);
        
        // Eliminar TODOS los separadores
        const cleanText = originalText.replace(/[.,\s]/g, '');
        const target = parseInt(cleanText, 10);
        
        if (isNaN(target) || target === 0) {
            console.warn('⚠️ KPI no válido:', originalText);
            return;
        }
        
        console.log('✅ Valor parseado:', target);
        
        const duration = 1500;
        const steps = 60;
        const increment = target / steps;
        const stepTime = duration / steps;
        
        let current = 0;
        kpi.textContent = '0';
        
        const counter = setInterval(() => {
            current += increment;
            
            if (current >= target) {
                current = target;
                clearInterval(counter);
            }
            
            kpi.textContent = Math.floor(current).toLocaleString('es-ES');
        }, stepTime);
        
        // Asegurar valor final exacto
        setTimeout(() => {
            const finalValue = target.toLocaleString('es-ES');
            if (kpi.textContent !== finalValue) {
                kpi.textContent = finalValue;
            }
        }, duration + 100);
    });
}

// Animar barras de probabilidad
function animateProbabilityBars() {
    const probabilityBars = document.querySelectorAll('.probability-fill');
    
    probabilityBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        
        // Animar después de un pequeño delay
        setTimeout(() => {
            bar.style.width = width;
        }, 100);
    });
}

// Información de debug (solo en desarrollo)
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('🤖 Dashboard ML inicializado');
    console.log('📊 Total estudiantes:', document.querySelectorAll('.student-row').length);
}