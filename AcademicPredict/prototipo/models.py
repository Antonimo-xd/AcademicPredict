from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class CarreraUniversitaria(models.Model):
    codigo_carrera = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=300, blank=True)
    campus = models.CharField(max_length=50, help_text="Ubicación: Valencia, Gandía, Alcoy")
    
    creditos_totales_requeridos = models.DecimalField(max_digits=6, decimal_places=2, default=240.00)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.codigo_carrera} ({self.campus})"

class EstudianteUniversitario(models.Model):
    codigo_estudiante = models.CharField(max_length=50, unique=True)
    carrera = models.ForeignKey(CarreraUniversitaria, on_delete=models.CASCADE, related_name='estudiantes')
    
    anio_ingreso_universidad = models.IntegerField()
    anio_inicio_estudios = models.IntegerField()
    
    tipo_acceso_universidad = models.CharField(max_length=50) 
    
    nota_selectividad_base = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    nota_selectividad_total = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    orden_preferencia_carrera = models.IntegerField(null=True, blank=True)
    
    nivel_educativo_padre = models.CharField(max_length=50)
    nivel_educativo_madre = models.CharField(max_length=50)
    dedicacion_estudios = models.CharField(max_length=20, choices=[('TiempoCompleto', 'Tiempo Completo'), ('TiempoParcial', 'Tiempo Parcial')])
    es_desplazado = models.BooleanField(default=False)

    estado_abandono = models.CharField(max_length=20, help_text="Variable Objetivo: Abandono vs NoAbandono")
    
    es_segunda_titulacion = models.BooleanField(default=False)
    es_plan_antiguo_adaptado = models.BooleanField(default=False)
    cerca_de_finalizacion_carrera = models.BooleanField(default=False)
    tiene_impagos_matricula = models.BooleanField(default=False)
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.codigo_estudiante} - {self.estado_abandono}"

class AsignaturaUniversitaria(models.Model):
    codigo_asignatura = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=300, blank=True)
    carrera = models.ForeignKey(CarreraUniversitaria, on_delete=models.CASCADE)
    creditos = models.DecimalField(max_digits=5, decimal_places=2, default=6.00)
    
    anio_carrera = models.IntegerField(help_text="Año del plan de estudios (1-6)")
    
    def __str__(self):
        return self.codigo_asignatura

