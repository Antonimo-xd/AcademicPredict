from django.urls import path
from . import views_ml

app_name = 'ml'

urlpatterns = [

    path('dashboard/', views_ml.dashboard_ml, name='dashboard_ml'),
    path('ejecutar/', views_ml.ejecutar_deteccion_api, name='ejecutar_deteccion_api'),
    path('exportar/csv/', views_ml.exportar_csv, name='exportar_csv'),
    path('exportar/excel/', views_ml.exportar_excel, name='exportar_excel'),
    
    path('estudiante/<int:estudiante_id>/', views_ml.estudiante_detalle_ml, name='estudiante_detalle_ml'),
    path('estudiante/<int:estudiante_id>/excel/', views_ml.exportar_detalle_excel, name='exportar_detalle_excel'),

]