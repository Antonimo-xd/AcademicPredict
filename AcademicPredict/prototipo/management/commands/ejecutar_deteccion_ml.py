from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from prototipo.models import (
    RegistroAcademicoUniversitario,
    PrediccionDesercionUniversitaria,
)
from prototipo.ml.predictor import PredictorML
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Ejecuta detección ML de deserción para todos los estudiantes'
    
    def add_arguments(self, parser):
        
        parser.add_argument(
            '--anio',
            type=int,
            default=None,
            help='Año académico específico (default: más reciente)'
        )
        
        parser.add_argument(
            '--test',
            action='store_true',
            help='Modo test: procesa solo 100 estudiantes'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar actualización de predicciones existentes'
        )
    
    def handle(self, *args, **options):
        """
        Método principal que ejecuta el comando.
        
        FLUJO:
        1. Inicializar predictor ML
        2. Obtener registros académicos
        3. Ejecutar predicciones
        4. Guardar en base de datos
        5. Reportar estadísticas
        """
        
        # =====================================================================
        # CONFIGURACIÓN
        # =====================================================================
        
        anio = options['anio']
        modo_test = options['test']
        force = options['force']
        
        # Encabezado
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("🤖 DETECCIÓN ML - PREDICCIÓN DE DESERCIÓN"))
        self.stdout.write("=" * 80)
        self.stdout.write("")
        
        # =====================================================================
        # PASO 1: INICIALIZAR PREDICTOR
        # =====================================================================
        
        self.stdout.write("📦 PASO 1: Inicializando Predictor ML...")
        
        try:
            predictor = PredictorML()
            predictor.cargar_modelos()
            self.stdout.write(self.style.SUCCESS("   ✅ Modelos cargados correctamente"))
        except Exception as e:
            raise CommandError(f"❌ Error cargando modelos: {e}")
        
        self.stdout.write("")
        
        # =====================================================================
        # PASO 2: OBTENER REGISTROS ACADÉMICOS
        # =====================================================================
        
        self.stdout.write("📊 PASO 2: Obteniendo registros académicos...")
        
        try:
            # Determinar año académico
            if anio is None:
                # Obtener año más reciente
                anio = RegistroAcademicoUniversitario.objects.latest(
                    'anio_academico'
                ).anio_academico
                self.stdout.write(f"   ℹ️  Año académico detectado: {anio}")
            else:
                self.stdout.write(f"   ℹ️  Año académico especificado: {anio}")
            
            # Obtener registros más recientes de cada estudiante
            registros = RegistroAcademicoUniversitario.objects.filter(
                anio_academico=anio
            ).select_related('estudiante').order_by('estudiante', '-anio_academico')
            
            # Eliminar duplicados (mantener solo el más reciente por estudiante)
            estudiantes_vistos = set()
            registros_unicos = []
            
            for reg in registros:
                if reg.estudiante_id not in estudiantes_vistos:
                    registros_unicos.append(reg)
                    estudiantes_vistos.add(reg.estudiante_id)
            
            registros = registros_unicos
            
            # Modo test: limitar a 100
            if modo_test:
                registros = registros[:100]
                self.stdout.write(self.style.WARNING(
                    f"   ⚠️  MODO TEST: Procesando solo {len(registros)} estudiantes"
                ))
            
            total_registros = len(registros)
            self.stdout.write(self.style.SUCCESS(
                f"   ✅ Registros obtenidos: {total_registros} estudiantes"
            ))
            
            if total_registros == 0:
                raise CommandError(
                    f"❌ No se encontraron registros para el año {anio}"
                )
                
        except RegistroAcademicoUniversitario.DoesNotExist:
            raise CommandError("❌ No hay registros académicos en la base de datos")
        except Exception as e:
            raise CommandError(f"❌ Error obteniendo registros: {e}")
        
        self.stdout.write("")
        
        # =====================================================================
        # PASO 3: EJECUTAR PREDICCIONES
        # =====================================================================
        
        self.stdout.write("🔮 PASO 3: Ejecutando predicciones ML...")
        self.stdout.write(f"   ⏱️  Esto puede tomar 2-5 minutos...")
        
        try:
            # Ejecutar predictor
            resultados = predictor.predecir_estudiantes(registros)
            
            self.stdout.write(self.style.SUCCESS(
                f"   ✅ Predicciones completadas: {len(resultados)} estudiantes"
            ))
            
            # Estadísticas
            stats = predictor.obtener_estadisticas(resultados)
            
            self.stdout.write("")
            self.stdout.write("   📊 DISTRIBUCIÓN DE RIESGO:")
            self.stdout.write(f"      🔴 Crítico: {stats['criticos']} ({stats['pct_criticos']:.1f}%)")
            self.stdout.write(f"      🟠 Alto: {stats['altos']} ({stats['pct_altos']:.1f}%)")
            self.stdout.write(f"      🟡 Medio: {stats['medios']} ({stats['pct_medios']:.1f}%)")
            self.stdout.write(f"      🟢 Bajo: {stats['bajos']} ({stats['pct_bajos']:.1f}%)")
            self.stdout.write(f"      ⚠️  Anomalías: {stats['anomalias']} ({stats['pct_anomalias']:.1f}%)")
            
        except Exception as e:
            raise CommandError(f"❌ Error ejecutando predicciones: {e}")
        
        self.stdout.write("")
        
        # =====================================================================
        # PASO 4: GUARDAR EN BASE DE DATOS
        # =====================================================================
        
        self.stdout.write("💾 PASO 4: Guardando predicciones en base de datos...")
        
        predicciones_creadas = 0
        predicciones_actualizadas = 0
        errores = 0
        
        try:
            # Usar transacción para consistencia
            with transaction.atomic():
                for resultado in resultados:
                    try:
                        # Verificar si ya existe predicción
                        prediccion_existente = PrediccionDesercionUniversitaria.objects.filter(
                            estudiante=resultado['estudiante']
                        ).first()

                        prediccion, created = PrediccionDesercionUniversitaria.objects.update_or_create(
                            estudiante=resultado['estudiante'],
                            defaults={
                                'registro_academico': resultado['registro'],
                                
                                # XGBoost
                                'probabilidad_desercion': resultado['probabilidad_desercion'],
                                'nivel_riesgo': resultado['nivel_riesgo'],
                                
                                # Isolation Forest
                                'es_anomalia': resultado['es_anomalia'],
                                'score_anomalia': resultado['score_anomalia'],
                                
                                # Regresión (rendimiento)
                                'rendimiento_predicho_futuro': resultado['rendimiento_predicho_futuro'],
                                
                                # Factores
                                'factores_riesgo': resultado['factores_riesgo'],
                                
                                # Metadatos
                                'modelo_usado': resultado['modelo_usado'],
                                'version_modelo': resultado['version_modelo'],
                                'fecha_prediccion': timezone.now()
                            }
                        )
                        
                        if created:
                            predicciones_creadas += 1
                        else:
                            predicciones_actualizadas += 1
                            
                    except Exception as e:
                        errores += 1
                        logger.error(
                            f"Error guardando predicción para estudiante "
                            f"{resultado['estudiante'].id}: {e}"
                        )
            
            self.stdout.write(self.style.SUCCESS(
                f"   ✅ Predicciones guardadas correctamente"
            ))
            self.stdout.write(f"      Creadas: {predicciones_creadas}")
            self.stdout.write(f"      Actualizadas: {predicciones_actualizadas}")
            
            if errores > 0:
                self.stdout.write(self.style.WARNING(
                    f"      ⚠️  Errores: {errores}"
                ))
                
        except Exception as e:
            raise CommandError(f"❌ Error guardando en BD: {e}")
        
        self.stdout.write("")
        
        # =====================================================================
        # PASO 5: RESUMEN FINAL
        # =====================================================================
        
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("✅ DETECCIÓN COMPLETADA EXITOSAMENTE"))
        self.stdout.write("=" * 80)
        self.stdout.write("")
        
        self.stdout.write("📊 RESUMEN FINAL:")
        self.stdout.write(f"   Total procesados: {len(resultados)}")
        self.stdout.write(f"   Año académico: {anio}")
        self.stdout.write(f"   Fecha: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.stdout.write("")
        
        self.stdout.write("🎯 ESTUDIANTES EN RIESGO:")
        estudiantes_riesgo = stats['criticos'] + stats['altos']
        self.stdout.write(self.style.ERROR(
            f"   ⚠️  {estudiantes_riesgo} estudiantes requieren atención "
            f"({(estudiantes_riesgo/stats['total']*100):.1f}%)"
        ))
        self.stdout.write("")
        
        self.stdout.write("💡 PRÓXIMOS PASOS:")
        self.stdout.write("   1. Revisar dashboard ML: python manage.py runserver → /ml/dashboard/")
        self.stdout.write("   2. Contactar estudiantes en riesgo crítico/alto")
        self.stdout.write("   3. Exportar reportes para coordinadores")
        self.stdout.write("")
        
        self.stdout.write("=" * 80)
        
        # Retornar estadísticas para tests
        return None  