class RegistroAcademicoUniversitario(models.Model):
    estudiante = models.ForeignKey(EstudianteUniversitario, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(AsignaturaUniversitaria, on_delete=models.CASCADE)
    
    anio_academico = models.IntegerField()
    id_grupo_creditos = models.CharField(max_length=50, blank=True)
    matricula_activa = models.BooleanField(default=True)
    
    anio_carrera_minimo = models.IntegerField()
    anio_carrera_maximo = models.IntegerField()

    creditos_matriculados_anio_1 = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_matriculados_anio_2 = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_matriculados_anio_3 = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_matriculados_anio_4 = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_matriculados_anio_5 = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_matriculados_anio_6 = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    creditos_aprobados_anio_1 = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_aprobados_anio_2 = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_aprobados_anio_3 = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_aprobados_anio_4 = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_aprobados_anio_5 = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_aprobados_anio_6 = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    creditos_matriculados_oficiales = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_matriculados_movilidad = models.DecimalField(max_digits=6, decimal_places=2, default=0) 
    creditos_matriculados_practicas = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    creditos_aprobados_examen = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_aprobados_especiales = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    creditos_practicas_empresa = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    creditos_actividades_extracurriculares = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    creditos_ajuste_reconocimientos = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    creditos_matriculados_semestre_1 = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_matriculados_semestre_2 = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_matriculados_anuales = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    creditos_aprobados_semestre_1 = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_aprobados_semestre_2 = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_aprobados_anuales = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    creditos_matriculados_total_anio = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_aprobados_total_anio = models.DecimalField(max_digits=6, decimal_places=2, default=0) 

    creditos_aprobados_titulo_global = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_pendientes_titulo_global = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    creditos_pendientes_acta_oficial = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    rendimiento_semestre_1 = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rendimiento_semestre_2 = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    rendimiento_total_anio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    rendimiento_anio_previo_1 = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    rendimiento_anio_previo_2 = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    rendimiento_anio_previo_3 = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    
    nota_final_asignatura = models.DecimalField(max_digits=4, decimal_places=2, null=True)

    eventos_lms_total = models.IntegerField(default=0)
    visitas_lms_total = models.IntegerField(default=0)
    tareas_entregadas_total = models.IntegerField(default=0)
    examenes_enviados_total = models.IntegerField(default=0)
    tiempo_total_minutos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dias_wifi_total = models.IntegerField(default=0)
    
    eventos_recursos_total = models.IntegerField(default=0) 
    dias_recursos_total = models.IntegerField(default=0)    

    detalle_mensual_lms = models.JSONField(default=dict)
    
    class Meta:
        unique_together = ['estudiante', 'asignatura', 'anio_academico']

    def __str__(self):
        return f"{self.estudiante} - {self.anio_academico}"

    @property
    def tasa_aprobacion(self):
        if self.creditos_matriculados_total_anio > 0:
            return (float(self.creditos_aprobados_total_anio) / float(self.creditos_matriculados_total_anio)) * 100
        return 0.0
    
    @property
    def progreso_carrera(self):
        creditos_totales = self.estudiante.carrera.creditos_totales_requeridos
        if creditos_totales > 0:
            return (float(self.creditos_aprobados_titulo_global) / float(creditos_totales)) * 100
        return 0.0
    
    @property
    def promedio_actividad_lms_diaria(self):
        if self.visitas_lms_total > 0:
            return float(self.tiempo_total_minutos) / float(self.visitas_lms_total)
        return 0.0

class PrediccionDesercionUniversitaria(models.Model):
    estudiante = models.ForeignKey(EstudianteUniversitario,on_delete=models.CASCADE, related_name='predicciones_desercion')
    
    registro_academico = models.ForeignKey(RegistroAcademicoUniversitario, on_delete=models.CASCADE, related_name='predicciones', help_text="Registro académico usado para la predicción")
    
    # =================================================================
    # RESULTADOS DE ISOLATION FOREST
    # =================================================================

    es_anomalia = models.BooleanField(default=False, help_text="¿Se detectó como anomalía?")
    
    score_anomalia = models.FloatField(null=True, blank=True, help_text="Puntuación de anomalía (valores negativos = anomalía)")
    
    # =================================================================
    # RESULTADOS DE XGBOOST
    # =================================================================
    
    probabilidad_desercion = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], help_text="Probabilidad de deserción (0-1)")
    
    NIVEL_RIESGO_CHOICES = [
        ('Bajo', 'Riesgo Bajo (< 30%)'),
        ('Medio', 'Riesgo Medio (30-60%)'),
        ('Alto', 'Riesgo Alto (60-80%)'),
        ('Critico', 'Riesgo Crítico (> 80%)'),
    ]
    
    nivel_riesgo = models.CharField(max_length=10, choices=NIVEL_RIESGO_CHOICES, help_text="Nivel de riesgo calculado")
    
    # =================================================================
    # RESULTADOS DE REGRESIÓN LINEAL
    # =================================================================
    
    rendimiento_predicho_futuro = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)], help_text="Rendimiento académico predicho para el próximo período (%)")
    
    # =================================================================
    # FACTORES CONTRIBUYENTES
    # =================================================================
    
    factores_riesgo = models.JSONField(default=dict, help_text="Diccionario con factores que contribuyen al riesgo")

    fecha_prediccion = models.DateTimeField(auto_now_add=True)
    modelo_usado = models.CharField(max_length=50, default='XGBoost')
    version_modelo = models.CharField(max_length=20, default='1.0')
    
    class Meta:
        verbose_name = "Predicción de Deserción"
        verbose_name_plural = "Predicciones de Deserción"
        ordering = ['-fecha_prediccion']
    
    def __str__(self):
        return f"{self.estudiante.codigo_estudiante} - {self.get_nivel_riesgo_display()}"
    
    def get_riesgo_color(self):
        """Retorna un color para visualización según el riesgo"""
        colores = {
            'Bajo': 'success',
            'Medio': 'warning',
            'Alto': 'danger',
            'Critico': 'dark'
        }
        return colores.get(self.nivel_riesgo, 'secondary')

