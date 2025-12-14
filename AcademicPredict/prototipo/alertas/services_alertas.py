"""
Servicios de negocio para el sistema de alertas.
Lógica reutilizable separada de las vistas.
"""

from prototipo.models import (
    PrediccionDesercion,
    AlertaEstudiante,
    FichaSeguimientoEstudiante
)


def generar_alerta_automatica(prediccion):
    """
    Genera alerta automática basada en una predicción.
    
    Args:
        prediccion: Instancia de PrediccionDesercion
    
    Returns:
        AlertaEstudiante creada o None
    """
    
    # Determinar si debe crear alerta
    if prediccion.clasificacion_riesgo not in ['alto', 'critico']:
        return None
    
    # Determinar prioridad
    if prediccion.clasificacion_riesgo == 'critico':
        prioridad = 'critica'
    else:
        prioridad = 'alta'
    
    # Crear alerta
    alerta = AlertaEstudiante.objects.create(
        estudiante=prediccion.estudiante,
        prediccion=prediccion,
        tipo_alerta='riesgo_alto',
        prioridad=prioridad,
        titulo=f"Estudiante en {prediccion.get_clasificacion_riesgo_display()}",
        mensaje=f"Índice de riesgo: {prediccion.indice_riesgo:.1f}%",
        indice_riesgo_momento=prediccion.indice_riesgo
    )
    
    return alerta


def actualizar_ficha_seguimiento(estudiante):
    """
    Actualiza contadores de la ficha de seguimiento.
    
    Args:
        estudiante: Instancia de EstudianteUniversitario
    """
    
    ficha, created = FichaSeguimientoEstudiante.objects.get_or_create(
        estudiante=estudiante
    )
    
    # Actualizar contadores
    ficha.alertas_activas = estudiante.alertas.filter(
        estado__in=['pendiente', 'en_revision'],
        visible=True
    ).count()
    
    ficha.total_intervenciones = estudiante.intervenciones.count()
    
    ficha.intervenciones_exitosas = estudiante.intervenciones.filter(
        resultado='exitosa'
    ).count()
    
    # Última predicción
    ultima = estudiante.predicciones_alertas.filter(activa=True).first()
    if ultima:
        ficha.ultimo_indice_riesgo = ultima.indice_riesgo
        ficha.ultima_clasificacion = ultima.clasificacion_riesgo
        ficha.ultima_fecha_prediccion = ultima.fecha_prediccion
    
    ficha.save()
    
    return ficha