import joblib  
import pandas as pd
from pathlib import Path
from django.conf import settings
import logging
import warnings

from prototipo.models import (
    TrazabilidadPrediccionDesercion,
    AlertaEstudiante,
    FichaSeguimientoEstudiante
)

from django.utils import timezone

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class PredictorML:
    """Predictor ML con carga usando joblib (compatible con modelos entrenados)"""
    
    def __init__(self):
        """Inicializa el predictor"""
        self.xgboost_model = None
        self.isolation_forest_model = None
        self.logistic_model = None
        self.scaler = None
        
        # Features que usa el modelo (IMPORTANTE: mismo orden que entrenamiento)
        self.feature_names = [
            'anio_academico',
            'anio_carrera_minimo',
            'anio_carrera_maximo',
            'eventos_lms_total',
            'visitas_lms_total',
            'tareas_entregadas_total',
            'examenes_enviados_total',
            'dias_wifi_total',
            'eventos_recursos_total',
            'dias_recursos_total',
        ]
        
        self.modelos_dir = Path(settings.BASE_DIR) / 'modelos_ml'
        logger.info("🤖 PredictorML inicializado")
    
    def cargar_modelos(self):
        """Carga modelos usando joblib"""
        
        try:
            logger.info("📦 Cargando modelos ML con joblib...")
            
            # 1. XGBoost (modelo principal)
            xgboost_path = self.modelos_dir / 'xgboost_model_SIN_LEAKAGE.pkl'
            if not xgboost_path.exists():
                raise FileNotFoundError(f"❌ No encontrado: {xgboost_path}")

            self.xgboost_model = joblib.load(xgboost_path)
            logger.info("✅ XGBoost cargado")
            
            # 2. Isolation Forest (detección anomalías)
            isolation_path = self.modelos_dir / 'isolation_forest_model_SIN_LEAKAGE.pkl'
            if not isolation_path.exists():
                raise FileNotFoundError(f"❌ No encontrado: {isolation_path}")
            
            self.isolation_forest_model = joblib.load(isolation_path)
            logger.info("✅ Isolation Forest cargado")
            
            # 3. Regresión Logística (baseline interpretable)
            logistic_path = self.modelos_dir / 'logistic_regression_model_SIN_LEAKAGE.pkl'
            if not logistic_path.exists():
                raise FileNotFoundError(f"❌ No encontrado: {logistic_path}")
            
            self.logistic_model = joblib.load(logistic_path)
            logger.info("✅ Regresión Logística cargada")
            
            # 4. Scaler (normalización)
            scaler_path = self.modelos_dir / 'standard_scaler_SIN_LEAKAGE.pkl'
            if not scaler_path.exists():
                raise FileNotFoundError(f"❌ No encontrado: {scaler_path}")
            
            self.scaler = joblib.load(scaler_path)
            logger.info("✅ Scaler cargado")
            
            logger.info("🎉 Todos los modelos cargados exitosamente con joblib")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando modelos: {e}")
            raise
    
    def preparar_features(self, registros):
        """Convierte registros Django QuerySet a DataFrame con features"""
        logger.info(f"🔧 Preparando features para {len(registros)} registros...")
        
        data = []
        for reg in registros:
            data.append({
                'anio_academico': reg.anio_academico or 0,
                'anio_carrera_minimo': reg.anio_carrera_minimo or 0,
                'anio_carrera_maximo': reg.anio_carrera_maximo or 0,
                'eventos_lms_total': reg.eventos_lms_total or 0,
                'visitas_lms_total': reg.visitas_lms_total or 0,
                'tareas_entregadas_total': reg.tareas_entregadas_total or 0,
                'examenes_enviados_total': reg.examenes_enviados_total or 0,
                'dias_wifi_total': reg.dias_wifi_total or 0,
                'eventos_recursos_total': reg.eventos_recursos_total or 0,
                'dias_recursos_total': reg.dias_recursos_total or 0,
            })
        
        df = pd.DataFrame(data)
        
        # Asegurar orden correcto de columnas
        df = df[self.feature_names]
        
        logger.info(f"✅ Features preparadas: {df.shape}")
        return df
    
    def predecir_xgboost(self, X):
        """Predice probabilidades con XGBoost"""

        if self.xgboost_model is None:
            raise Exception("❌ Modelo XGBoost no cargado")
        
        # Normalizar features (igual que en entrenamiento)
        X_scaled = self.scaler.transform(X)
        
        # Predecir probabilidades
        probabilidades = self.xgboost_model.predict_proba(X_scaled)[:, 1]
        
        return probabilidades
    
    def predecir_isolation_forest(self, X):
        """Predice anomalías con Isolation Forest"""

        if self.isolation_forest_model is None:
            raise Exception("❌ Modelo Isolation Forest no cargado")
        
        X_scaled = self.scaler.transform(X)
        
        # Predecir anomalías
        predicciones = self.isolation_forest_model.predict(X_scaled)
        
        # Obtener scores de anomalía
        scores = self.isolation_forest_model.score_samples(X_scaled)
        
        return predicciones, scores
    
    def predecir_regresion_logistica(self, X):
        """Predice probabilidades con Regresión Logística"""

        if self.logistic_model is None:
            raise Exception("❌ Modelo de Regresión Logística no cargado")
        
        X_scaled = self.scaler.transform(X)
        probabilidades = self.logistic_model.predict_proba(X_scaled)[:, 1]
        
        return probabilidades
    
    def calcular_nivel_riesgo(self, probabilidad):

        prob_pct = probabilidad * 100
        
        if prob_pct >= 97: 
            return 'Critico'
        elif prob_pct >= 95: 
            return 'Alto'
        elif prob_pct >= 75:  
            return 'Medio'
        else: 
            return 'Bajo'
    
    def identificar_factores_riesgo(self, estudiante_data):
        """Identifica factores de riesgo específicos del estudiante"""

        factores = []
        
        # Factor 1: Asistencia a campus (WiFi)
        if estudiante_data['dias_wifi_total'] < 15:
            factores.append({
                'factor': 'Baja presencia en campus',
                'descripcion': f"Solo {estudiante_data['dias_wifi_total']} días de asistencia",
                'valor_actual': estudiante_data['dias_wifi_total'],
                'valor_esperado': '≥ 15 días',
                'impacto': 'ALTO',
                'peso': 14.34,
                'recomendacion': 'Incentivar asistencia presencial'
            })
        
        # Factor 2: Tareas entregadas
        if estudiante_data['tareas_entregadas_total'] < 6:
            factores.append({
                'factor': 'Bajo compromiso con tareas',
                'descripcion': f"Solo {estudiante_data['tareas_entregadas_total']} tareas entregadas",
                'valor_actual': estudiante_data['tareas_entregadas_total'],
                'valor_esperado': '≥ 6 tareas',
                'impacto': 'ALTO',
                'peso': 13.63,
                'recomendacion': 'Seguimiento de entregas'
            })
        
        # Factor 3: Exámenes enviados
        if estudiante_data['examenes_enviados_total'] < 3:
            factores.append({
                'factor': 'Baja participación en evaluaciones',
                'descripcion': f"Solo {estudiante_data['examenes_enviados_total']} exámenes",
                'valor_actual': estudiante_data['examenes_enviados_total'],
                'valor_esperado': '≥ 3 exámenes',
                'impacto': 'ALTO',
                'peso': 14.24,
                'recomendacion': 'Verificar problemas para rendir exámenes'
            })
        
        # Factor 4: Actividad en LMS
        if estudiante_data['visitas_lms_total'] < 50:
            factores.append({
                'factor': 'Baja actividad en LMS',
                'descripcion': f"Solo {estudiante_data['visitas_lms_total']} visitas",
                'valor_actual': estudiante_data['visitas_lms_total'],
                'valor_esperado': '≥ 50 visitas',
                'impacto': 'MEDIO',
                'peso': 6.89,
                'recomendacion': 'Capacitación en uso de LMS'
            })
        
        # Factor 5: Uso de recursos
        if estudiante_data['dias_recursos_total'] < 8:
            factores.append({
                'factor': 'Bajo uso de recursos',
                'descripcion': f"Solo {estudiante_data['dias_recursos_total']} días",
                'valor_actual': estudiante_data['dias_recursos_total'],
                'valor_esperado': '≥ 8 días',
                'impacto': 'MEDIO',
                'peso': 10.19,
                'recomendacion': 'Promover recursos disponibles'
            })
        
        # Factor 6: Año avanzado
        if estudiante_data['anio_carrera_maximo'] >= 4:
            factores.append({
                'factor': 'Estudiante en año avanzado',
                'descripcion': f"Año {estudiante_data['anio_carrera_maximo']}",
                'valor_actual': estudiante_data['anio_carrera_maximo'],
                'valor_esperado': 'Completar carrera',
                'impacto': 'MEDIO',
                'peso': 16.03,
                'recomendacion': 'Apoyo para requisitos finales'
            })
        
        # Ordenar por impacto (ALTO primero)
        orden_impacto = {'ALTO': 0, 'MEDIO': 1, 'BAJO': 2}
        factores.sort(key=lambda x: orden_impacto[x['impacto']])
        
        return factores
    
    def predecir_estudiantes(self, registros):
        """Método principal: Predice riesgo para lista de estudiantes"""
        
        logger.info(f"🚀 Iniciando predicción para {len(registros)} estudiantes...")
        
        # Verificar que modelos estén cargados
        if self.xgboost_model is None:
            logger.warning("⚠️ Modelos no cargados, cargando ahora...")
            self.cargar_modelos()
        
        # 1. Preparar features
        X = self.preparar_features(registros)
        
        # 2. Ejecutar modelos
        logger.info("🔮 Ejecutando XGBoost...")
        probs_xgboost = self.predecir_xgboost(X)
        
        logger.info("🌲 Ejecutando Isolation Forest...")
        anomalias, scores_anomalia = self.predecir_isolation_forest(X)
        
        logger.info("📊 Ejecutando Regresión Logística...")
        probs_logistic = self.predecir_regresion_logistica(X)
        
        # 3. Combinar resultados
        resultados = []
        
        for i, registro in enumerate(registros):
            # Probabilidad de XGBoost (modelo principal)
            prob_xgb = float(probs_xgboost[i])
            
            # Nivel de riesgo
            nivel = self.calcular_nivel_riesgo(prob_xgb)
            
            # Factores de riesgo
            estudiante_data = X.iloc[i].to_dict()
            factores = self.identificar_factores_riesgo(estudiante_data)
            
            # Anomalía
            es_anomalia = anomalias[i] == -1
            score_anom = float(scores_anomalia[i])
            
            # Rendimiento predicho futuro
            rendimiento_predicho = (1 - prob_xgb) * 100
            
            resultado = {
                'registro': registro,
                'estudiante': registro.estudiante,
                'probabilidad_desercion': prob_xgb,
                'nivel_riesgo': nivel,
                'es_anomalia': es_anomalia,
                'score_anomalia': score_anom,
                'rendimiento_predicho_futuro': rendimiento_predicho,
                'factores_riesgo': factores,
                'modelo_usado': 'XGBoost_v1',
                'version_modelo': '1.0'
            }
            
            resultados.append(resultado)
        
        logger.info(f"✅ Predicciones completadas: {len(resultados)} estudiantes")
        return resultados
    
    def obtener_estadisticas(self, resultados):
        """Calcula estadísticas agregadas de las predicciones"""
        total = len(resultados)
        
        if total == 0:
            return {
                'total': 0,
                'criticos': 0,
                'altos': 0,
                'medios': 0,
                'bajos': 0,
                'anomalias': 0
            }
        
        niveles = [r['nivel_riesgo'] for r in resultados]
        anomalias = sum(1 for r in resultados if r['es_anomalia'])
        
        return {
            'total': total,
            'criticos': niveles.count('Critico'),
            'altos': niveles.count('Alto'),
            'medios': niveles.count('Medio'),
            'bajos': niveles.count('Bajo'),
            'anomalias': anomalias,
            'pct_criticos': (niveles.count('Critico') / total) * 100,
            'pct_altos': (niveles.count('Alto') / total) * 100,
            'pct_medios': (niveles.count('Medio') / total) * 100,
            'pct_bajos': (niveles.count('Bajo') / total) * 100,
            'pct_anomalias': (anomalias / total) * 100,
        }


