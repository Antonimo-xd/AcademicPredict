from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Count, Avg, Q
from django.http import JsonResponse
import logging
import json
import numpy as np

from prototipo.models import (
    CarreraUniversitaria,
    EstudianteUniversitario,
    AsignaturaUniversitaria,
    RegistroAcademicoUniversitario,
    AlertaEstudiante,
    IntervencionEstudiante,
    FichaSeguimientoEstudiante
)

from prototipo.service.import_service_universidad import ImportadorDatosUniversitarios

logger = logging.getLogger(__name__)

@login_required
@user_passes_test(lambda u: hasattr(u, 'perfil'))  
def home(request):
    """Vista principal del sistema."""
    
    total_alertas = AlertaEstudiante.objects.filter(
    estado__in=['pendiente', 'en_revision'],
    visible=True
    ).count()

    alertas_criticas = AlertaEstudiante.objects.filter(
        prioridad='critica',
        estado__in=['pendiente', 'en_revision'],
        visible=True
    ).count()

    estudiantes_seguimiento = FichaSeguimientoEstudiante.objects.filter(
        en_seguimiento=True
    ).count()

    total_intervenciones = IntervencionEstudiante.objects.count()

    alertas_recientes = AlertaEstudiante.objects.select_related(
        'estudiante', 'estudiante__carrera', 'prediccion'
    ).filter(
        estado='pendiente',
        visible=True
    ).order_by('-prioridad', '-fecha_creacion')[:3]

    estudiantes_recientes = EstudianteUniversitario.objects.select_related(
        'carrera', 'ficha_seguimiento', 'ficha_seguimiento__tutor_principal'
    ).filter(
        ficha_seguimiento__en_seguimiento=True
    ).order_by('-ficha_seguimiento__fecha_actualizacion')[:5]

    total_carreras = CarreraUniversitaria.objects.count()
    total_estudiantes = EstudianteUniversitario.objects.count()
    total_asignaturas = AsignaturaUniversitaria.objects.count()
    total_registros = RegistroAcademicoUniversitario.objects.count()

    contexto = {
        # Estadísticas básicas
        'total_carreras': total_carreras,
        'total_estudiantes': total_estudiantes,
        'total_asignaturas': total_asignaturas,
        'total_registros': total_registros,
        
        # Estadísticas de alertas 
        'total_alertas': total_alertas,
        'alertas_criticas': alertas_criticas,
        'estudiantes_seguimiento': estudiantes_seguimiento,
        'total_intervenciones': total_intervenciones,
        
        # Datos para mostrar en home 
        'alertas_recientes': alertas_recientes,
        'estudiantes_recientes': estudiantes_recientes,
        'user_rol': request.user.perfil.rol,
    }
    
    return render(request, 'home.html', contexto)

@login_required
@user_passes_test(lambda u: u.perfil.rol == 'admin', login_url='/sin-permiso/')
def importar_datos_universidad(request):
    """Vista para importar datos del dataset universitario desde CSV."""
    
    if request.method == 'POST':
        if 'archivo_csv' not in request.FILES:
            messages.error(request, '❌ Por favor selecciona un archivo CSV.')
            return redirect('importar_datos_universidad')
        
        archivo = request.FILES['archivo_csv']
        
        if not archivo.name.endswith('.csv'):
            messages.error(request, '❌ El archivo debe ser formato CSV (.csv)')
            return redirect('importar_datos_universidad')
        
        try:
            ruta_temp = default_storage.save(
                f'temp_uploads/{archivo.name}',
                ContentFile(archivo.read())
            )
            ruta_completa = default_storage.path(ruta_temp)
            
            logger.info(f"Archivo guardado en: {ruta_completa}")
            messages.info(request, f"📁 Archivo recibido: {archivo.name}")
            messages.info(request, "🔄 Iniciando importación... Esto puede tardar varios minutos.")
            

            
            importador = ImportadorDatosUniversitarios(ruta_completa)
            estadisticas = importador.importar_completo()
            reporte = importador.generar_reporte()
            logger.info(reporte)
            default_storage.delete(ruta_temp)
            
            messages.success(request, f"""
                ✅ Importación completada exitosamente!
                
                📊 Resultados:
                • Carreras: {estadisticas['carreras_creadas']}
                • Estudiantes: {estadisticas['estudiantes_creados']}
                • Asignaturas: {estadisticas['asignaturas_creadas']}
                • Registros creados: {estadisticas['registros_creados']}
                • Registros actualizados: {estadisticas['registros_actualizados']}
                • Errores: {len(estadisticas['errores'])}
            """)
            
            request.session['ultima_importacion'] = {
                'carreras': estadisticas['carreras_creadas'],
                'estudiantes': estadisticas['estudiantes_creados'],
                'asignaturas': estadisticas['asignaturas_creadas'],
                'registros_creados': estadisticas['registros_creados'],
                'registros_actualizados': estadisticas['registros_actualizados'],
                'errores': len(estadisticas['errores']),
                'reporte': reporte,
            }
            
            return redirect('importar_datos_universidad')
            
        except Exception as e:
            logger.error(f"Error durante importación: {str(e)}")
            messages.error(request, f"❌ Error durante la importación: {str(e)}")
            try:
                default_storage.delete(ruta_temp)
            except:
                pass
            return redirect('importar_datos_universidad')
    
    contexto = {}
    
    if 'ultima_importacion' in request.session:
        contexto['ultima_importacion'] = request.session['ultima_importacion']
    
    contexto['estadisticas_bd'] = {
        'carreras': CarreraUniversitaria.objects.count(),
        'estudiantes': EstudianteUniversitario.objects.count(),
        'asignaturas': AsignaturaUniversitaria.objects.count(),
        'registros': RegistroAcademicoUniversitario.objects.count(),
    }
    
    return render(request, 'universidad/importar_datos_universidad.html', contexto)

