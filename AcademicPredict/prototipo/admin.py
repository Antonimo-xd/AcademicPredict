from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CarreraUniversitaria,
    EstudianteUniversitario,
    AsignaturaUniversitaria,
    RegistroAcademicoUniversitario,
    PrediccionDesercionUniversitaria,
    AsignaturaCriticaUniversitaria,
    TrazabilidadPrediccionDesercion,
    AlertaEstudiante,
    IntervencionEstudiante,
    FichaSeguimientoEstudiante,
    PerfilUsuario
)

# =============================================================================
# CONFIGURACIÓN GENERAL DEL SITIO
# =============================================================================
admin.site.site_header = "AcademicPredict - Panel de Control"
admin.site.site_title = "AcademicPredict Admin"
admin.site.index_title = "Gestión de Datos Universitarios"


@admin.register(CarreraUniversitaria)
class CarreraUniversitariaAdmin(admin.ModelAdmin):
    list_display = [
        'codigo_carrera', 
        'nombre', 
        'campus', 
        'creditos_totales_requeridos', 
        'fecha_creacion'
    ]
    list_filter = ['campus']
    search_fields = ['codigo_carrera', 'nombre']
    
    # Eliminamos 'coordinador' que ya no existe en el modelo
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo_carrera', 'nombre', 'campus')
        }),
        ('Plan de Estudios', {
            'fields': ('creditos_totales_requeridos',)
        }),
    )


@admin.register(EstudianteUniversitario)
class EstudianteUniversitarioAdmin(admin.ModelAdmin):
    list_display = [
        'codigo_estudiante',
        'carrera',
        'status_abandono_colored', # Coloreado visual
        'anio_ingreso_universidad',
        'tipo_acceso_universidad'
    ]
    
    list_filter = [
        'estado_abandono', 
        'carrera__campus', # Filtro por campus a través de la carrera
        'dedicacion_estudios',
        'es_desplazado',
        'anio_ingreso_universidad'
    ]
    
    search_fields = ['codigo_estudiante']
    
    # Función para colorear el estado en la lista
    def status_abandono_colored(self, obj):
        color = 'red' if obj.estado_abandono == 'Abandono' else 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, 
            obj.estado_abandono
        )
    status_abandono_colored.short_description = "Estado Abandono"


@admin.register(AsignaturaUniversitaria)
class AsignaturaUniversitariaAdmin(admin.ModelAdmin):
    list_display = [
        'codigo_asignatura',
        'nombre',
        'creditos',
        'anio_carrera',
        'carrera'
    ]
    list_filter = ['anio_carrera', 'carrera']
    search_fields = ['codigo_asignatura', 'nombre']


@admin.register(RegistroAcademicoUniversitario)
class RegistroAcademicoUniversitarioAdmin(admin.ModelAdmin):
    """
    El admin más importante. Aquí verás los datos enriquecidos.
    """
    list_display = [
        'estudiante',
        'anio_academico',
        'tasa_aprobacion_visual', # Calculado
        'progreso_carrera_visual', # Calculado
        'creditos_aprobados_total_anio',
        'matricula_activa'
    ]
    
    list_filter = [
        'anio_academico',
        'matricula_activa',
        'anio_carrera_minimo'
    ]
    
    search_fields = ['estudiante__codigo_estudiante', 'asignatura__codigo_asignatura']
    
    # Agrupamos los campos para que no sea una lista infinita
    fieldsets = (
        ('Contexto', {
            'fields': ('estudiante', 'asignatura', 'anio_academico', 'matricula_activa')
        }),
        ('Golden Features (Clave para ML)', {
            'fields': (
                'creditos_matriculados_movilidad', 
                'creditos_matriculados_practicas',
                'creditos_matriculados_oficiales'
            ),
            'classes': ('wide', 'extrapretty'), # Estilo visual
        }),
        ('Totales Anuales', {
            'fields': (
                'creditos_matriculados_total_anio', 
                'creditos_aprobados_total_anio',
                'creditos_aprobados_titulo_global'
            )
        }),
        ('Huella Digital (LMS)', {
            'fields': (
                'eventos_lms_total', 
                'visitas_lms_total', 
                'tareas_entregadas_total',
                'tiempo_total_minutos',
                'dias_wifi_total'
            )
        }),
        ('Métricas Calculadas', {
            'fields': ('tasa_aprobacion', 'progreso_carrera', 'promedio_actividad_lms_diaria'),
        })
    )
    
    readonly_fields = ['tasa_aprobacion', 'progreso_carrera', 'promedio_actividad_lms_diaria']

    # --- Funciones para mostrar métricas calculadas en la lista ---
    
    def tasa_aprobacion_visual(self, obj):
        valor = obj.tasa_aprobacion
        color = 'green' if valor >= 80 else 'orange' if valor >= 50 else 'red'
        return format_html(
            '<b style="color: {};">{:.1f}%</b>', color, valor
        )
    tasa_aprobacion_visual.short_description = "Tasa Éxito"

    def progreso_carrera_visual(self, obj):
        return f"{obj.progreso_carrera:.1f}%"
    progreso_carrera_visual.short_description = "Progreso"


