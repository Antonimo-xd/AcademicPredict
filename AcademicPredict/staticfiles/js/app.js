/* ============================================
   JAVASCRIPT GLOBAL - AcademicPredict
   SIN conflictos con alertas.js
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    
    // ================================================
    // SIDEBAR MOBILE
    // ================================================
    
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarClose = document.getElementById('sidebarClose');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.add('show');
        });
    }
    
    if (sidebarClose) {
        sidebarClose.addEventListener('click', function() {
            sidebar.classList.remove('show');
        });
    }
    
    // Cerrar sidebar al hacer clic fuera (solo móvil)
    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 992) {
            if (!sidebar.contains(event.target) && 
                !event.target.closest('#sidebarToggle')) {
                sidebar.classList.remove('show');
            }
        }
    });
    
    // ================================================
    // AUTO-DISMISS ALERTS
    // ================================================
    
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // 5 segundos
    });
    
    // ================================================
    // TOOLTIPS Y POPOVERS DE BOOTSTRAP
    // ================================================
    
    // Inicializar tooltips
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers
    const popoverTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="popover"]')
    );
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // ================================================
    // ANIMACIÓN DE NÚMEROS (COUNT UP)
    // ================================================
    
    function animateNumber(element, target, duration = 1000) {
        const start = 0;
        const increment = target / (duration / 16); // 60 FPS
        let current = start;
        
        const timer = setInterval(function() {
            current += increment;
            if (current >= target) {
                element.textContent = target.toLocaleString('es-CL');
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current).toLocaleString('es-CL');
            }
        }, 16);
    }
    
    // Animar números en estadísticas
    const statNumbers = document.querySelectorAll('.stat-number, .stat-number-small');
    const observerOptions = {
        threshold: 0.5
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                const target = parseInt(entry.target.textContent.replace(/\D/g, ''));
                if (!isNaN(target)) {
                    animateNumber(entry.target, target);
                    entry.target.dataset.animated = 'true';
                }
            }
        });
    }, observerOptions);
    
    statNumbers.forEach(function(stat) {
        observer.observe(stat);
    });
    
    // ================================================
    // CONFIRMAR ANTES DE SALIR CON CAMBIOS NO GUARDADOS
    // ================================================
    
    let formChanged = false;
    
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(function(input) {
            input.addEventListener('change', function() {
                formChanged = true;
            });
        });
        
        form.addEventListener('submit', function() {
            formChanged = false;
        });
    });
    
    // ================================================
    // SMOOTH SCROLL
    // ================================================
    
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // ================================================
    // BOTÓN SCROLL TO TOP
    // ================================================
    
    const scrollTopBtn = document.createElement('button');
    scrollTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollTopBtn.className = 'btn btn-primary scroll-top-btn';
    scrollTopBtn.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 999;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    `;
    document.body.appendChild(scrollTopBtn);
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollTopBtn.style.display = 'block';
        } else {
            scrollTopBtn.style.display = 'none';
        }
    });
    
    scrollTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // ================================================
    // BÚSQUEDA EN TABLAS
    // ================================================
    
    const searchInputs = document.querySelectorAll('[data-table-search]');
    searchInputs.forEach(function(input) {
        const tableId = input.getAttribute('data-table-search');
        const table = document.getElementById(tableId);
        
        if (table) {
            input.addEventListener('keyup', function() {
                const filter = this.value.toLowerCase();
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(function(row) {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(filter) ? '' : 'none';
                });
            });
        }
    });
    
    // ================================================
    // FORMATO DE FECHAS
    // ================================================
    
    function formatDate(dateString) {
        const options = { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        const date = new Date(dateString);
        return date.toLocaleDateString('es-CL', options);
    }
    
    // Formatear todas las fechas con clase .format-date
    document.querySelectorAll('.format-date').forEach(function(element) {
        const dateString = element.textContent;
        element.textContent = formatDate(dateString);
    });
    
    // ================================================
    // COPIAR AL PORTAPAPELES
    // ================================================
    
    document.querySelectorAll('[data-copy]').forEach(function(button) {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            navigator.clipboard.writeText(textToCopy).then(function() {
                // Feedback visual
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check me-2"></i>Copiado!';
                button.classList.add('btn-success');
                
                setTimeout(function() {
                    button.innerHTML = originalText;
                    button.classList.remove('btn-success');
                }, 2000);
            });
        });
    });
    
    // ================================================
    // LOGS DE CONSOLA
    // ================================================
    
    console.log('%c AcademicPredict ', 'background: #667eea; color: white; font-size: 16px; padding: 10px;');
    console.log('Sistema de Predicción Universitaria v2.0');
    console.log('Desarrollado por Bastian');
    
});

// ============================================
// NOTA: Sistema de alertas manejado por alertas.js
// NO duplicar funcionalidad aquí
// ============================================