class AsignaturaCriticaUniversitaria(models.Model):
    asignatura = models.ForeignKey(AsignaturaUniversitaria, on_delete=models.CASCADE, related_name='analisis_criticos')
    
    anio_academico = models.IntegerField(validators=[MinValueValidator(2018), MaxValueValidator(2030)], help_text="Año académico analizado")
    
    total_estudiantes_matriculados = models.IntegerField(validators=[MinValueValidator(0)], help_text="Estudiantes que se matricularon")
    
    total_estudiantes_aprobados = models.IntegerField(validators=[MinValueValidator(0)], help_text="Estudiantes que aprobaron")
    
    total_estudiantes_reprobados = models.IntegerField(validators=[MinValueValidator(0)], help_text="Estudiantes que reprobaron")
    
    tasa_reprobacion = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)], help_text="Porcentaje de reprobación")
    
    nota_promedio = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(10)], help_text="Nota promedio de la asignatura")
    
    rendimiento_promedio = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], help_text="Rendimiento promedio de los estudiantes (%)")
    
    actividad_lms_promedio = models.FloatField(default=0, help_text="Promedio de minutos de uso del LMS")
    
    es_critica = models.BooleanField(default=False, help_text="¿Se considera asignatura crítica? (> 40% reprobación)")
    
    fecha_analisis = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Asignatura Crítica"
        verbose_name_plural = "Asignaturas Críticas"
        unique_together = ['asignatura', 'anio_academico']
        ordering = ['-tasa_reprobacion']
    
    def __str__(self):
        return f"{self.asignatura.codigo_asignatura} - {self.tasa_reprobacion:.1f}% reprobación"