# Funciones auxiliares para vistas Django

def obtener_color_nivel_riesgo(nivel):
    """Retorna color Bootstrap para badges"""
    colores = {
        'Critico': 'danger',
        'Alto': 'warning',
        'Medio': 'info',
        'Bajo': 'success',
    }
    return colores.get(nivel, 'secondary')


def obtener_recomendaciones_accion(nivel):
    """Retorna acciones recomendadas según nivel de riesgo"""
    recomendaciones = {
        'Critico': [
            '🚨 URGENTE: Reunión con tutor en 24 horas',
            '📞 Contactar inmediatamente',
            '👥 Notificar coordinador',
            '💼 Apoyo académico personalizado',
            '🎯 Asignar tutor par',
            '📊 Revisar historial completo'
        ],
        'Alto': [
            '📧 Contactar en 48 horas',
            '📚 Derivar a tutorías',
            '🔍 Seguimiento semanal',
            '📝 Revisar asignaturas críticas',
            '🤝 Apoyo psicopedagógico'
        ],
        'Medio': [
            '📅 Seguimiento quincenal',
            '📨 Email con recursos',
            '📖 Promover biblioteca',
            '👀 Monitorear LMS'
        ],
        'Bajo': [
            '✅ Monitoreo mensual',
            '🎉 Reconocer buen desempeño',
            '📢 Invitar a actividades'
        ]
    }
    
    return recomendaciones.get(nivel, [])