@login_required
@user_passes_test(lambda u: hasattr(u, 'perfil'))
def dashboard_universidad(request):
    """Dashboard básico con métricas generales y gráficos."""

    logger.info("📄 Iniciando carga del dashboard...")

    user_rol = request.user.perfil.rol

    estudiantes = EstudianteUniversitario.objects.all()

    if user_rol == 'coordinador_carrera':
        carrera = request.user.perfil.carrera_asignada
        if carrera:
            estudiantes = estudiantes.filter(carrera=carrera)
        else:
            messages.error(request, "No tienes carrera asignada")
            return redirect('home')

    # Ahora SÍ usa la variable filtrada:
    total_estudiantes = estudiantes.count()  # ✅ Usa estudiantes filtrados
    total_abandonos = estudiantes.filter(estado_abandono='Abandono').count()  # ✅ Filtrados
    
    if total_estudiantes > 0:
        tasa_abandono = (total_abandonos / total_estudiantes) * 100
    else:
        tasa_abandono = 0
    
    registros_validos = RegistroAcademicoUniversitario.objects.filter(creditos_aprobados_total_anio__gt=0)
    
    if registros_validos.exists():
        promedio_raw = registros_validos.aggregate(prom=Avg('creditos_aprobados_total_anio'))
        promedio_creditos = float(promedio_raw['prom'] or 0)
    else:
        promedio_creditos = 0.0
    
    total_carreras = CarreraUniversitaria.objects.count()
    
    abandono_stats = estudiantes.values('estado_abandono').annotate(
        total=Count('id')
    )

    abandono_labels = []
    abandono_data = []

    for stat in abandono_stats:
        label = 'Desertores' if stat['estado_abandono'] == 'Abandono' else 'Activos'
        abandono_labels.append(label)
        abandono_data.append(stat['total'])
    
    abandono_por_anio = estudiantes.filter(
        estado_abandono='Abandono',
        anio_ingreso_universidad__gt=2000
    ).values('anio_ingreso_universidad').annotate(
        total=Count('id')
    ).order_by('anio_ingreso_universidad')
    
    abandono_anio_labels = [str(x['anio_ingreso_universidad']) for x in abandono_por_anio]
    abandono_anio_data = [x['total'] for x in abandono_por_anio]
    
    abandono_por_carrera = estudiantes.filter(
        estado_abandono='Abandono'
    ).values('carrera__codigo_carrera').annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    abandono_carrera_labels = [x['carrera__codigo_carrera'] for x in abandono_por_carrera]
    abandono_carrera_data = [x['total'] for x in abandono_por_carrera]
    
    rendimientos_qs = RegistroAcademicoUniversitario.objects.filter(
        rendimiento_total_anio__gt=0,
        rendimiento_total_anio__lte=100
    ).values_list('rendimiento_total_anio', flat=True)
    
    conteo_rangos = [0] * 10 
    rangos_labels = ["0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"]
    
    for val in rendimientos_qs[:20000]: 
        v = float(val)
        idx = int(v // 10)
        if idx >= 10: idx = 9
        conteo_rangos[idx] += 1
        
    top_asignaturas = RegistroAcademicoUniversitario.objects.values(
        'asignatura__codigo_asignatura'
    ).annotate(
        total=Count('estudiante', distinct=True)
    ).order_by('-total')[:10]
    
    top_asig_labels = [x['asignatura__codigo_asignatura'] for x in top_asignaturas]
    top_asig_data = [x['total'] for x in top_asignaturas]
    
    anios_disponibles = RegistroAcademicoUniversitario.objects.values_list(
        'anio_academico', flat=True
    ).distinct().order_by('-anio_academico')
    
    carreras_disponibles = CarreraUniversitaria.objects.values('id', 'codigo_carrera').order_by('codigo_carrera')
    campus_disponibles = CarreraUniversitaria.objects.values_list('campus', flat=True).distinct().order_by('campus')
    
    contexto = {
        'total_estudiantes': total_estudiantes,
        'total_abandonos': total_abandonos,
        'tasa_abandono': round(tasa_abandono, 2),
        'promedio_creditos': round(promedio_creditos, 2),
        'total_carreras': total_carreras,
        
        'abandono_labels': json.dumps(abandono_labels),
        'abandono_data': json.dumps(abandono_data),
        'abandono_anio_labels': json.dumps(abandono_anio_labels),
        'abandono_anio_data': json.dumps(abandono_anio_data),
        'abandono_carrera_labels': json.dumps(abandono_carrera_labels),
        'abandono_carrera_data': json.dumps(abandono_carrera_data),
        'rendimiento_labels': json.dumps(rangos_labels),
        'rendimiento_data': json.dumps(conteo_rangos),
        'top_asignaturas_labels': json.dumps(top_asig_labels),
        'top_asignaturas_data': json.dumps(top_asig_data),
        
        'anios_disponibles': anios_disponibles,
        'carreras_disponibles': carreras_disponibles,
        'campus_disponibles': campus_disponibles,

        'user_rol': user_rol,
        'puede_importar': user_rol == 'admin',
    }
    
    return render(request, 'universidad/dashboard.html', contexto)

@login_required
@user_passes_test(lambda u: hasattr(u, 'perfil'))
def dashboard_filtrado_ajax(request):
    """Recibe parámetros GET y devuelve JSON con los datos recalculados."""
    
    user_rol = request.user.perfil.rol
    
    estudiantes_qs = EstudianteUniversitario.objects.all()
    
    if user_rol == 'coordinador_carrera':
        carrera = request.user.perfil.carrera_asignada
        if carrera:
            estudiantes_qs = estudiantes_qs.filter(carrera=carrera)

    anio = request.GET.get('anio_academico')
    carrera = request.GET.get('carrera')
    campus = request.GET.get('campus')
    dedicacion = request.GET.get('dedicacion')
    
    filtro_estudiante = Q()
    if carrera and carrera != 'todas':
        filtro_estudiante &= Q(carrera__codigo_carrera=carrera)
    if dedicacion and dedicacion != 'todas':
        filtro_estudiante &= Q(dedicacion_estudios=dedicacion)
    if campus and campus != 'todos':
        filtro_estudiante &= Q(carrera__campus=campus)
        
    filtro_registro = Q()
    if anio and anio != 'todos':
        filtro_registro &= Q(anio_academico=anio)
    if carrera and carrera != 'todas':
        filtro_registro &= Q(estudiante__carrera__codigo_carrera=carrera)
    if dedicacion and dedicacion != 'todas':
        filtro_registro &= Q(estudiante__dedicacion_estudios=dedicacion)
    if campus and campus != 'todos':
        filtro_registro &= Q(estudiante__carrera__campus=campus)

    # 3. Recalcular KPIs (Aquí están las variables que faltaban)
    total_estudiantes = EstudianteUniversitario.objects.filter(filtro_estudiante).count()
    
    total_abandonos = EstudianteUniversitario.objects.filter(filtro_estudiante, estado_abandono='Abandono').count()
    
    tasa = (total_abandonos / total_estudiantes * 100) if total_estudiantes > 0 else 0
    
    registros_credito = RegistroAcademicoUniversitario.objects.filter(filtro_registro, creditos_aprobados_total_anio__gt=0)
    promedio_creditos = registros_credito.aggregate(prom=Avg('creditos_aprobados_total_anio'))['prom'] or 0
    
    filtros_carreras = Q()
    if carrera and carrera != 'todas':
        filtros_carreras &= Q(codigo_carrera=carrera)
    if campus and campus != 'todos':
        filtros_carreras &= Q(campus=campus)
        
    total_carreras = CarreraUniversitaria.objects.filter(filtros_carreras).count()

    # 4. Recalcular Gráficos
    abandono_stats = EstudianteUniversitario.objects.filter(filtro_estudiante).values('estado_abandono').annotate(t=Count('id'))
    pie_labels = ['Desertores' if x['estado_abandono']=='Abandono' else 'Activos' for x in abandono_stats]
    pie_data = [x['t'] for x in abandono_stats]
    
    abandono_anio = EstudianteUniversitario.objects.filter(filtro_estudiante, estado_abandono='Abandono', anio_ingreso_universidad__gt=2000).values('anio_ingreso_universidad').annotate(t=Count('id')).order_by('anio_ingreso_universidad')
    line_labels = [str(x['anio_ingreso_universidad']) for x in abandono_anio]
    line_data = [x['t'] for x in abandono_anio]
    
    abandono_carrerra = EstudianteUniversitario.objects.filter(filtro_estudiante, estado_abandono='Abandono').values('carrera__codigo_carrera').annotate(t=Count('id')).order_by('-t')[:10]
    bar_labels = [x['carrera__codigo_carrera'] for x in abandono_carrerra]
    bar_data = [x['t'] for x in abandono_carrerra]

    rendimiento_valores = RegistroAcademicoUniversitario.objects.filter(filtro_registro, rendimiento_total_anio__gt=0, rendimiento_total_anio__lte=100).values_list('rendimiento_total_anio', flat=True)[:10000]
    historico_data = [0]*10
    for valor in rendimiento_valores:
        idx = int(float(valor) // 10)
        if idx >= 10: idx = 9
        historico_data[idx] += 1
        
    top_asignatura = RegistroAcademicoUniversitario.objects.filter(filtro_registro).values('asignatura__codigo_asignatura').annotate(t=Count('estudiante', distinct=True)).order_by('-t')[:10]
    top_asig_labels = [x['asignatura__codigo_asignatura'] for x in top_asignatura]
    top_asig_data = [x['t'] for x in top_asignatura]

    data = {
        'success': True,
        'kpis': {
            'total_estudiantes': total_estudiantes,
            'total_abandonos': total_abandonos,
            'tasa_abandono': round(tasa, 2),
            'promedio_creditos': round(float(promedio_creditos), 2),
            'total_carreras': total_carreras
        },
        'graficos': {
            'abandono_pie': {'labels': pie_labels, 'data': pie_data},
            'abandono_anio': {'labels': line_labels, 'data': line_data},
            'abandono_carrera': {'labels': bar_labels, 'data': bar_data},
            'rendimiento': {'labels': ["0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"], 'data': historico_data},
            'top_asignaturas': {'labels': top_asig_labels, 'data': top_asig_data}
        },
        'filtros_aplicados': {
            'anio': anio, 'carrera': carrera
        }
    }
    
    return JsonResponse(data)

@login_required
@user_passes_test(lambda u: u.perfil.rol in ['admin', 'coordinador', 'coordinador_carrera'])
def dashboard_avanzado(request):
    """Vista para el dashboard avanzado con análisis estadístico."""
    
    logger.info("🚀 Cargando Dashboard Avanzado...")

    logger.info("📊 Calculando matriz de correlaciones...")
    
    user_rol = request.user.perfil.rol

    estudiantes = EstudianteUniversitario.objects.all()
    
    if user_rol == 'coordinador_carrera':
        carrera = request.user.perfil.carrera_asignada
        if carrera:
            estudiantes = estudiantes.filter(carrera=carrera)

    variables_modelo = [
        'creditos_aprobados_total_anio',
        'creditos_matriculados_total_anio',
        'rendimiento_total_anio',
        'eventos_lms_total',
        'visitas_lms_total',
        'dias_wifi_total',
    ]
    
    variables_labels = [
        'Créditos Aprobados',
        'Créditos Matriculados',
        'Rendimiento',
        'Eventos LMS',
        'Visitas LMS',
        'Días WiFi'
    ]
    
    registros = RegistroAcademicoUniversitario.objects.filter(
        rendimiento_total_anio__gt=0
    ).values(*variables_modelo)[:5000] 
    
    if registros:
        data_array = []
        for r in registros:
            fila = [float(r[v] or 0) for v in variables_modelo]
            data_array.append(fila)
        
        if len(data_array) > 1:
            matriz_correlacion = np.corrcoef(np.array(data_array).T).tolist()
            matriz_correlacion = [[0 if np.isnan(x) else x for x in row] for row in matriz_correlacion]
        else:
            matriz_correlacion = []
            
        logger.info(f"✅ Matriz calculada con {len(data_array)} registros")
    else:
        matriz_correlacion = []
        logger.warning("⚠️ No hay datos suficientes para correlaciones")
    
    logger.info("📦 Calculando distribuciones por grupo...")
    
    box_plot_data = {}
    
    anios_ingreso = EstudianteUniversitario.objects.filter(
        anio_ingreso_universidad__gt=2015
    ).values_list('anio_ingreso_universidad', flat=True).distinct().order_by('-anio_ingreso_universidad')[:5]
    
    for anio in anios_ingreso:
        rendimientos = list(RegistroAcademicoUniversitario.objects.filter(
            estudiante__anio_ingreso_universidad=anio,
            rendimiento_total_anio__gt=0
        ).values_list('rendimiento_total_anio', flat=True)[:500])
        
        if rendimientos:
            vals = [float(r) for r in rendimientos]
            
            box_plot_data[str(anio)] = {
                'min': float(np.min(vals)),
                'q1': float(np.percentile(vals, 25)),
                'median': float(np.median(vals)),
                'q3': float(np.percentile(vals, 75)),
                'max': float(np.max(vals)),
                'mean': float(np.mean(vals)),
                'std': float(np.std(vals))
            }
    
    logger.info("📈 Analizando series temporales...")
    
    serie_temporal = []
    anios_serie = sorted(list(anios_ingreso))
    
    for anio in anios_serie:
        total = EstudianteUniversitario.objects.filter(anio_ingreso_universidad=anio).count()
        abandonos = EstudianteUniversitario.objects.filter(
            anio_ingreso_universidad=anio, 
            estado_abandono='Abandono'
        ).count()
        
        tasa = (abandonos / total * 100) if total > 0 else 0
        
        serie_temporal.append({
            'anio': str(anio),
            'tasa_abandono': round(tasa, 2),
            'total_estudiantes': total,
            'abandonos': abandonos
        })
    
    logger.info("👥 Analizando perfiles...")
    
    perfiles = {
        'alto_rendimiento_activo': 0,
        'alto_rendimiento_pasivo': 0,
        'bajo_rendimiento_activo': 0,
        'bajo_rendimiento_pasivo': 0,
    }
    
    registros_perfiles = RegistroAcademicoUniversitario.objects.filter(
        rendimiento_total_anio__gt=0
    ).values('rendimiento_total_anio', 'eventos_lms_total')[:5000]
    
    for r in registros_perfiles:
        rend = float(r['rendimiento_total_anio'] or 0)
        evts = int(r['eventos_lms_total'] or 0)

        if rend >= 70:
            if evts >= 100: perfiles['alto_rendimiento_activo'] += 1
            else: perfiles['alto_rendimiento_pasivo'] += 1
        else:
            if evts >= 100: perfiles['bajo_rendimiento_activo'] += 1
            else: perfiles['bajo_rendimiento_pasivo'] += 1
    
    contexto = {
        'matriz_correlacion': json.dumps(matriz_correlacion),
        'variables_labels': json.dumps(variables_labels),
        'box_plot_data': json.dumps(box_plot_data),
        'serie_temporal': json.dumps(serie_temporal),
        'perfiles_labels': json.dumps(list(perfiles.keys())),
        'perfiles_data': json.dumps(list(perfiles.values())),
        
        'total_estudiantes': estudiantes.count(),
        'total_registros': RegistroAcademicoUniversitario.objects.count(),
    }
    
    return render(request, 'universidad/dashboard_avanzado.html', contexto)

@login_required
@user_passes_test(lambda u: u.perfil.rol in ['admin', 'coordinador', 'coordinador_carrera'])
def dashboard_avanzado_filtrado(request):
    """Aplica filtros al dashboard avanzado y recalcula estadísticas."""
    
    user_rol = request.user.perfil.rol
    anio = request.GET.get('anio_academico')
    carrera = request.GET.get('carrera')
    campus = request.GET.get('campus')
    dedicacion = request.GET.get('dedicacion')
    
    conjunto_consultas = RegistroAcademicoUniversitario.objects.filter(rendimiento_total_anio__gt=0)
    
    if anio and anio != 'todos':
        conjunto_consultas = conjunto_consultas.filter(anio_academico=anio)
    if carrera and carrera != 'todas':
        conjunto_consultas = conjunto_consultas.filter(estudiante__carrera__codigo_carrera=carrera)
    if campus and campus != 'todos':
        conjunto_consultas = conjunto_consultas.filter(estudiante__carrera__campus=campus)
    if dedicacion and dedicacion != 'todas':
        conjunto_consultas = conjunto_consultas.filter(estudiante__dedicacion_estudios=dedicacion)

    return JsonResponse({'success': True, 'message': 'Filtros aplicados (Lógica pendiente de implementación completa)'})

@login_required
def sin_permiso(request):
    """Página que muestra cuando el usuario no tiene permisos."""
    return render(request, 'sin_permiso.html', {
        'user_rol': request.user.perfil.rol if hasattr(request.user, 'perfil') else 'desconocido'
    })

