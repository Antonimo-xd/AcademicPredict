document.addEventListener('DOMContentLoaded', function() {
    
    // ================================================
    // ELEMENTOS DEL DOM
    // ================================================
    
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('archivo_csv');
    const fileName = document.getElementById('fileName');
    const fileNameText = document.getElementById('fileNameText');
    const btnUpload = document.getElementById('btnUpload');
    const uploadForm = document.getElementById('uploadForm');
    
    // ================================================
    // DRAG & DROP
    // ================================================
    
    // Click en zona de subida
    uploadZone.addEventListener('click', function(e) {
        if (e.target !== fileInput) {
            fileInput.click();
        }
    });
    
    // Drag over
    uploadZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.classList.add('dragging');
    });
    
    // Drag leave
    uploadZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.classList.remove('dragging');
    });
    
    // Drop
    uploadZone.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.classList.remove('dragging');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (validateFile(file)) {
                fileInput.files = files;
                updateFileName(file);
            }
        }
    });
    
    // ================================================
    // CAMBIO DE ARCHIVO
    // ================================================
    
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            if (validateFile(file)) {
                updateFileName(file);
            } else {
                e.target.value = '';
            }
        }
    });
    
    // ================================================
    // VALIDACIÓN DE ARCHIVO
    // ================================================
    
    function validateFile(file) {
        // Validar extensión
        if (!file.name.endsWith('.csv')) {
            showAlert('error', 'El archivo debe ser formato CSV (.csv)');
            return false;
        }
        
        // Validar tamaño (máximo 200MB)
        const maxSize = 200 * 1024 * 1024; // 200MB
        if (file.size > maxSize) {
            showAlert('error', 'El archivo es demasiado grande. Máximo 200MB.');
            return false;
        }
        
        return true;
    }
    
    // ================================================
    // ACTUALIZAR NOMBRE DE ARCHIVO
    // ================================================
    
    function updateFileName(file) {
        fileName.style.display = 'block';
        fileNameText.textContent = file.name;
        btnUpload.disabled = false;
        
        // Mostrar info del archivo
        const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);
        fileNameText.innerHTML = `
            <strong>${file.name}</strong><br>
            <small class="text-muted">Tamaño: ${sizeInMB} MB</small>
        `;
    }
    
    // ================================================
    // ENVÍO DEL FORMULARIO
    // ================================================
    
    uploadForm.addEventListener('submit', function(e) {
        // Confirmar importación
        if (!confirm('¿Estás seguro de iniciar la importación? Este proceso puede tardar varios minutos.')) {
            e.preventDefault();
            return false;
        }
        
        // Mostrar loading
        showLoadingOverlay();
        
        // Deshabilitar botón
        btnUpload.disabled = true;
        btnUpload.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Importando...';
    });
    
    // ================================================
    // LOADING OVERLAY
    // ================================================
    
    function showLoadingOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.id = 'loadingOverlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner">
                    <i class="fas fa-spinner fa-spin"></i>
                </div>
                <div class="loading-text">Importando datos...</div>
                <small class="text-muted">Por favor no cierres esta ventana</small>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    
    function hideLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.remove();
        }
    }
    
    // ================================================
    // ALERTAS
    // ================================================
    
    function showAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insertar al inicio del contenido
        const mainContent = document.querySelector('.main-content');
        const container = mainContent.querySelector('.container-fluid');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss después de 5 segundos
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
    
    // ================================================
    // TOGGLE REPORTE DETALLADO
    // ================================================
    
    window.toggleReporte = function() {
        const reporte = document.getElementById('reporteDetallado');
        if (reporte) {
            if (reporte.style.display === 'none') {
                reporte.style.display = 'block';
            } else {
                reporte.style.display = 'none';
            }
        }
    };
    
    // ================================================
    // ESTIMACIÓN DE TIEMPO
    // ================================================
    
    function estimateTime(fileSize) {
        // Estimación aproximada: ~1MB por segundo
        const seconds = fileSize / (1024 * 1024);
        const minutes = Math.ceil(seconds / 60);
        return minutes;
    }
    
    // ================================================
    // PREVENIR CIERRE DURANTE IMPORTACIÓN
    // ================================================
    
    let isImporting = false;
    
    uploadForm.addEventListener('submit', function() {
        isImporting = true;
    });
    
    // ================================================
    // LOGS DE CONSOLA
    // ================================================
    
    console.log('Módulo de importación cargado correctamente');
    
});