class TrazabilidadPrediccionDesercion(models.Model):
    CLASIFICACIONES = [
        ('bajo', 'Riesgo Bajo'),
        ('medio', 'Riesgo Medio'),
        ('alto', 'Riesgo Alto'),
        ('critico', 'Riesgo Crítico'),
    ]
    
    estudiante = models.ForeignKey('EstudianteUniversitario', on_delete=models.CASCADE, related_name='predicciones', help_text='Estudiante al que pertenece esta predicción')
    
    fecha_prediccion = models.DateTimeField(default=timezone.now, help_text='Momento en que se generó la predicción')
    
    probabilidad_desercion = models.FloatField(help_text='Probabilidad de deserción (0.0 a 1.0)')
    
    indice_riesgo = models.FloatField(help_text='Índice de riesgo calculado (0 a 100)', db_index=True)
    
    clasificacion_riesgo = models.CharField(max_length=10, choices=CLASIFICACIONES, help_text='Clasificación del nivel de riesgo', db_index=True)
    
    factores_riesgo = models.JSONField(default=list, help_text='Lista de factores que contribuyen al riesgo', blank=True)
    
    importancia_factores = models.JSONField(default=dict, help_text='Importancia de cada factor (SHAP values)', blank=True)
    
    modelo_usado = models.CharField(max_length=100, default='XGBoost', help_text='Algoritmo ML utilizado')
    
    version_modelo = models.CharField(max_length=50, default='1.0', help_text='Versión del modelo ML' )
    
    accuracy_modelo = models.FloatField(null=True, blank=True, help_text='Precisión del modelo al momento de predicción')
    
    es_cambio_significativo = models.BooleanField(default=False, help_text='True si hubo cambio importante vs predicción anterior')
    
    cambio_clasificacion = models.CharField(max_length=50, blank=True, help_text='Descripción del cambio de clasificación')
    
    activa = models.BooleanField(default=True, help_text='True si es la predicción más reciente')
    
    class Meta:
        db_table = 'prediccion_desercion'
        verbose_name = 'Predicción de Deserción'
        verbose_name_plural = 'Predicciones de Deserción'
        ordering = ['-fecha_prediccion']
        indexes = [
            models.Index(fields=['estudiante', '-fecha_prediccion']),
            models.Index(fields=['clasificacion_riesgo', '-indice_riesgo']),
            models.Index(fields=['-fecha_prediccion']),
        ]
    
    def __str__(self):
        return f"{self.estudiante.codigo_estudiante} - {self.clasificacion_riesgo} ({self.indice_riesgo:.1f}%)"
    
    def save(self, *args, **kwargs):
        es_nueva = self.pk is None
        
        if es_nueva:
            prediccion_anterior = TrazabilidadPrediccionDesercion.objects.filter(
                estudiante=self.estudiante,
                activa=True
            ).first()
            
            if prediccion_anterior:
                cambio_indice = abs(self.indice_riesgo - prediccion_anterior.indice_riesgo)
                cambio_clasificacion = self.clasificacion_riesgo != prediccion_anterior.clasificacion_riesgo
                
                if cambio_indice >= 10 or cambio_clasificacion:
                    self.es_cambio_significativo = True
                    self.cambio_clasificacion = f"{prediccion_anterior.clasificacion_riesgo} → {self.clasificacion_riesgo}"
                
                prediccion_anterior.activa = False
                prediccion_anterior.save()
        
        super().save(*args, **kwargs)
        
        if es_nueva and (self.es_cambio_significativo or self.clasificacion_riesgo in ['alto', 'critico']):
            self.generar_alerta()
    
    def generar_alerta(self):
        if self.clasificacion_riesgo == 'critico':
            prioridad = 'critica'
        elif self.clasificacion_riesgo == 'alto':
            prioridad = 'alta'
        else:
            prioridad = 'media'
        
        if self.es_cambio_significativo:
            mensaje = f"Cambio significativo detectado: {self.cambio_clasificacion}. Índice de riesgo: {self.indice_riesgo:.1f}%"
        else:
            mensaje = f"Estudiante clasificado como {self.get_clasificacion_riesgo_display()}. Índice: {self.indice_riesgo:.1f}%"
        
        alerta = AlertaEstudiante.objects.create(
            estudiante=self.estudiante,
            prediccion=self,
            tipo_alerta='cambio_riesgo' if self.es_cambio_significativo else 'riesgo_alto',
            prioridad=prioridad,
            titulo=f"Alerta de Riesgo - {self.estudiante.codigo_estudiante}",
            mensaje=mensaje
        )
        
        return alerta
    
    def obtener_prediccion_anterior(self):
        return TrazabilidadPrediccionDesercion.objects.filter(
            estudiante=self.estudiante,
            fecha_prediccion__lt=self.fecha_prediccion
        ).first()
    
    def calcular_tendencia(self):
        anterior = self.obtener_prediccion_anterior()
        if not anterior:
            return 'nueva'
        
        diferencia = self.indice_riesgo - anterior.indice_riesgo
        
        if diferencia < -5:
            return 'mejorando'
        elif diferencia > 5:
            return 'empeorando'
        else:
            return 'estable'

