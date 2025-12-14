document.addEventListener('DOMContentLoaded', function() {
    
    console.log('Iniciando Dashboard Avanzado - VERSION FORZADA');
    
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
    // 1. HEATMAP DE CORRELACIONES
    // ================================================
    
    function crearHeatmapCorrelaciones() {
        console.log('Creando heatmap de correlaciones...');
        
        if (!matrizCorrelacion || matrizCorrelacion.length === 0) {
            console.warn('No hay datos para el heatmap');
            document.getElementById('heatmapCorrelaciones').innerHTML = 
                '<p class="text-center text-muted py-5">Sin datos disponibles para correlaciones</p>';
            return;
        }
        
        // FORZAR el tamano del contenedor
        const container = document.getElementById('heatmapCorrelaciones');
        container.style.minHeight = '600px';
        container.style.height = '600px';
        
        const data = [{
            z: matrizCorrelacion,
            x: variablesLabels,
            y: variablesLabels,
            type: 'heatmap',
            colorscale: [
                [0, '#0066CC'],
                [0.25, '#66B2FF'],
                [0.5, '#FFFFFF'],
                [0.75, '#FFB366'],
                [1, '#FF6600']
            ],
            zmin: -1,
            zmax: 1,
            colorbar: {
                title: 'Correlacion',
                titleside: 'right',
                thickness: 20,
                len: 0.8
            },
            hovertemplate: 
                '<b>%{y}</b> vs <b>%{x}</b><br>' +
                'Correlacion: <b>%{z:.3f}</b><br>' +
                '<extra></extra>',
            text: matrizCorrelacion.map(row => 
                row.map(val => val.toFixed(2))
            ),
            texttemplate: '%{text}',
            textfont: {
                size: 10,
                color: '#000'
            },
            showscale: true
        }];
        
        // FORZAR altura especifica
        const layout = {
            title: 'Matriz de Correlaciones de Pearson',
            
            // CAMBIO: Usar autosize en lugar de width fijo
            autosize: true, 
            
            // Mantener height fijo está bien para consistencia vertical
            height: 600,    
            
            margin: { l: 180, r: 50, b: 120, t: 80 },
            xaxis: { tickangle: -45, side: 'bottom',automargin: true },
            yaxis: {automargin: true}
            
            // ELIMINADO: width: container.offsetWidth
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            displaylogo: false
        };
        
        Plotly.newPlot('heatmapCorrelaciones', data, layout, config);
        
        // Ajustar al cambiar tamano de ventana
        window.addEventListener('resize', function() {
          const graficosPlotly = ['heatmapCorrelaciones', 'boxPlotRendimiento'];
          
          graficosPlotly.forEach(function(id) {
              const el = document.getElementById(id);
              if (el) {
                  // Esta función obliga al gráfico a llenar el contenedor padre al 100%
                  Plotly.Plots.resize(el);
              }
          });
      });
        
        console.log('Heatmap creado exitosamente con altura forzada');
    }
    
    // ================================================
    // 2. BOX PLOTS
    // ================================================
    
    function crearBoxPlots() {
        console.log('Creando box plots...');
        
        if (!boxPlotData || Object.keys(boxPlotData).length === 0) {
            console.warn('No hay datos para box plots');
            document.getElementById('boxPlotRendimiento').innerHTML = 
                '<p class="text-center text-muted py-5">Sin datos disponibles para box plots</p>';
            return;
        }
        
        // FORZAR el tamano del contenedor
        const container = document.getElementById('boxPlotRendimiento');
        container.style.minHeight = '500px';
        container.style.height = '500px';
        
        const traces = [];
        
        for (const [anio, stats] of Object.entries(boxPlotData)) {
            traces.push({
                y: [stats.min, stats.q1, stats.median, stats.q3, stats.max],
                type: 'box',
                name: 'Año ' + anio,
                //boxmean: 'sd',
                marker: {
                    color: colors.primary,
                    opacity: 0.7,
                    line: { width: 1, color: colors.dark }
                },
                line: { width: 2 },
                hovertemplate: 
                    '<b>Año ' + anio + '</b><br>' +
                    'Minimo: %{y[0]:.2f}<br>' +
                    'Q1: %{y[1]:.2f}<br>' +
                    'Mediana: %{y[2]:.2f}<br>' +
                    'Q3: %{y[3]:.2f}<br>' +
                    'Maximo: %{y[4]:.2f}<br>' +
                    'Media: ' + stats.mean.toFixed(2) + '<br>' +
                    'Desv. Std: ' + stats.std.toFixed(2) +
                    '<extra></extra>'
            });
        }
        
        // FORZAR altura especifica
        const layout = {
            title: {
                text: 'Distribucion de Rendimiento por Cohorte',
                font: { size: 16, family: 'Segoe UI, sans-serif' }
            },
            yaxis: {
                title: 'Rendimiento Academico (%)',
                titlefont: { size: 13 },
                                // Rango fijo para que no se pegue al techo (100) ni al suelo (0)
                range: [-5, 105],
                zeroline: true,
                zerolinecolor: '#eee',
                titlefont: { size: 13 },
                gridcolor: 'rgba(0,0,0,0.1)'
            },
            xaxis: {
                title: 'Año de Ingreso',
                titlefont: { size: 13 }
            },
            autosize: true,
            height: 480,  // Altura fija que funciona
            margin: {
                l: 60,
                r: 30,
                t: 80,
                b: 60
            },
            showlegend: false,
            paper_bgcolor: '#ffffff',
            plot_bgcolor: '#fafafa'
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            displaylogo: false
        };
        
        Plotly.newPlot('boxPlotRendimiento', traces, layout, config);
        
        // Ajustar al cambiar tamano de ventana
        window.addEventListener('resize', function() {
          const graficosPlotly = ['heatmapCorrelaciones', 'boxPlotRendimiento'];
          
          graficosPlotly.forEach(function(id) {
              const el = document.getElementById(id);
              if (el) {
                  // Esta función obliga al gráfico a llenar el contenedor padre al 100%
                  Plotly.Plots.resize(el);
              }
          });
      });
        
        console.log('Box plots creados exitosamente con altura forzada');
    }
    
    // ================================================
    // 3. SERIE TEMPORAL
    // ================================================
    
    function crearSerieTemporal() {
        console.log('Creando serie temporal...');
        
        if (!serieTemporal || serieTemporal.length === 0) {
            console.warn('No hay datos para serie temporal');
            return;
        }
        
        const ctx = document.getElementById('chartSerieTemporal');
        if (!ctx) {
            console.error('Canvas no encontrado');
            return;
        }
        
        const labels = serieTemporal.map(item => item.anio);
        const tasas = serieTemporal.map(item => item.tasa_abandono);
        
        const n = tasas.length;
        const sumX = labels.reduce((sum, _, i) => sum + i, 0);
        const sumY = tasas.reduce((sum, val) => sum + val, 0);
        const sumXY = tasas.reduce((sum, val, i) => sum + (i * val), 0);
        const sumX2 = labels.reduce((sum, _, i) => sum + (i * i), 0);
        
        const m = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
        const b = (sumY - m * sumX) / n;
        
        const tendencia = labels.map((_, i) => m * i + b);
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Tasa de Abandono',
                        data: tasas,
                        borderColor: colors.danger,
                        backgroundColor: colors.danger + '33',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        pointBackgroundColor: colors.danger,
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    },
                    {
                        label: 'Linea de Tendencia',
                        data: tendencia,
                        borderColor: colors.dark,
                        borderWidth: 2,
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 2.5,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            padding: 15,
                            font: { size: 12, weight: '600' }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: { size: 14, weight: 'bold' },
                        bodyFont: { size: 13 },
                        padding: 12,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                if (context.datasetIndex === 0) {
                                    const item = serieTemporal[context.dataIndex];
                                    return [
                                        'Tasa: ' + context.parsed.y.toFixed(2) + '%',
                                        'Total: ' + item.total_estudiantes + ' estudiantes',
                                        'Abandonos: ' + item.abandonos
                                    ];
                                } else {
                                    return 'Tendencia: ' + context.parsed.y.toFixed(2) + '%';
                                }
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Tasa de Abandono (%)',
                            font: { size: 13, weight: '600' }
                        },
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Año de Ingreso',
                            font: { size: 13, weight: '600' }
                        },
                        grid: { display: false }
                    }
                }
            }
        });
        
        console.log('Serie temporal creada exitosamente');
    }
    
    // ================================================
    // 4. GRAFICO DE PERFILES
    // ================================================
    
    function crearGraficoPerfiles() {
        console.log('Creando grafico de perfiles...');
        
        if (!perfilesData || perfilesData.length === 0) {
            console.warn('No hay datos para perfiles');
            return;
        }
        
        const ctx = document.getElementById('chartPerfiles');
        if (!ctx) {
            console.error('Canvas no encontrado');
            return;
        }
        
        const labelsAmigables = perfilesLabels.map(label => {
            if (label === 'alto_rendimiento_activo') return 'Alto Rendimiento + Activo';
            if (label === 'alto_rendimiento_pasivo') return 'Alto Rendimiento + Pasivo';
            if (label === 'bajo_rendimiento_activo') return 'Bajo Rendimiento + Activo';
            if (label === 'bajo_rendimiento_pasivo') return 'Bajo Rendimiento + Pasivo';
            return label;
        });
        
        const coloresPerfiles = [
            colors.success,
            colors.info,
            colors.warning,
            colors.danger
        ];
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labelsAmigables,
                datasets: [{
                    data: perfilesData,
                    backgroundColor: coloresPerfiles.map(c => c + 'cc'),
                    borderColor: coloresPerfiles,
                    borderWidth: 2,
                    hoverOffset: 15
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 1.5,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 25,
                            font: { size: 13, weight: '600' },
                            boxWidth: 15
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: { size: 14, weight: 'bold' },
                        bodyFont: { size: 13 },
                        padding: 12,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return label + ': ' + value + ' (' + percentage + '%)';
                            },
                            afterLabel: function(context) {
                                const interpretaciones = [
                                    'Estudiantes modelo',
                                    'Potencial no aprovechado',
                                    'Necesitan apoyo',
                                    'Riesgo critico'
                                ];
                                return interpretaciones[context.dataIndex];
                            }
                        }
                    }
                },
                layout: {
                    padding: {
                        top: 10,
                        bottom: 40
                    }
                }
            }
        });
        
        console.log('Grafico de perfiles creado exitosamente');
    }
    
    // ================================================
    // INICIALIZAR
    // ================================================
    
    function inicializarDashboard() {
        console.log('Inicializando visualizaciones con tamanos forzados...');
        
        try {
            crearHeatmapCorrelaciones();
            crearBoxPlots();
            crearSerieTemporal();
            crearGraficoPerfiles();
            
            console.log('Dashboard Avanzado Cargado - VERSION FORZADA');
        } catch (error) {
            console.error('Error al inicializar dashboard:', error);
        }
    }
    
    // Esperar un momento antes de inicializar
    setTimeout(inicializarDashboard, 100);
    
});




















