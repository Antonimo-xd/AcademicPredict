import pandas as pd
import logging
from decimal import Decimal, InvalidOperation
from django.db import transaction
from prototipo.models import (
    CarreraUniversitaria,
    EstudianteUniversitario,
    AsignaturaUniversitaria,
    RegistroAcademicoUniversitario
)

logger = logging.getLogger(__name__)

class ImportadorDatosUniversitarios:
    """Importador Sincronizado con models.py y views.py."""
    
    def __init__(self, ruta_csv):
        self.ruta_csv = ruta_csv
        self.estadisticas = {
            'carreras_creadas': 0,
            'estudiantes_creados': 0,
            'asignaturas_creadas': 0,
            'registros_creados': 0,
            'registros_actualizados': 0,
            'errores': []
        }
        self.cache_carreras = {}
        self.cache_estudiantes = {}
        self.cache_asignaturas = {}
    
    def limpiar_decimal(self, valor):
        if pd.isna(valor) or valor == '': return Decimal('0.00')
        try:
            return Decimal(str(valor).replace(',', '.'))
        except:
            return Decimal('0.00')
    
    def limpiar_entero(self, valor):
        if pd.isna(valor) or valor == '': return 0
        try:
            return int(float(str(valor).replace(',', '.')))
        except:
            return 0
    
    def extraer_datos_lms(self, row):
        """
        Extrae y suma los datos mensuales del LMS.
        Formato columna: [Accion]_LMS_[Año]_[Mes]
        """
        datos_mensuales = {}
        
        totales = {
            'eventos': 0, 'visitas': 0, 'tareas': 0, 
            'examenes': 0, 'minutos': 0.0, 'wifi': 0,
            'eventos_recursos': 0, 'dias_recursos': 0 
        }
        
        meses = [
            '2021_09', '2021_10', '2021_11', '2021_12',
            '2022_01', '2022_02', '2022_03', '2022_04', 
            '2022_05', '2022_06', '2022_07', '2022_08'
        ]

        for mes in meses:
            key_eventos = f'Eventos_LMS_{mes}'
            key_visitas = f'Visitas_LMS_{mes}'
            key_tareas  = f'Tareas_Entregadas_LMS_{mes}'
            key_examenes= f'Examenes_Enviados_LMS_{mes}'
            key_minutos = f'Minutos_Totales_LMS_{mes}'
            key_wifi    = f'Dias_Acceso_Wifi_Campus_{mes}'
            key_rec_evt = f'Eventos_Recursos_LMS_{mes}'
            key_rec_dia = f'Dias_Acceso_Recursos_LMS_{mes}'

            if key_eventos in row:
                info_mes = {
                    'eventos': self.limpiar_entero(row.get(key_eventos)),
                    'visitas': self.limpiar_entero(row.get(key_visitas)),
                    'tareas': self.limpiar_entero(row.get(key_tareas)),
                    'examenes': self.limpiar_entero(row.get(key_examenes)),
                    'minutos': float(self.limpiar_decimal(row.get(key_minutos))),
                    'wifi_dias': self.limpiar_entero(row.get(key_wifi)),
                    'eventos_recursos': self.limpiar_entero(row.get(key_rec_evt)),
                    'dias_recursos': self.limpiar_entero(row.get(key_rec_dia))
                }
                
                datos_mensuales[mes] = info_mes
                
                # Sumar a totales
                totales['eventos'] += info_mes['eventos']
                totales['visitas'] += info_mes['visitas']
                totales['tareas'] += info_mes['tareas']
                totales['examenes'] += info_mes['examenes']
                totales['minutos'] += info_mes['minutos']
                totales['wifi'] += info_mes['wifi_dias']
                totales['eventos_recursos'] += info_mes['eventos_recursos']
                totales['dias_recursos'] += info_mes['dias_recursos']

        return datos_mensuales, totales

    @transaction.atomic
    def importar_completo(self):
        print(f"🚀 Iniciando importación de: {self.ruta_csv}")
        
        df = pd.read_csv(self.ruta_csv, sep=';', encoding='utf-8', dtype=str)
        total = len(df)
        
        print(f"📊 Filas detectadas: {total}")

        for index, row in df.iterrows():
            if index % 100 == 0: print(f"   Procesando fila {index}/{total}...", end='\r')
            
            try:
                # 1. CARRERA
                id_carrera = row['Id_Carrera']
                if id_carrera not in self.cache_carreras:
                    carrera, created = CarreraUniversitaria.objects.get_or_create(
                        codigo_carrera=id_carrera,
                        defaults={
                            'campus': row.get('Campus', 'Desconocido'),
                            'nombre': f"Carrera {id_carrera}"
                        }
                    )
                    self.cache_carreras[id_carrera] = carrera
                    if created: self.estadisticas['carreras_creadas'] += 1 
                carrera_obj = self.cache_carreras[id_carrera]

                # 2. ESTUDIANTE
                id_est = row['Id_Estudiante']
                if id_est not in self.cache_estudiantes:
                    es_desplazado = row.get('Estudiante_Desplazado') in ['Desplazado', 'Si', '1', 'True']
                    segunda_tit = str(row.get('Es_Segunda_Titulacion')) == '1'
                    plan_antiguo = str(row.get('Es_Plan_Antiguo_Adaptado')) == '1'
                    cerca_fin = str(row.get('Cerca_De_Finalizacion_Carrera')) == '1'
                    impagos = str(row.get('Tiene_Impagos_Matricula')) == '1'

                    estudiante, created = EstudianteUniversitario.objects.update_or_create(
                        codigo_estudiante=id_est,
                        defaults={
                            'carrera': carrera_obj,
                            'anio_ingreso_universidad': self.limpiar_entero(row['Anio_Ingreso_Universidad']),
                            'anio_inicio_estudios': self.limpiar_entero(row['Anio_Inicio_Estudios']),
                            'tipo_acceso_universidad': row['Tipo_Acceso_Universidad'],
                            'nota_selectividad_base': self.limpiar_decimal(row['Nota_Selectividad_Base']),
                            'nota_selectividad_total': self.limpiar_decimal(row['Nota_Selectividad_Total']),
                            'orden_preferencia_carrera': self.limpiar_entero(row['Orden_Preferencia_Carrera']),
                            'nivel_educativo_padre': row['Nivel_Educativo_Padre'],
                            'nivel_educativo_madre': row['Nivel_Educativo_Madre'],
                            'dedicacion_estudios': row['Dedicacion_Estudios'],
                            'es_desplazado': es_desplazado,
                            'estado_abandono': row['Estado_Abandono'],
                            'es_segunda_titulacion': segunda_tit,
                            'es_plan_antiguo_adaptado': plan_antiguo,
                            'cerca_de_finalizacion_carrera': cerca_fin,
                            'tiene_impagos_matricula': impagos
                        }
                    )
                    self.cache_estudiantes[id_est] = estudiante
                    if created: self.estadisticas['estudiantes_creados'] += 1 
                est_obj = self.cache_estudiantes[id_est]

                # 3. ASIGNATURA
                id_asig = row['Id_Asignatura']
                if id_asig not in self.cache_asignaturas:
                    asignatura, created = AsignaturaUniversitaria.objects.get_or_create(
                        codigo_asignatura=id_asig,
                        defaults={
                            'carrera': carrera_obj,
                            'anio_carrera': self.limpiar_entero(row.get('Anio_Carrera_Minimo', 1))
                        }
                    )
                    self.cache_asignaturas[id_asig] = asignatura
                    if created: self.estadisticas['asignaturas_creadas'] += 1 
                asig_obj = self.cache_asignaturas[id_asig]

                # 4. REGISTRO ACADÉMICO Y LMS
                lms_mensual, lms_totales = self.extraer_datos_lms(row)
                
                registro, created = RegistroAcademicoUniversitario.objects.update_or_create(
                    estudiante=est_obj,
                    asignatura=asig_obj,
                    anio_academico=self.limpiar_entero(row['Anio_Academico']),
                    defaults={
                        'id_grupo_creditos': row.get('Id_Grupo_Creditos', ''),
                        'matricula_activa': row.get('Matricula_Activa') in ['Activo', 'Si', '1', 'True'],
                        'anio_carrera_minimo': self.limpiar_entero(row['Anio_Carrera_Minimo']),
                        'anio_carrera_maximo': self.limpiar_entero(row['Anio_Carrera_Maximo']),
                        
                        # Créditos
                        'creditos_matriculados_anio_1': self.limpiar_decimal(row['Creditos_Matriculados_Anio_Carrera_1']),
                        'creditos_matriculados_anio_2': self.limpiar_decimal(row['Creditos_Matriculados_Anio_Carrera_2']),
                        'creditos_matriculados_anio_3': self.limpiar_decimal(row['Creditos_Matriculados_Anio_Carrera_3']),
                        'creditos_matriculados_anio_4': self.limpiar_decimal(row['Creditos_Matriculados_Anio_Carrera_4']),
                        'creditos_matriculados_anio_5': self.limpiar_decimal(row['Creditos_Matriculados_Anio_Carrera_5']),
                        'creditos_matriculados_anio_6': self.limpiar_decimal(row['Creditos_Matriculados_Anio_Carrera_6']),
                        
                        'creditos_aprobados_anio_1': self.limpiar_decimal(row['Creditos_Aprobados_Anio_Carrera_1']),
                        'creditos_aprobados_anio_2': self.limpiar_decimal(row['Creditos_Aprobados_Anio_Carrera_2']),
                        'creditos_aprobados_anio_3': self.limpiar_decimal(row['Creditos_Aprobados_Anio_Carrera_3']),
                        'creditos_aprobados_anio_4': self.limpiar_decimal(row['Creditos_Aprobados_Anio_Carrera_4']),
                        'creditos_aprobados_anio_5': self.limpiar_decimal(row['Creditos_Aprobados_Anio_Carrera_5']),
                        'creditos_aprobados_anio_6': self.limpiar_decimal(row['Creditos_Aprobados_Anio_Carrera_6']),

                        'creditos_aprobados_examen': self.limpiar_decimal(row['Creditos_Aprobados_Examen']),
                        'creditos_aprobados_especiales': self.limpiar_decimal(row['Creditos_Aprobados_Especiales']),
                        
                        'creditos_matriculados_semestre_1': self.limpiar_decimal(row['Creditos_Matriculados_Semestre_1']),
                        'creditos_matriculados_semestre_2': self.limpiar_decimal(row['Creditos_Matriculados_Semestre_2']),
                        'creditos_matriculados_anuales': self.limpiar_decimal(row['Creditos_Matriculados_Anuales']),
                        
                        'creditos_aprobados_semestre_1': self.limpiar_decimal(row['Creditos_Aprobados_Semestre_1']),
                        'creditos_aprobados_semestre_2': self.limpiar_decimal(row['Creditos_Aprobados_Semestre_2']),
                        'creditos_aprobados_anuales': self.limpiar_decimal(row['Creditos_Aprobados_Anuales']),
                        
                        'creditos_matriculados_total_anio': self.limpiar_decimal(row['Creditos_Matriculados_Total_Anio']),
                        'creditos_aprobados_total_anio': self.limpiar_decimal(row['Creditos_Aprobados_Total_Por_Periodo']),
                        'creditos_aprobados_titulo_global': self.limpiar_decimal(row['Creditos_Aprobados_Titulo_Global']),
                        'creditos_pendientes_titulo_global': self.limpiar_decimal(row['Creditos_Pendientes_Titulo_Global']),
                        'creditos_pendientes_acta_oficial': self.limpiar_decimal(row['Creditos_Pendientes_Acta_Oficial']),
                        
                        'creditos_matriculados_oficiales': self.limpiar_decimal(row.get('Creditos_Matriculados_Oficiales')),
                        'creditos_matriculados_movilidad': self.limpiar_decimal(row.get('Creditos_Matriculados_Movilidad')),
                        'creditos_matriculados_practicas': self.limpiar_decimal(row.get('Creditos_Matriculados_Practicas')),

                        'creditos_practicas_empresa': self.limpiar_decimal(row.get('Creditos_Practicas_Empresa')),
                        'creditos_actividades_extracurriculares': self.limpiar_decimal(row.get('Creditos_Actividades_Extracurriculares')),
                        'creditos_ajuste_reconocimientos': self.limpiar_decimal(row.get('Creditos_Ajuste_Reconocimientos')),

                        # Rendimientos
                        'rendimiento_semestre_1': self.limpiar_decimal(row['Rendimiento_Academico_Semestre_1']),
                        'rendimiento_semestre_2': self.limpiar_decimal(row['Rendimiento_Academico_Semestre_2']),
                        'rendimiento_total_anio': self.limpiar_decimal(row['Rendimiento_Academico_Total_Anio']),
                        'rendimiento_anio_previo_1': self.limpiar_decimal(row['Rendimiento_Academico_Anio_Previo_1']),
                        'rendimiento_anio_previo_2': self.limpiar_decimal(row['Rendimiento_Academico_Anio_Previo_2']),
                        'rendimiento_anio_previo_3': self.limpiar_decimal(row['Rendimiento_Academico_Anio_Previo_3']),
                        
                        'nota_final_asignatura': self.limpiar_decimal(row['Nota_Final_Asignatura']),
                        
                        # LMS Totales
                        'eventos_lms_total': lms_totales['eventos'],
                        'visitas_lms_total': lms_totales['visitas'],
                        'tareas_entregadas_total': lms_totales['tareas'],
                        'examenes_enviados_total': lms_totales['examenes'],
                        'tiempo_total_minutos': Decimal(str(lms_totales['minutos'])),
                        'dias_wifi_total': lms_totales['wifi'],
                        'detalle_mensual_lms': lms_mensual,

                        # Totales LMS calculados 
                        'eventos_recursos_total': lms_totales['eventos_recursos'],
                        'dias_recursos_total': lms_totales['dias_recursos'],
                    }
                )
                
                if created:
                    self.estadisticas['registros_creados'] += 1
                else:
                    self.estadisticas['registros_actualizados'] += 1

            except Exception as e:
                self.estadisticas['errores'].append(f"Fila {index}: {str(e)}")

        print(f"\n✅ Importación finalizada.")
        return self.estadisticas

    def generar_reporte(self): 
        return f"Importación completada. Creados: {self.estadisticas['registros_creados']}. Errores: {len(self.estadisticas['errores'])}"






