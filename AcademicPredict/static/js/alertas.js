// ============================================
// SISTEMA DE ALERTAS - JavaScript Corregido
// Calcula posición dinámica del dropdown
// ============================================

const INTERVALO_ACTUALIZACION = 300000; // 5 minutos
let intervaloAlertas = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔔 Inicializando sistema de alertas...');
    
    cargarAlertasUrgentes();
    configurarDropdown();
    configurarBannerColapsable();
    
    // Actualizar cada 5 minutos
    intervaloAlertas = setInterval(cargarAlertasUrgentes, INTERVALO_ACTUALIZACION);
});

// ============================================
// CONFIGURAR DROPDOWN
// ============================================

function configurarDropdown() {
    const toggle = document.getElementById('alertasToggle');
    const dropdown = document.getElementById('alertasDropdown');
    const overlay = document.getElementById('alertasOverlay');
    
    if (!toggle || !dropdown || !overlay) {
        console.warn('⚠️ Elementos de alertas no encontrados');
        return;
    }
    
    // Toggle dropdown
    toggle.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const isShown = dropdown.classList.contains('show');
        if (isShown) {
            cerrarDropdown();
        } else {
            abrirDropdown();
        }
    });
    
    // IMPORTANTE: Evitar que clicks dentro del dropdown lo cierren
    dropdown.addEventListener('click', function(e) {
        e.stopPropagation();
    });
    
    // Cerrar con overlay
    overlay.addEventListener('click', cerrarDropdown);
    
    // Cerrar con ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && dropdown.classList.contains('show')) {
            cerrarDropdown();
        }
    });
    
    // Recalcular posición al redimensionar ventana
    window.addEventListener('resize', function() {
        if (dropdown.classList.contains('show')) {
            posicionarDropdown();
        }
    });
}

function abrirDropdown() {
    const dropdown = document.getElementById('alertasDropdown');
    const overlay = document.getElementById('alertasOverlay');
    
    // Posicionar el dropdown correctamente
    posicionarDropdown();
    
    // Mostrar
    dropdown.classList.add('show');
    overlay.classList.add('show');
    
    console.log('✅ Dropdown abierto');
}

function posicionarDropdown() {
    const toggle = document.getElementById('alertasToggle');
    const dropdown = document.getElementById('alertasDropdown');
    
    if (!toggle || !dropdown) return;
    
    // Obtener posición del botón de la campana
    const rect = toggle.getBoundingClientRect();
    
    // Detectar si estamos en móvil
    const isMobile = window.innerWidth <= 991;
    
    if (isMobile) {
        // En móvil: centrar en la pantalla
        dropdown.style.left = '50%';
        dropdown.style.transform = 'translateX(-50%)';
        dropdown.style.top = '80px';
    } else {
        // En desktop: posicionar al lado del sidebar
        const sidebarWidth = 260; // Ancho de tu sidebar
        dropdown.style.left = (sidebarWidth + 20) + 'px';
        dropdown.style.top = (rect.top + window.scrollY) + 'px';
        dropdown.style.transform = 'none';
    }
}

function cerrarDropdown() {
    const dropdown = document.getElementById('alertasDropdown');
    const overlay = document.getElementById('alertasOverlay');
    
    dropdown.classList.remove('show');
    overlay.classList.remove('show');
    
    console.log('✅ Dropdown cerrado');
}

// ============================================
// CONFIGURAR BANNER COLAPSABLE (HOME)
// ============================================

function configurarBannerColapsable() {
    const banner = document.getElementById('alertasBannerHome');
    if (!banner) return; // No estamos en home
    
    const btnCerrar = banner.querySelector('.btn-close');
    const contenidoBanner = banner.querySelector('.alerta-banner-content');
    
    if (!btnCerrar) return;
    
    // Verificar si el banner estaba colapsado
    const wasCollapsed = localStorage.getItem('alertasBannerCollapsed') === 'true';
    if (wasCollapsed) {
        colapsarBanner(banner, contenidoBanner, true);
    }
    
    // Click en cerrar
    btnCerrar.addEventListener('click', function(e) {
        e.preventDefault();
        colapsarBanner(banner, contenidoBanner, false);
    });
}

function colapsarBanner(banner, contenido, instant) {
    // Ocultar contenido
    if (instant) {
        contenido.style.display = 'none';
    } else {
        contenido.style.transition = 'all 0.3s ease';
        contenido.style.opacity = '0';
        contenido.style.maxHeight = '0';
        setTimeout(() => {
            contenido.style.display = 'none';
        }, 300);
    }
    
    // Agregar botón expandir
    if (!banner.querySelector('.btn-expandir-alertas')) {
        const btnExpandir = document.createElement('button');
        btnExpandir.className = 'btn btn-expandir-alertas';
        btnExpandir.innerHTML = '<i class="fas fa-bell me-2"></i>Alertas Pendientes';
        btnExpandir.onclick = function() {
            expandirBanner(banner, contenido, btnExpandir);
        };
        banner.appendChild(btnExpandir);
        
        if (!instant) {
            setTimeout(() => {
                btnExpandir.style.opacity = '1';
            }, 100);
        }
    }
    
    // Guardar estado
    localStorage.setItem('alertasBannerCollapsed', 'true');
}