@admin.register(PrediccionDesercionUniversitaria)
class PrediccionDesercionUniversitariaAdmin(admin.ModelAdmin):
    list_display = [
        'estudiante', 
        'nivel_riesgo_colored', 
        'probabilidad_desercion', 
        'es_anomalia', 
        'fecha_prediccion'
    ]
    
    list_filter = ['nivel_riesgo', 'es_anomalia', 'modelo_usado']
    search_fields = ['estudiante__codigo_estudiante']
    readonly_fields = ['fecha_prediccion', 'factores_riesgo']

    def nivel_riesgo_colored(self, obj):
        colors = {
            'Bajo': 'green',
            'Medio': 'orange',
            'Alto': 'red',
            'Critico': 'darkred'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.nivel_riesgo, 'black'),
            obj.nivel_riesgo
        )
    nivel_riesgo_colored.short_description = "Riesgo"


@admin.register(AsignaturaCriticaUniversitaria)
class AsignaturaCriticaUniversitariaAdmin(admin.ModelAdmin):
    list_display = [
        'asignatura',
        'anio_academico',
        'tasa_reprobacion_visual',
        'total_estudiantes_reprobados',
        'es_critica'
    ]
    
    list_filter = ['es_critica', 'anio_academico']
    
    def tasa_reprobacion_visual(self, obj):
        # Si la reprobación es alta (>40%), poner en rojo
        color = 'red' if obj.tasa_reprobacion > 40 else 'black'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, obj.tasa_reprobacion
        )
    tasa_reprobacion_visual.short_description = "% Reprobación"

@admin.register(TrazabilidadPrediccionDesercion)
class TrazabilidadPrediccionDesercionAdmin(admin.ModelAdmin):
    list_display = [
        'estudiante',
        'clasificacion_riesgo',
        'indice_riesgo',
        'fecha_prediccion',
        'activa'
    ]
    list_filter = ['clasificacion_riesgo', 'activa', 'fecha_prediccion']
    search_fields = ['estudiante__codigo_estudiante']
    ordering = ['-fecha_prediccion']


@admin.register(AlertaEstudiante)
class AlertaEstudianteAdmin(admin.ModelAdmin):
    list_display = [
        'estudiante',
        'tipo_alerta',
        'prioridad',
        'estado',
        'tutor_asignado',
        'fecha_creacion'
    ]
    list_filter = ['tipo_alerta', 'prioridad', 'estado', 'fecha_creacion']
    search_fields = ['estudiante__codigo_estudiante', 'titulo']
    ordering = ['-fecha_creacion']


@admin.register(IntervencionEstudiante)
class IntervencionEstudianteAdmin(admin.ModelAdmin):
    list_display = [
        'estudiante',
        'tipo_intervencion', 
        'fecha_intervencion',
        'responsable',
        'resultado'
    ]
    list_filter = ['tipo_intervencion', 'resultado', 'fecha_intervencion'] 
    
    search_fields = ['estudiante__codigo_estudiante', 'titulo']
    ordering = ['-fecha_intervencion']


@admin.register(FichaSeguimientoEstudiante)
class FichaSeguimientoEstudianteAdmin(admin.ModelAdmin):
    list_display = [
        'estudiante',
        'ultimo_indice_riesgo',
        'ultima_clasificacion',
        'alertas_activas',
        'en_seguimiento',
        'tutor_principal'
    ]
    list_filter = ['en_seguimiento', 'ultima_clasificacion']
    search_fields = ['estudiante__codigo_estudiante']


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'rol', 'carrera_asignada']
    list_filter = ['rol']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Rol y Permisos', {
            'fields': ('rol', 'carrera_asignada')
        }),
    )