class AlertaEstudiante(models.Model):
    TIPOS_ALERTA = [
        ('cambio_riesgo', 'Cambio de Clasificación'),
        ('riesgo_alto', 'Riesgo Alto Detectado'),
        ('inactividad', 'Inactividad Prolongada'),
        ('bajo_rendimiento', 'Bajo Rendimiento Académico'),
        ('ausentismo', 'Ausentismo Elevado'),
        ('manual', 'Alerta Manual'),
    ]
    
    PRIORIDADES = [
        ('critica', 'Crítica'),
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]
    
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_revision', 'En Revisión'),
        ('resuelta', 'Resuelta'),
        ('descartada', 'Descartada'),
    ]
    
    estudiante = models.ForeignKey('EstudianteUniversitario', on_delete=models.CASCADE, related_name='alertas', help_text='Estudiante que generó la alerta')
    
    prediccion = models.ForeignKey(TrazabilidadPrediccionDesercion, on_delete=models.SET_NULL, null=True, blank=True, related_name='alertas', help_text='Predicción que originó la alerta')
    
    tutor_asignado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='alertas_asignadas', help_text='Tutor responsable de atender la alerta')
    
    tipo_alerta = models.CharField(max_length=20, choices=TIPOS_ALERTA, help_text='Tipo de alerta')
    
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media', help_text='Nivel de prioridad', db_index=True)
    
    estado = models.CharField(max_length=15, choices=ESTADOS, default='pendiente', help_text='Estado actual de la alerta', db_index=True)
    
    titulo = models.CharField(max_length=200, help_text='Título descriptivo de la alerta')
    
    mensaje = models.TextField(help_text='Descripción detallada de la alerta')
    
    fecha_creacion = models.DateTimeField(default=timezone.now, help_text='Momento en que se creó la alerta')
    
    fecha_revision = models.DateTimeField(null=True, blank=True, help_text='Momento en que se empezó a revisar')
    
    fecha_resolucion = models.DateTimeField(null=True, blank=True, help_text='Momento en que se resolvió')
    
    acciones_tomadas = models.TextField(blank=True, help_text='Descripción de las acciones realizadas')
    
    notificacion_enviada = models.BooleanField(default=False, help_text='True si se envió notificación por email')
    
    fecha_notificacion = models.DateTimeField(null=True, blank=True, help_text='Momento en que se envió la notificación')
    
    email_destinatarios = models.JSONField(default=list, blank=True, help_text='Lista de emails que recibieron notificación')
    
    visible = models.BooleanField(default=True, help_text='True si la alerta debe mostrarse')
    
    class Meta:
        db_table = 'alerta_estudiante'
        verbose_name = 'Alerta de Estudiante'
        verbose_name_plural = 'Alertas de Estudiantes'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['estado', 'prioridad', '-fecha_creacion']),
            models.Index(fields=['estudiante', '-fecha_creacion']),
            models.Index(fields=['-fecha_creacion']),
        ]
    
    def __str__(self):
        return f"{self.get_prioridad_display()} - {self.estudiante.codigo_estudiante} - {self.titulo}"
    
    def save(self, *args, **kwargs):
        es_nueva = self.pk is None
        
        super().save(*args, **kwargs)
        
        # Enviar notificación si es una alerta nueva y crítica/alta
        if es_nueva and self.prioridad in ['critica', 'alta'] and not self.notificacion_enviada:
            self.enviar_notificacion_email()
    
    def enviar_notificacion_email(self):
        try:
            destinatarios = []
            
            if self.tutor_asignado and self.tutor_asignado.email:
                destinatarios.append(self.tutor_asignado.email)
            
            coordinadores = User.objects.filter(
                is_staff=True,
                email__isnull=False
            ).exclude(email='')
            destinatarios.extend(coordinadores.values_list('email', flat=True))
            
            if not destinatarios:
                return False
            
            asunto = f"[{self.get_prioridad_display()}] {self.titulo}"
            
            mensaje_html = f"""
            <h2>Alerta de Estudiante en Riesgo</h2>
            
            <p><strong>Prioridad:</strong> {self.get_prioridad_display()}</p>
            <p><strong>Estudiante:</strong> {self.estudiante.codigo_estudiante}</p>
            <p><strong>Carrera:</strong> {self.estudiante.carrera.nombre_carrera if self.estudiante.carrera else 'N/A'}</p>
            
            <h3>Detalles de la Alerta</h3>
            <p>{self.mensaje}</p>
            
            {f"<p><strong>Índice de Riesgo:</strong> {self.prediccion.indice_riesgo:.1f}%</p>" if self.prediccion else ""}
            {f"<p><strong>Clasificación:</strong> {self.prediccion.get_clasificacion_riesgo_display()}</p>" if self.prediccion else ""}
            
            <p><strong>Fecha de Creación:</strong> {self.fecha_creacion.strftime('%d/%m/%Y %H:%M')}</p>
            
            <p>Por favor, revisa esta alerta en el dashboard del sistema.</p>
            
            <hr>
            <p><small>AcademicPredict - Sistema de Predicción de Deserción Universitaria</small></p>
            """
            
            send_mail(
                subject=asunto,
                message=self.mensaje, 
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=list(set(destinatarios)),
                html_message=mensaje_html,
                fail_silently=False,
            )
            
            self.notificacion_enviada = True
            self.fecha_notificacion = timezone.now()
            self.email_destinatarios = list(set(destinatarios))
            self.save(update_fields=['notificacion_enviada', 'fecha_notificacion', 'email_destinatarios'])
            
            return True
            
        except Exception as e:
            print(f"Error enviando notificación: {e}")
            return False
    
    def marcar_en_revision(self, tutor=None):
        self.estado = 'en_revision'
        self.fecha_revision = timezone.now()
        if tutor:
            self.tutor_asignado = tutor
        self.save()
    
    def resolver(self, acciones=''):
        self.estado = 'resuelta'
        self.fecha_resolucion = timezone.now()
        if acciones:
            self.acciones_tomadas = acciones
        self.save()
    
    def descartar(self, razon=''):
        self.estado = 'descartada'
        self.fecha_resolucion = timezone.now()
        if razon:
            self.acciones_tomadas = f"Descartada: {razon}"
        self.save()
    
    @property
    def dias_pendiente(self):
        if self.estado == 'pendiente':
            return (timezone.now() - self.fecha_creacion).days
        elif self.fecha_revision:
            return (self.fecha_revision - self.fecha_creacion).days
        return 0

