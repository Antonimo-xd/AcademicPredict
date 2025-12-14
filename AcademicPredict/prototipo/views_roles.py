# =============================================================================
# VISTAS PARA GESTIÓN DE ROLES Y ASIGNACIONES
# =============================================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User

from prototipo.models import (
    EstudianteUniversitario,
    AlertaEstudiante,
    IntervencionEstudiante,
    PrediccionDesercionUniversitaria
)


@login_required
@user_passes_test(lambda u: u.perfil.rol in ['admin', 'coordinador'])
def asignar_analista(request, estudiante_id):
    """
    Asigna un analista a un estudiante con alerta de riesgo.
    Solo Admin y Coordinador pueden hacer esto.
    """
    if request.method != 'POST':
        messages.error(request, "Método no permitido")
        return redirect('dashboard_ml')
    
    estudiante = get_object_or_404(EstudianteUniversitario, id=estudiante_id)
    
    # Buscar predicción más reciente
    prediccion = PrediccionDesercionUniversitaria.objects.filter(
        estudiante=estudiante
    ).order_by('-fecha_prediccion').first()
    
    if not prediccion:
        messages.error(request, "No hay predicción ML para este estudiante")
        return redirect('dashboard_ml')
    
    # Buscar o crear alerta
    alerta, created = AlertaEstudiante.objects.get_or_create(
        estudiante=estudiante,
        prediccion=prediccion,
        defaults={
            'nivel_prioridad': 'Critica' if prediccion.nivel_riesgo == 'Critico' else 'Alta',
            'estado': 'Pendiente'
        }
    )
    
    # Asignar analista
    analista_id = request.POST.get('analista_id')
    
    if not analista_id:
        messages.error(request, "Debes seleccionar un analista")
        return redirect('estudiante_detalle_ml', estudiante_id=estudiante_id)
    
    try:
        analista = User.objects.get(id=analista_id)
        
        # Verificar que es analista
        if analista.perfil.rol != 'analista':
            messages.error(request, "El usuario seleccionado no es analista")
            return redirect('estudiante_detalle_ml', estudiante_id=estudiante_id)
        
        alerta.analista_asignado = analista
        alerta.estado = 'Asignada'
        alerta.fecha_asignacion = timezone.now()
        alerta.save()
        
        messages.success(request, f"✅ Caso asignado a {analista.get_full_name()}")
        
    except User.DoesNotExist:
        messages.error(request, "Analista no encontrado")
    
    return redirect('estudiante_detalle_ml', estudiante_id=estudiante_id)


@login_required
@user_passes_test(lambda u: u.perfil.rol == 'analista')
def registrar_intervencion(request, alerta_id):
    """
    Formulario para que analista registre intervención.
    Solo el analista ASIGNADO puede registrar.
    """
    alerta = get_object_or_404(AlertaEstudiante, id=alerta_id)
    
    # Verificar que está asignado a este analista
    if alerta.analista_asignado != request.user:
        messages.error(request, "⚠️ Este caso no está asignado a ti")
        return redirect('dashboard_ml')
    
    if request.method == 'POST':
        tipo = request.POST.get('tipo_intervencion')
        fecha = request.POST.get('fecha_intervencion')
        descripcion = request.POST.get('descripcion')
        fecha_seguimiento = request.POST.get('fecha_seguimiento', None)
        
        IntervencionEstudiante.objects.create(
            alerta=alerta,
            estudiante=alerta.estudiante,
            analista=request.user,
            tipo_intervencion=tipo,
            fecha_intervencion=fecha,
            descripcion=descripcion,
            fecha_proximo_seguimiento=fecha_seguimiento if fecha_seguimiento else None
        )
        
        # Actualizar estado
        if alerta.estado == 'Asignada':
            alerta.estado = 'EnProceso'
            alerta.save()
        
        messages.success(request, "✅ Intervención registrada exitosamente")
        return redirect('estudiante_detalle_ml', estudiante_id=alerta.estudiante.id)
    
    # GET: Mostrar formulario
    contexto = {
        'alerta': alerta,
        'tipos': IntervencionEstudiante.TIPOS,
        'fecha_hoy': timezone.now().date(),
    }
    
    return render(request, 'roles/registrar_intervencion.html', contexto)


@login_required
@user_passes_test(lambda u: u.perfil.rol in ['analista', 'admin', 'coordinador'])
def marcar_resuelta(request, alerta_id):
    """
    Marca una alerta como resuelta.
    Analista asignado o Coordinadores pueden hacerlo.
    """
    if request.method != 'POST':
        messages.error(request, "Método no permitido")
        return redirect('dashboard_ml')
    
    alerta = get_object_or_404(AlertaEstudiante, id=alerta_id)
    
    # Verificar permisos
    es_analista_asignado = (request.user.perfil.rol == 'analista' and 
                           alerta.analista_asignado == request.user)
    es_coordinador = request.user.perfil.rol in ['admin', 'coordinador']
    
    if not (es_analista_asignado or es_coordinador):
        messages.error(request, "⚠️ No tienes permiso para resolver esta alerta")
        return redirect('dashboard_ml')
    
    # Marcar como resuelta
    alerta.estado = 'Resuelta'
    alerta.save()
    
    messages.success(request, "✅ Alerta marcada como resuelta")
    
    return redirect('estudiante_detalle_ml', estudiante_id=alerta.estudiante.id)


@login_required
@user_passes_test(lambda u: u.perfil.rol == 'analista')
def mis_casos_asignados(request):
    """
    Vista simplificada para analistas: solo sus casos asignados.
    """
    alertas = AlertaEstudiante.objects.filter(
        analista_asignado=request.user,
        estado__in=['Asignada', 'EnProceso']
    ).select_related('estudiante', 'prediccion').order_by('-nivel_prioridad', '-fecha_creacion')
    
    # Estadísticas
    total = alertas.count()
    criticos = alertas.filter(nivel_prioridad='Critica').count()
    altos = alertas.filter(nivel_prioridad='Alta').count()
    
    contexto = {
        'alertas': alertas,
        'total': total,
        'criticos': criticos,
        'altos': altos,
    }
    
    return render(request, 'roles/mis_casos.html', contexto)