function expandirBanner(banner, contenido, btnExpandir) {
    // Quitar botón expandir
    btnExpandir.style.opacity = '0';
    setTimeout(() => {
        btnExpandir.remove();
    }, 300);
    
    // Mostrar contenido
    contenido.style.display = 'block';
    setTimeout(() => {
        contenido.style.transition = 'all 0.3s ease';
        contenido.style.opacity = '1';
        contenido.style.maxHeight = '1000px';
    }, 10);
    
    // Guardar estado
    localStorage.setItem('alertasBannerCollapsed', 'false');
}

// ============================================
// CARGAR ALERTAS URGENTES
// ============================================

function cargarAlertasUrgentes() {
    console.log('📡 Cargando alertas urgentes...');
    
    fetch('/alertas/api/urgentes/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(`✅ ${data.total} alertas cargadas`);
            actualizarBadge(data.total);
            renderizarAlertas(data.alertas);
        })
        .catch(error => {
            console.error('❌ Error cargando alertas:', error);
            mostrarErrorCarga();
        });
}

function actualizarBadge(total) {
    const badge = document.getElementById('alertasBadge');
    const sidebarBadge = document.getElementById('sidebar-alertas-badge');
    
    // Badge en la campana
    if (badge) {
        if (total > 0) {
            badge.textContent = total > 99 ? '99+' : total;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }
    
    // Badge en el menú del sidebar
    if (sidebarBadge) {
        if (total > 0) {
            sidebarBadge.textContent = total > 99 ? '99+' : total;
            sidebarBadge.style.display = 'inline-block';
        } else {
            sidebarBadge.style.display = 'none';
        }
    }
}

function renderizarAlertas(alertas) {
    const lista = document.getElementById('alertasLista');
    if (!lista) return;
    
    // Si no hay alertas
    if (!alertas || alertas.length === 0) {
        lista.innerHTML = `
            <div class="alertas-empty">
                <i class="fas fa-check-circle"></i>
                <p>No hay alertas urgentes</p>
            </div>
        `;
        return;
    }
    
    // Renderizar alertas
    let html = '';
    alertas.forEach(alerta => {
        const prioridadClass = obtenerClasePrioridad(alerta.prioridad_codigo);
        const fechaFormateada = formatearFecha(alerta.fecha_creacion);
        
        html += `
            <div class="alerta-item" onclick="navegarAFicha('${alerta.estudiante}')">
                <strong>
                    ${alerta.estudiante}
                    <span class="alerta-prioridad-badge ${prioridadClass}">
                        ${alerta.prioridad}
                    </span>
                </strong>
                <p>${alerta.titulo}</p>
                <small>
                    <span class="alerta-riesgo">${alerta.indice_riesgo.toFixed(1)}%</span>
                    ${fechaFormateada}
                </small>
            </div>
        `;
    });
    
    lista.innerHTML = html;
}

function mostrarErrorCarga() {
    const lista = document.getElementById('alertasLista');
    if (!lista) return;
    
    lista.innerHTML = `
        <div class="alertas-empty">
            <i class="fas fa-exclamation-triangle text-warning"></i>
            <p>Error al cargar alertas</p>
            <button class="btn btn-sm btn-primary" onclick="cargarAlertasUrgentes()">
                Reintentar
            </button>
        </div>
    `;
}

function obtenerClasePrioridad(codigo) {
    const mapa = {
        'critica': 'alerta-prioridad-critica',
        'alta': 'alerta-prioridad-alta',
        'media': 'alerta-prioridad-media',
        'baja': 'alerta-prioridad-baja'
    };
    return mapa[codigo] || 'alerta-prioridad-media';
}

function formatearFecha(fechaISO) {
    try {
        const fecha = new Date(fechaISO);
        const ahora = new Date();
        const diff = ahora - fecha;
        
        // Si es de hace menos de 1 hora, mostrar "hace X minutos"
        if (diff < 3600000) {
            const minutos = Math.floor(diff / 60000);
            return `hace ${minutos} min`;
        }
        
        // Si es de hoy, mostrar hora
        if (fecha.toDateString() === ahora.toDateString()) {
            return fecha.toLocaleTimeString('es-ES', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        
        // Si es de esta semana, mostrar día y hora
        const diasDiff = Math.floor(diff / 86400000);
        if (diasDiff < 7) {
            return fecha.toLocaleDateString('es-ES', {
                weekday: 'short',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        
        // Más antiguo: mostrar fecha completa
        return fecha.toLocaleDateString('es-ES', {
            day: '2-digit',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        console.error('Error formateando fecha:', e);
        return fechaISO;
    }
}

function navegarAFicha(codigoEstudiante) {
    cerrarDropdown();
    console.log(`📍 Navegando a ficha de ${codigoEstudiante}`);
    window.location.href = `/alertas/estudiante/${codigoEstudiante}/seguimiento/`;
}

// Limpiar intervalo al salir de la página
window.addEventListener('beforeunload', function() {
    if (intervaloAlertas) {
        clearInterval(intervaloAlertas);
        console.log('🛑 Intervalo de alertas detenido');
    }
});

// API pública para debugging
window.SistemaAlertas = {
    cargar: cargarAlertasUrgentes,
    abrir: abrirDropdown,
    cerrar: cerrarDropdown,
    version: '2.1'
};

console.log('✅ Sistema de alertas cargado v2.1');