class IntervencionEstudiante(models.Model):
    TIPOS_INTERVENCION = [
        ('tutoria', 'Tutoría Académica'),
        ('psicologica', 'Apoyo Psicológico'),
        ('vocacional', 'Orientación Vocacional'),
        ('financiera', 'Asesoría Financiera'),
        ('seguimiento', 'Seguimiento General'),
        ('reunion', 'Reunión con Estudiante'),
        ('contacto_familia', 'Contacto con Familia'),
        ('derivacion', 'Derivación a Especialista'),
        ('otro', 'Otro'),
    ]
    
    RESULTADOS = [
        ('exitosa', 'Exitosa'),
        ('parcial', 'Parcialmente Exitosa'),
        ('sin_efecto', 'Sin Efecto'),
        ('pendiente', 'Pendiente de Evaluar'),
    ]

    estudiante = models.ForeignKey('EstudianteUniversitario',on_delete=models.CASCADE, related_name='intervenciones', help_text='Estudiante que recibió la intervención')

    alerta_relacionada = models.ForeignKey(AlertaEstudiante, on_delete=models.SET_NULL, null=True, blank=True, related_name='intervenciones', help_text='Alerta que motivó esta intervención')

    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='intervenciones_realizadas', help_text='Usuario que realizó o registró la intervención')

    tipo_intervencion = models.CharField(max_length=20, choices=TIPOS_INTERVENCION, help_text='Tipo de intervención realizada')

    fecha_intervencion = models.DateTimeField(default=timezone.now, help_text='Fecha y hora de la intervención')

    titulo = models.CharField(max_length=200, help_text='Título o resumen de la intervención')

    descripcion = models.TextField(help_text='Descripción detallada de la intervención')

    resultado = models.CharField(max_length=15, choices=RESULTADOS, default='pendiente', help_text='Resultado de la intervención')

    observaciones = models.TextField(blank=True, help_text='Observaciones adicionales o seguimiento')

    requiere_seguimiento = models.BooleanField(default=False, help_text='True si requiere intervención de seguimiento')

    fecha_seguimiento = models.DateField(null=True, blank=True, help_text='Fecha programada para seguimiento')

    archivo_adjunto = models.FileField(upload_to='intervenciones/%Y/%m/',null=True, blank=True, help_text='Documento o archivo relacionado')

    fecha_registro = models.DateTimeField(auto_now_add=True, help_text='Momento en que se registró en el sistema')

    fecha_actualizacion = models.DateTimeField(auto_now=True, help_text='Última actualización del registro')

    class Meta:
        db_table = 'intervencion_estudiante'
        verbose_name = 'Intervención de Estudiante'
        verbose_name_plural = 'Intervenciones de Estudiantes'
        ordering = ['-fecha_intervencion']
        indexes = [
            models.Index(fields=['estudiante', '-fecha_intervencion']),
            models.Index(fields=['tipo_intervencion', '-fecha_intervencion']),
            models.Index(fields=['-fecha_intervencion']),
        ]

    def __str__(self):
        return f"{self.get_tipo_intervencion_display()} - {self.estudiante.codigo_estudiante} - {self.fecha_intervencion.strftime('%d/%m/%Y')}"

    def marcar_como_completada(self, resultado, observaciones=''):
        """Marca la intervención como completada con un resultado."""
        self.resultado = resultado
        if observaciones:
            self.observaciones = observaciones
        self.save()

