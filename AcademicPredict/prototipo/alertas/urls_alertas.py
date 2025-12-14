"""
URLs del Sistema de Alertas
AcademicPredict - Bastián

EXPLICACIÓN:
Este archivo define todas las rutas (URLs) del sistema de alertas.
Django usa estas rutas para saber qué vista (función) ejecutar cuando
el usuario accede a una URL específica.
"""

from django.urls import path
from . import views_alertas as views

# app_name permite hacer reverse con 'alertas:nombre'
# Ejemplo: {% url 'alertas:dashboard' %}
app_name = 'alertas'

urlpatterns = [
    # ================================================================
    # DASHBOARD DE ALERTAS
    # ================================================================
    # URL: /alertas/
    # Vista principal con KPIs y tabla de alertas
    path('', views.dashboard, name='dashboard'),
    
    
    # ================================================================
    # DETALLE Y GESTIÓN DE ALERTAS
    # ================================================================
    # URL: /alertas/detalle/1/
    # Muestra información completa de una alerta específica
    path('detalle/<int:pk>/', views.detalle, name='detalle'),
    
    # URL: /alertas/cambiar-estado/1/
    # Cambia el estado de una alerta (pendiente, en_revision, resuelta, descartada)
    path('cambiar-estado/<int:pk>/', views.cambiar_estado, name='cambiar_estado'),
    
    
    # ================================================================
    # SEGUIMIENTO DE ESTUDIANTES
    # ================================================================
    # URL: /alertas/seguimiento/EST001/
    # Ficha individual del estudiante con historial de intervenciones
    # NOTA: Usa código de estudiante (str), no ID numérico
    path('seguimiento/<str:codigo>/', views.seguimiento, name='seguimiento'),
    
    # URL: /alertas/nueva-intervencion/EST001/
    # Registra una nueva intervención para el estudiante
    path('nueva-intervencion/<str:codigo>/', views.nueva_intervencion, name='nueva_intervencion'),
    
    # URL: /alertas/cambiar-estado-seguimiento/EST001/
    # Activa o desactiva el seguimiento del estudiante
    path('cambiar-estado-seguimiento/<str:codigo>/', views.cambiar_estado_seguimiento, name='cambiar_estado_seguimiento'),
    
    
    # ================================================================
    # LISTADO DE ESTUDIANTES EN SEGUIMIENTO
    # ================================================================
    # URL: /alertas/listado/
    # Lista todos los estudiantes en seguimiento activo
    path('listado/', views.listado_seguimiento, name='listado_seguimiento'),
    
    
    # ================================================================
    # REPORTES
    # ================================================================
    # URL: /alertas/reportes/
    # Generación de reportes (Excel, PDF, CSV)
    path('reportes/', views.reportes, name='reporte'),
    
    # URL: /alertas/generar-reporte/
    # Procesa el formulario y genera el reporte
    path('generar-reporte/', views.generar_reporte, name='generar_reporte'),

    path('exportar/seguimiento/', views.exportar_seguimiento, name='exportar_seguimiento'),
    
    
    # ================================================================
    # API ENDPOINTS
    # ================================================================
    # URL: /alertas/api/urgentes/
    # API JSON para obtener alertas urgentes (para dropdown en sidebar)
    # Retorna: {'total': 5, 'alertas': [...]}
    path('api/urgentes/', views.api_alertas_urgentes, name='api_urgentes'),
]