def generar_alertas_desde_ml(estudiante, resultado_ml):
    """Genera alertas automáticas DESPUÉS de ejecutar ML.
    Se llama desde el dashboard ML al finalizar predicciones."""
    
    # 1. Crear TRAZABILIDAD de predicción (registro histórico)
    prediccion = TrazabilidadPrediccionDesercion.objects.create(
        estudiante=estudiante,
        probabilidad_desercion=resultado_ml['probabilidad'],
        indice_riesgo=resultado_ml['indice_riesgo'],
        clasificacion_riesgo=resultado_ml['clasificacion'],
        factores_riesgo=resultado_ml.get('factores_riesgo', []),
        modelo_usado='XGBoost',
        version_modelo='1.0',
        activa=True
    )
    
    alerta = None
    
    # 2. Si es riesgo alto o crítico → GENERAR ALERTA
    if resultado_ml['clasificacion'] in ['alto', 'critico']:
        prioridad = 'critica' if resultado_ml['clasificacion'] == 'critico' else 'alta'
        
        alerta = AlertaEstudiante.objects.create(
            estudiante=estudiante,
            prediccion=prediccion,
            tipo_alerta='riesgo_alto',
            prioridad=prioridad,
            titulo=f"Estudiante en Riesgo {resultado_ml['clasificacion'].title()}",
            mensaje=f"El modelo ML detectó índice de riesgo de {resultado_ml['indice_riesgo']:.1f}%",
            indice_riesgo_momento=resultado_ml['indice_riesgo'],
            estado='pendiente'
        )
        
        # 3. Actualizar/crear ficha de seguimiento
        ficha, created = FichaSeguimientoEstudiante.objects.get_or_create(
            estudiante=estudiante
        )
        ficha.en_seguimiento = True
        ficha.ultimo_indice_riesgo = resultado_ml['indice_riesgo']
        ficha.ultima_clasificacion = resultado_ml['clasificacion']
        ficha.ultima_fecha_prediccion = timezone.now()
        ficha.alertas_activas = estudiante.alertas.filter(
            estado__in=['pendiente', 'en_revision'],
            visible=True
        ).count()
        ficha.save()
        
        print(f"✅ Alerta generada para {estudiante.codigo_estudiante} - {prioridad.upper()}")
    
    return {
        'prediccion': prediccion,
        'alerta': alerta
    }