class FichaSeguimientoEstudiante(models.Model):
    estudiante = models.OneToOneField('EstudianteUniversitario', on_delete=models.CASCADE, primary_key=True, related_name='ficha_seguimiento', help_text='Estudiante al que pertenece esta ficha')

    en_seguimiento = models.BooleanField(default=False, help_text='True si el estudiante está en seguimiento activo')

    fecha_inicio_seguimiento = models.DateField(null=True, blank=True, help_text='Fecha en que comenzó el seguimiento')

    ultimo_indice_riesgo = models.FloatField(null=True, blank=True, help_text='Último índice de riesgo calculado')

    ultima_clasificacion = models.CharField(max_length=10, choices=TrazabilidadPrediccionDesercion.CLASIFICACIONES, null=True, blank=True, help_text='Última clasificación de riesgo')

    fecha_ultima_prediccion = models.DateTimeField(null=True, blank=True, help_text='Fecha de la última predicción')

    total_alertas = models.IntegerField(default=0, help_text='Total de alertas generadas')

    alertas_activas = models.IntegerField(default=0, help_text='Alertas pendientes o en revisión')
    
    total_intervenciones = models.IntegerField(default=0, help_text='Total de intervenciones realizadas')

    intervenciones_exitosas = models.IntegerField(default=0, help_text='Intervenciones con resultado exitoso')

    tutor_principal = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True, related_name='estudiantes_tutorados', help_text='Tutor principal asignado')

    notas_generales = models.TextField(blank=True, help_text='Notas generales sobre el seguimiento del estudiante')

    ultima_fecha_contacto = models.DateField(null=True, blank=True, help_text='Última vez que se contactó al estudiante')

    proxima_fecha_contacto = models.DateField(null=True, blank=True, help_text='Próxima fecha programada de contacto')

    fecha_creacion = models.DateTimeField(auto_now_add=True, help_text='Momento en que se creó la ficha')

    fecha_actualizacion = models.DateTimeField(auto_now=True, help_text='Última actualización de la ficha')

    class Meta:
        db_table = 'ficha_seguimiento_estudiante'
        verbose_name = 'Ficha de Seguimiento'
        verbose_name_plural = 'Fichas de Seguimiento'

    def __str__(self):
        return f"Ficha: {self.estudiante.codigo_estudiante}"
    
    def actualizar_contadores(self):
        """Actualiza los contadores de alertas e intervenciones."""
        self.total_alertas = self.estudiante.alertas.count()
        self.alertas_activas = self.estudiante.alertas.filter(
            estado__in=['pendiente', 'en_revision']
        ).count()
        self.total_intervenciones = self.estudiante.intervenciones.count()
        self.intervenciones_exitosas = self.estudiante.intervenciones.filter(
            resultado='exitosa'
        ).count()
        self.save()
    
    def actualizar_desde_prediccion(self, prediccion):
        """Actualiza la ficha con información de una nueva predicción."""
        self.ultimo_indice_riesgo = prediccion.indice_riesgo
        self.ultima_clasificacion = prediccion.clasificacion_riesgo
        self.fecha_ultima_prediccion = prediccion.fecha_prediccion
        
        if prediccion.clasificacion_riesgo in ['alto', 'critico']:
            if not self.en_seguimiento:
                self.en_seguimiento = True
                self.fecha_inicio_seguimiento = timezone.now().date()
        
        self.save()
    
    def obtener_evolucion_riesgo(self, dias=30):
        fecha_limite = timezone.now() - timezone.timedelta(days=dias)
        return TrazabilidadPrediccionDesercion.objects.filter(
            estudiante=self.estudiante,
            fecha_prediccion__gte=fecha_limite
        ).order_by('fecha_prediccion')

