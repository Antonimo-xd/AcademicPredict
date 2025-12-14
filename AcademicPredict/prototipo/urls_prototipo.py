from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import views_roles

urlpatterns = [
    
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', views.home, name='home'),
    path('home/', views.home, name='home_alias'),
    
    path('universidad/importar/', views.importar_datos_universidad, name='importar_datos_universidad'),
    
    path('dashboard/', views.dashboard_universidad, name='dashboard_universidad'),
    path('dashboard/filtrar/', views.dashboard_filtrado_ajax, name='dashboard_filtrado_ajax'),
    path('dashboard/avanzado/', views.dashboard_avanzado, name='dashboard_avanzado'),
    path('dashboard/avanzado/filtrar/', views.dashboard_avanzado_filtrado, name='dashboard_avanzado_filtrado'),

    path('asignar-analista/<int:estudiante_id>/', views_roles.asignar_analista, name='asignar_analista'),
    path('registrar-intervencion/<int:alerta_id>/', views_roles.registrar_intervencion, name='registrar_intervencion'),
    path('marcar-resuelta/<int:alerta_id>/', views_roles.marcar_resuelta, name='marcar_resuelta'),
    path('mis-casos/', views_roles.mis_casos_asignados, name='mis_casos_asignados'),

    path('sin-permiso/', views.sin_permiso, name='sin_permiso'),
]