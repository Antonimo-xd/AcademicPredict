/* ============================================
   DASHBOARD_FILTROS.JS - AcademicPredict
   VERSIÓN CORREGIDA con sanitización
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    
    console.log('📊 Inicializando Dashboard con Filtros...');
    
    // ================================================
    // CONFIGURACIÓN GLOBAL DE CHART.JS
    // ================================================
    
    Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#6c757d';
    Chart.defaults.animation.duration = 1000;
    Chart.defaults.animation.easing = 'easeInOutQuart';
    
    // ================================================
    // PALETA DE COLORES
    // ================================================
    
    const colors = {
        primary: '#667eea',
        secondary: '#764ba2',
        success: '#11998e',
        danger: '#f5576c',
        warning: '#ffc107',
        info: '#4facfe',
        light: '#f8f9fa',
        dark: '#2c3e50',
    };
    
    // ================================================
    // VARIABLES GLOBALES PARA ALMACENAR GRÁFICOS
    // ================================================
    
    let chartAbandonoPie = null;
    let chartAbandonoAnio = null;
    let chartAbandonoCarrera = null;
    let chartRendimiento = null;
    let chartTopAsignaturas = null;
    
    // ================================================
    // 🔧 NUEVA FUNCIÓN: SANITIZAR VALORES
    // ================================================
    
    /**
     * 📚 EXPLICACIÓN EDUCATIVA:
     * Esta función limpia valores que podrían contener:
     * - Espacios no rompibles (\u00A0 o \xa0)
     * - Espacios normales extra
     * - Caracteres invisibles
     * 
     * Esto es importante porque los datos pueden venir de:
     * - Copy-paste desde Excel/Word (introduce espacios especiales)
     * - Encodings incorrectos (UTF-8 mal interpretado)
     * - Problemas en la base de datos
     */
    function sanitizarValor(valor) {
        if (!valor) return valor;
        
        // Convertir a string y eliminar:
        // 1. Espacios no rompibles (\u00A0)
        // 2. Espacios normales al inicio/fin
        // 3. Múltiples espacios consecutivos
        return String(valor)
            .replace(/\u00A0/g, '')  // Eliminar espacios no rompibles
            .replace(/\s+/g, '')      // Eliminar todos los espacios
            .trim();                  // Limpiar inicio/fin
    }
    
    // ================================================
    // FUNCIÓN: CREAR GRÁFICOS INICIALES
    // ================================================
    
    function crearGraficosIniciales() {
        console.log('🎨 Creando gráficos iniciales...');
        
        // GRÁFICO 1: Pie Chart
        const ctxPie = document.getElementById('chartAbandonoPie');
        if (ctxPie && typeof abandonoLabels !== 'undefined') {
            chartAbandonoPie = new Chart(ctxPie, {
                type: 'pie',
                data: {
                    labels: abandonoLabels,
                    datasets: [{
                        data: abandonoData,
                        backgroundColor: [colors.success, colors.danger],
                        borderColor: '#fff',
                        borderWidth: 2,
                        hoverOffset: 10
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 15,
                                font: { size: 13, weight: '600' }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            },
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleFont: { size: 14, weight: 'bold' },
                            bodyFont: { size: 13 },
                            padding: 12,
                            cornerRadius: 8
                        }
                    }
                }
            });
        }
        
        // GRÁFICO 2: Line Chart
        const ctxLine = document.getElementById('chartAbandonoAnio');
        if (ctxLine && typeof abandonoAnioLabels !== 'undefined') {
            chartAbandonoAnio = new Chart(ctxLine, {
                type: 'line',
                data: {
                    labels: abandonoAnioLabels,
                    datasets: [{
                        label: 'Estudiantes con Abandono',
                        data: abandonoAnioData,
                        borderColor: colors.danger,
                        backgroundColor: colors.danger + '20',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointHoverRadius: 8,
                        pointBackgroundColor: colors.danger,
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    interaction: { mode: 'index', intersect: false },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                            labels: { font: { size: 13, weight: '600' } }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleFont: { size: 14, weight: 'bold' },
                            bodyFont: { size: 13 },
                            padding: 12,
                            cornerRadius: 8
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { precision: 0 },
                            grid: { color: 'rgba(0, 0, 0, 0.05)' }
                        },
                        x: { grid: { display: false } }
                    }
                }
            });
        }
        
        // GRÁFICO 3: Bar Chart Horizontal
        const ctxBar = document.getElementById('chartAbandonoCarrera');
        if (ctxBar && typeof abandonoCarreraLabels !== 'undefined') {
            chartAbandonoCarrera = new Chart(ctxBar, {
                type: 'bar',
                data: {
                    labels: abandonoCarreraLabels,
                    datasets: [{
                        label: 'Estudiantes con Abandono',
                        data: abandonoCarreraData,
                        backgroundColor: colors.danger + 'cc',
                        borderColor: colors.danger,
                        borderWidth: 2,
                        borderRadius: 5,
                        hoverBackgroundColor: colors.danger
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    indexAxis: 'y',
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleFont: { size: 14, weight: 'bold' },
                            bodyFont: { size: 13 },
                            padding: 12,
                            cornerRadius: 8
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: { precision: 0 },
                            grid: { color: 'rgba(0, 0, 0, 0.05)' }
                        },
                        y: { grid: { display: false } }
                    }
                }
            });
        }
        
        // GRÁFICO 4: Histograma
        const ctxHistogram = document.getElementById('chartRendimiento');
        if (ctxHistogram && typeof rendimientoLabels !== 'undefined') {
            chartRendimiento = new Chart(ctxHistogram, {
                type: 'bar',
                data: {
                    labels: rendimientoLabels,
                    datasets: [{
                        label: 'Número de Registros',
                        data: rendimientoData,
                        backgroundColor: colors.primary + 'cc',
                        borderColor: colors.primary,
                        borderWidth: 2,
                        borderRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `Registros: ${context.parsed.y}`;
                                }
                            },
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleFont: { size: 14, weight: 'bold' },
                            bodyFont: { size: 13 },
                            padding: 12,
                            cornerRadius: 8
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { precision: 0 },
                            grid: { color: 'rgba(0, 0, 0, 0.05)' },
                            title: {
                                display: true,
                                text: 'Frecuencia',
                                font: { size: 13, weight: '600' }
                            }
                        },
                        x: {
                            grid: { display: false },
                            title: {
                                display: true,
                                text: 'Rendimiento Académico (%)',
                                font: { size: 13, weight: '600' }
                            }
                        }
                    }
                }
            });
        }
        
        // GRÁFICO 5: Top Asignaturas
        const ctxTopAsignaturas = document.getElementById('chartTopAsignaturas');
        if (ctxTopAsignaturas && typeof topAsignaturasLabels !== 'undefined') {
            chartTopAsignaturas = new Chart(ctxTopAsignaturas, {
                type: 'bar',
                data: {
                    labels: topAsignaturasLabels,
                    datasets: [{
                        label: 'Número de Estudiantes',
                        data: topAsignaturasData,
                        backgroundColor: colors.info + 'cc',
                        borderColor: colors.info,
                        borderWidth: 2,
                        borderRadius: 5,
                        hoverBackgroundColor: colors.info
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleFont: { size: 14, weight: 'bold' },
                            bodyFont: { size: 13 },
                            padding: 12,
                            cornerRadius: 8
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { precision: 0 },
                            grid: { color: 'rgba(0, 0, 0, 0.05)' },
                            title: {
                                display: true,
                                text: 'Estudiantes Matriculados',
                                font: { size: 13, weight: '600' }
                            }
                        },
                        x: {
                            grid: { display: false },
                            ticks: {
                                autoSkip: false,
                                maxRotation: 45,
                                minRotation: 45
                            }
                        }
                    }
                }
            });
        }
        
        console.log('✅ Gráficos iniciales creados');
    }
    
    // ================================================
    // 🔧 FUNCIÓN MEJORADA: APLICAR FILTROS (AJAX)
    // ================================================
    
    function aplicarFiltros() {
        console.log('🔍 Aplicando filtros...');
        
        // Mostrar indicador de carga
        mostrarLoading(true);
        
        // PASO 1: Obtener valores y SANITIZARLOS
        const anioAcademico = sanitizarValor(document.getElementById('filtroAnioAcademico').value);
        const carrera = sanitizarValor(document.getElementById('filtroCarrera').value);
        const campus = sanitizarValor(document.getElementById('filtroCampus').value);
        const dedicacion = sanitizarValor(document.getElementById('filtroDedicacion').value);
        
        console.log(`   📋 Filtros SANITIZADOS: año=${anioAcademico}, carrera=${carrera}, campus=${campus}, dedicacion=${dedicacion}`);
        
        // 🔧 VALIDACIÓN ADICIONAL: Verificar que el año sea numérico
        if (anioAcademico !== 'todos' && isNaN(anioAcademico)) {
            console.error(`❌ Error: Año académico no es válido: "${anioAcademico}"`);
            alert('Error: El año académico contiene caracteres inválidos. Por favor, recarga la página.');
            mostrarLoading(false);
            return;
        }
        
        // PASO 2: Construir URL con parámetros GET
        const params = new URLSearchParams({
            anio_academico: anioAcademico,
            carrera: carrera,
            campus: campus,
            dedicacion: dedicacion
        });
        
        const url = `/dashboard/filtrar/?${params.toString()}`;
        console.log(`   🌐 URL: ${url}`);
        
        // PASO 3: Hacer petición AJAX con Fetch API
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('   ✅ Datos recibidos:', data);
                
                // PASO 4: Verificar si hay datos
                if (!data.success) {
                    console.warn('⚠️ La respuesta no fue exitosa');
                    alert('No se pudieron cargar los datos filtrados');
                    mostrarLoading(false);
                    return;
                }
                
                // PASO 5: Actualizar KPIs
                actualizarKPIs(data.kpis);
                
                // PASO 6: Actualizar gráficos
                actualizarGraficos(data.graficos);
                
                // PASO 7: Mostrar filtros activos
                mostrarFiltrosActivos(data.filtros_aplicados);
                
                // Ocultar loading
                mostrarLoading(false);
                
                console.log('✅ Dashboard actualizado correctamente');
            })
            .catch(error => {
                console.error('❌ Error al aplicar filtros:', error);
                alert('Error al aplicar filtros. Por favor, revisa la consola para más detalles.');
                mostrarLoading(false);
            });
    }
    
    // ================================================
    // FUNCIÓN: ACTUALIZAR KPIs
    // ================================================
    
    function actualizarKPIs(kpis) {
        console.log('📊 Actualizando KPIs...');
        
        const elementos = [
            { id: 'kpiEstudiantes', valor: kpis.total_estudiantes.toLocaleString('es-CL') },
            { id: 'kpiAbandonos', valor: `${kpis.total_abandonos.toLocaleString('es-CL')} estudiantes` },
            { id: 'kpiTasaAbandono', valor: `${kpis.tasa_abandono}%` },
            { id: 'kpiCreditos', valor: kpis.promedio_creditos },
            { id: 'kpiCarreras', valor: kpis.total_carreras.toLocaleString('es-CL') }
        ];
        
        elementos.forEach(elem => {
            const elemento = document.getElementById(elem.id);
            if (elemento) {
                elemento.classList.add('kpi-updating');
                setTimeout(() => {
                    elemento.textContent = elem.valor;
                    elemento.classList.remove('kpi-updating');
                }, 150);
            }
        });
        
        console.log('   ✓ KPIs actualizados');
    }
    
    // ================================================
    // 🔧 FUNCIÓN MEJORADA: ACTUALIZAR GRÁFICOS
    // ================================================
    
    function actualizarGraficos(graficos) {
        console.log('📈 Actualizando gráficos...');
        
        // Función auxiliar para verificar si hay datos
        function tieneDatos(data) {
            return data && Array.isArray(data) && data.length > 0 && data.some(val => val > 0);
        }
        
        // Actualizar Pie Chart
        if (chartAbandonoPie && graficos.abandono_pie) {
            if (tieneDatos(graficos.abandono_pie.data)) {
                chartAbandonoPie.data.labels = graficos.abandono_pie.labels;
                chartAbandonoPie.data.datasets[0].data = graficos.abandono_pie.data;
                chartAbandonoPie.update('active');
                console.log('   ✓ Pie Chart actualizado');
            } else {
                console.warn('   ⚠️ Pie Chart: Sin datos para mostrar');
            }
        }
        
        // Actualizar Line Chart
        if (chartAbandonoAnio && graficos.abandono_anio) {
            if (tieneDatos(graficos.abandono_anio.data)) {
                chartAbandonoAnio.data.labels = graficos.abandono_anio.labels;
                chartAbandonoAnio.data.datasets[0].data = graficos.abandono_anio.data;
                chartAbandonoAnio.update('active');
                console.log('   ✓ Line Chart actualizado');
            } else {
                console.warn('   ⚠️ Line Chart: Sin datos para mostrar');
            }
        }
        
        // Actualizar Bar Chart (Carreras)
        if (chartAbandonoCarrera && graficos.abandono_carrera) {
            if (tieneDatos(graficos.abandono_carrera.data)) {
                chartAbandonoCarrera.data.labels = graficos.abandono_carrera.labels;
                chartAbandonoCarrera.data.datasets[0].data = graficos.abandono_carrera.data;
                chartAbandonoCarrera.update('active');
                console.log('   ✓ Bar Chart (Carreras) actualizado');
            } else {
                console.warn('   ⚠️ Bar Chart (Carreras): Sin datos para mostrar');
            }
        }
        
        // Actualizar Histograma
        if (chartRendimiento && graficos.rendimiento) {
            if (tieneDatos(graficos.rendimiento.data)) {
                chartRendimiento.data.labels = graficos.rendimiento.labels;
                chartRendimiento.data.datasets[0].data = graficos.rendimiento.data;
                chartRendimiento.update('active');
                console.log('   ✓ Histograma actualizado');
            } else {
                console.warn('   ⚠️ Histograma: Sin datos para mostrar');
            }
        }
        
        // Actualizar Top Asignaturas
        if (chartTopAsignaturas && graficos.top_asignaturas) {
            if (tieneDatos(graficos.top_asignaturas.data)) {
                chartTopAsignaturas.data.labels = graficos.top_asignaturas.labels;
                chartTopAsignaturas.data.datasets[0].data = graficos.top_asignaturas.data;
                chartTopAsignaturas.update('active');
                console.log('   ✓ Bar Chart (Asignaturas) actualizado');
            } else {
                console.warn('   ⚠️ Bar Chart (Asignaturas): Sin datos para mostrar');
            }
        }
        
        console.log('✅ Todos los gráficos actualizados');
    }
    
    // ================================================
    // FUNCIÓN: MOSTRAR FILTROS ACTIVOS
    // ================================================
    
    function mostrarFiltrosActivos(filtros) {
        const indicador = document.getElementById('filtrosActivos');
        if (!indicador) return;
        
        let conteo = 0;
        const nombresActivos = [];
        
        if (filtros.anio_academico !== 'Todos') {
            conteo++;
            nombresActivos.push(`Año: ${filtros.anio_academico}`);
        }
        if (filtros.carrera !== 'Todas') {
            conteo++;
            nombresActivos.push(`Carrera: ${filtros.carrera}`);
        }
        if (filtros.campus !== 'Todos') {
            conteo++;
            nombresActivos.push(`Campus: ${filtros.campus}`);
        }
        if (filtros.dedicacion !== 'Todas') {
            conteo++;
            nombresActivos.push(`Dedicación: ${filtros.dedicacion}`);
        }
        
        if (conteo > 0) {
            indicador.innerHTML = `
                <i class="fas fa-filter me-2"></i>
                ${conteo} filtro(s) activo(s): ${nombresActivos.join(', ')}
            `;
            indicador.classList.remove('d-none');
            indicador.classList.add('alert', 'alert-info', 'mb-3');
        } else {
            indicador.classList.add('d-none');
        }
    }
    
    // ================================================
    // FUNCIÓN: MOSTRAR/OCULTAR LOADING
    // ================================================
    
    function mostrarLoading(mostrar) {
        const loading = document.getElementById('dashboardLoading');
        if (loading) {
            loading.style.display = mostrar ? 'flex' : 'none';
        }
    }
    
    // ================================================
    // FUNCIÓN: LIMPIAR FILTROS
    // ================================================
    
    function limpiarFiltros() {
        console.log('🧹 Limpiando filtros...');
        
        document.getElementById('filtroAnioAcademico').value = 'todos';
        document.getElementById('filtroCarrera').value = 'todas';
        document.getElementById('filtroCampus').value = 'todos';
        document.getElementById('filtroDedicacion').value = 'todas';
        
        aplicarFiltros();
        
        console.log('✅ Filtros limpiados');
    }
    
    // ================================================
    // EVENT LISTENERS
    // ================================================
    
    // Crear gráficos iniciales
    crearGraficosIniciales();
    
    // Botón "Aplicar Filtros"
    const btnAplicarFiltros = document.getElementById('btnAplicarFiltros');
    if (btnAplicarFiltros) {
        btnAplicarFiltros.addEventListener('click', aplicarFiltros);
    }
    
    // Botón "Limpiar Filtros"
    const btnLimpiarFiltros = document.getElementById('btnLimpiarFiltros');
    if (btnLimpiarFiltros) {
        btnLimpiarFiltros.addEventListener('click', limpiarFiltros);
    }
    
    console.log('%c 📊 Dashboard con Filtros Cargado ', 'background: #667eea; color: white; font-size: 14px; padding: 10px;');
    
});