# ============================================================================
# SIGNALS PARA MANTENER SINCRONIZACIÓN
# ============================================================================

@receiver(post_save, sender=TrazabilidadPrediccionDesercion)
def actualizar_ficha_desde_prediccion(sender, instance, created, **kwargs):
    """Actualiza la ficha de seguimiento cuando hay nueva predicción."""
    ficha, created = FichaSeguimientoEstudiante.objects.get_or_create(
        estudiante=instance.estudiante
    )
    ficha.actualizar_desde_prediccion(instance)


@receiver(post_save, sender=AlertaEstudiante)
def actualizar_contadores_alerta(sender, instance, created, **kwargs):
    """Actualiza contadores cuando se crea o modifica una alerta."""
    if hasattr(instance.estudiante, 'ficha_seguimiento'):
        instance.estudiante.ficha_seguimiento.actualizar_contadores()

@receiver(post_save, sender=IntervencionEstudiante)
def actualizar_contadores_intervencion(sender, instance, created, **kwargs):
    """Actualiza contadores cuando se crea o modifica una intervención."""
    if hasattr(instance.estudiante, 'ficha_seguimiento'):
        instance.estudiante.ficha_seguimiento.actualizar_contadores()

def generar_reporte_estudiante(estudiante):
    ficha = getattr(estudiante, 'ficha_seguimiento', None)
    
    reporte = {
        'estudiante': {
            'codigo': estudiante.codigo_estudiante,
            'carrera': str(estudiante.carrera) if estudiante.carrera else 'N/A',
            'estado_abandono': estudiante.estado_abandono,
        },
        'riesgo_actual': {
            'indice': ficha.ultimo_indice_riesgo if ficha else None,
            'clasificacion': ficha.ultima_clasificacion if ficha else None,
            'fecha': ficha.fecha_ultima_prediccion if ficha else None,
        },
        'seguimiento': {
            'en_seguimiento': ficha.en_seguimiento if ficha else False,
            'tutor': str(ficha.tutor_principal) if ficha and ficha.tutor_principal else 'Sin asignar',
            'alertas_activas': ficha.alertas_activas if ficha else 0,
            'total_intervenciones': ficha.total_intervenciones if ficha else 0,
        },
        'historial': {
            'predicciones': estudiante.predicciones.count(),
            'alertas': estudiante.alertas.count(),
            'intervenciones': estudiante.intervenciones.count(),
        }
    }
    
    return reporte

class PerfilUsuario(models.Model):
    """Perfil simple que extiende User con un rol."""
    ROLES = [
        ('admin', 'Administrador'),
        ('coordinador', 'Coordinador General'),
        ('coordinador_carrera', 'Coordinador de Carrera'),
        ('analista', 'Analista'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=30, choices=ROLES, default='analista')
    carrera_asignada = models.ForeignKey(
        'CarreraUniversitaria',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Solo para coordinadores de carrera"
    )
    
    

    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"

# Signal para crear perfil automáticamente
@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)



