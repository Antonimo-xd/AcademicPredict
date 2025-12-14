"""
SCRIPT DE LIMPIEZA - VERSIÓN 2 (CORREGIDA)
==========================================
CORRECCIONES V2:
- Solucionado el renombrado de 'assignment_submissions' (typo en PDF original)
- Cambiado 'Año' por 'Anio' para evitar errores de codificación (Ã±)
- Mantiene formato europeo y lógica de limpieza anterior

Autor: Claude (Asistente Gemini)
Fecha: Noviembre 2025
"""
import sys
import io
import pandas as pd
import numpy as np
import warnings

# Configuración de codificación para consola
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

ARCHIVO_DATASET1 = 'dataset_2021_hash.csv'
ARCHIVO_DATASET2 = 'dataset_2022_hash.csv'

SALIDA_DATASET1 = 'dataset_2021_ultra_limpio.csv'
SALIDA_DATASET2 = 'dataset_2022_ultra_limpio.csv'

MAPEO_DATASET1 = 'mapeo_completo_2021.csv'
MAPEO_DATASET2 = 'mapeo_completo_2022.csv'

CHUNK_SIZE = 5000

# =============================================================================
# DICCIONARIO DE RENOMBRADO (CORREGIDO 'AÑO' -> 'ANIO')
# =============================================================================

RENOMBRADO_COLUMNAS = {
    'dni_hash': 'Id_Estudiante',
    'tit_hash': 'Id_Carrera',
    'asi_hash': 'Id_Asignatura',
    'campus_hash': 'Campus',
    'grupos_por_tipocredito_hash': 'Id_Grupo_Creditos',
    'caca': 'Anio_Academico',
    'anyo_ingreso': 'Anio_Ingreso_Universidad',
    'tipo_ingreso': 'Tipo_Acceso_Universidad',
    'nota10_hash': 'Nota_Selectividad_Base',
    'nota14_hash': 'Nota_Selectividad_Total',
    'preferencia_seleccion': 'Orden_Preferencia_Carrera',
    'estudios_p_hash': 'Nivel_Educativo_Padre',
    'estudios_m_hash': 'Nivel_Educativo_Madre',
    'dedicacion': 'Dedicacion_Estudios',
    'desplazado_hash': 'Estudiante_Desplazado',
    'abandono_hash': 'Estado_Abandono',
    'nota_asig_hash': 'Nota_Final_Asignatura',
    'fecha_datos': 'Fecha_Extraccion_Datos',
    'curso_mas_bajo': 'Anio_Carrera_Minimo',
    'curso_mas_alto': 'Anio_Carrera_Maximo',
    'matricula_activa': 'Matricula_Activa',
    'cred_mat1': 'Creditos_Matriculados_Anio_Carrera_1',
    'cred_mat2': 'Creditos_Matriculados_Anio_Carrera_2',
    'cred_mat3': 'Creditos_Matriculados_Anio_Carrera_3',
    'cred_mat4': 'Creditos_Matriculados_Anio_Carrera_4',
    'cred_mat5': 'Creditos_Matriculados_Anio_Carrera_5',
    'cred_mat6': 'Creditos_Matriculados_Anio_Carrera_6',
    'cred_sup_1o': 'Creditos_Aprobados_Anio_Carrera_1',
    'cred_sup_2o': 'Creditos_Aprobados_Anio_Carrera_2',
    'cred_sup_3o': 'Creditos_Aprobados_Anio_Carrera_3',
    'cred_sup_4o': 'Creditos_Aprobados_Anio_Carrera_4',
    'cred_sup_5o': 'Creditos_Aprobados_Anio_Carrera_5',
    'cred_sup_6o': 'Creditos_Aprobados_Anio_Carrera_6',
    'cred_sup_normal': 'Creditos_Aprobados_Examen',
    'cred_sup_espec': 'Creditos_Aprobados_Especiales',
    'cred_sup': 'Creditos_Aprobados_Total_Por_Metodo',
    'cred_mat_normal': 'Creditos_Matriculados_Oficiales',
    'cred_mat_movilidad': 'Creditos_Matriculados_Movilidad',
    'cred_ptes_acta': 'Creditos_Pendientes_Acta_Oficial',
    'cred_mat_practicas': 'Creditos_Matriculados_Practicas',
    'cred_mat_sem_a': 'Creditos_Matriculados_Semestre_1',
    'cred_mat_sem_b': 'Creditos_Matriculados_Semestre_2',
    'cred_mat_anu': 'Creditos_Matriculados_Anuales',
    'cred_mat_total': 'Creditos_Matriculados_Total_Anio',  
    'cred_sup_sem_a': 'Creditos_Aprobados_Semestre_1',
    'cred_sup_sem_b': 'Creditos_Aprobados_Semestre_2',
    'cred_sup_anu': 'Creditos_Aprobados_Anuales',
    'cred_sup_total': 'Creditos_Aprobados_Total_Por_Periodo',
    'cred_sup_tit': 'Creditos_Aprobados_Titulo_Global',
    'cred_pend_sup_tit': 'Creditos_Pendientes_Titulo_Global',
    'rendimiento_cuat_a': 'Rendimiento_Academico_Semestre_1',
    'rendimiento_cuat_b': 'Rendimiento_Academico_Semestre_2',
    'rendimiento_total': 'Rendimiento_Academico_Total_Anio', 
    'rend_total_ultimo': 'Rendimiento_Academico_Anio_Previo_1',
    'rend_total_penultimo': 'Rendimiento_Academico_Anio_Previo_2',
    'rend_total_antepenultimo': 'Rendimiento_Academico_Anio_Previo_3',
    'exento_npp': 'Cerca_De_Finalizacion_Carrera',
    'anyo_inicio_estudios': 'Anio_Inicio_Estudios',
    'es_retitulado': 'Es_Segunda_Titulacion',
    'es_adaptado': 'Es_Plan_Antiguo_Adaptado',
    'practicas': 'Creditos_Practicas_Empresa',
    'actividades': 'Creditos_Actividades_Extracurriculares',
    'ajuste': 'Creditos_Ajuste_Reconocimientos',
    'ajuste1': 'Creditos_Ajuste_Reconocimientos_Adicional',
    'impagado_curso_mat': 'Tiene_Impagos_Matricula',
    'asig1': 'Creditos_Asignaturas_Regulares',
    'pract1': 'Creditos_Practicas_Empresa_Adicional',
    'activ1': 'Creditos_Actividades_Extracurriculares_Adicional',
    'total1': 'Creditos_Total_Adicional',
}

PATRON_RENOMBRADO_DIGITAL = {
    'pft_events': 'Eventos_LMS',
    'pft_visits': 'Visitas_LMS',
    'pft_days_logged': 'Dias_Acceso_LMS',
    'pft_assigment_submissions': 'Tareas_Entregadas_LMS',    
    'pft_assignment_submissions': 'Tareas_Entregadas_LMS', 
    'pft_test_submissions': 'Examenes_Enviados_LMS',
    'pft_total_minutes': 'Minutos_Totales_LMS',
    'resource_events': 'Eventos_Recursos_LMS',
    'n_resource_days': 'Dias_Acceso_Recursos_LMS',
    'n_wifi_days': 'Dias_Acceso_Wifi_Campus',
}

# =============================================================================
# MAPEOS GLOBALES
# =============================================================================

mapeos_globales = {
    'Id_Estudiante': {},
    'Id_Carrera': {},
    'Id_Asignatura': {},
    'Campus': {},
    'Id_Grupo_Creditos': {},
}

MAPEO_ESTUDIOS = {
    'F': 'FormacionProfesional',
    'L': 'Licenciatura',
    'M': 'Master',
    'P': 'Primaria',
    'R': 'SinDatos',
    'T': 'TecnicoSuperior'
}

MAPEO_DESPLAZADO = {
    'A': 'Desplazado',
    'B': 'NoDesplazado'
}

MAPEO_ABANDONO = {
    'A': 'Abandono',
    'B': 'NoAbandono'
}

MAPEO_DEDICACION = {
    'TC': 'TiempoCompleto',
    'TP': 'TiempoParcial'
}

MAPEO_MATRICULA = {
    '1': 'Activo',
    '1,0': 'Activo',
    '1.0': 'Activo',
    '0': 'Inactivo',
    '0,0': 'Inactivo',
    '0.0': 'Inactivo',
    'NA': 'NoAplica'
}

MAPEO_TIPO_INGRESO = {
    'NAP': 'Selectividad',
    'NAI': 'AccesoInternacional',
    'NAE': 'AccesoExtranjero',
    'NAD': 'AccesoDirecto',
    'NRO': 'Reconocimiento',
    'NTE': 'TituloExtranjero',
    'NSC': 'SinCodificar',
    'NAC': 'AccesoCurso',
    'NLE': 'LicenciaEstudios',
    'ANT': 'Antiguo',
    'BMA': 'BachilleratoMayores',
    'NCF': 'CicloFormativo',
    'NUE': 'UnionEuropea',
    'NIE': 'Internacional',
    'NSA': 'SinAsignar',
    'ASA': 'AccesoSinAsignar',
    'NAS': 'AccesoSuperior',
    'NCA': 'Convalidacion'
}

# =============================================================================
# FUNCIONES
# =============================================================================

def crear_etiqueta_legible(columna, valor, contador):
    """Convierte hashes en etiquetas numéricas legibles"""
    prefijos = {
        'Id_Estudiante': 'Estudiante',
        'Id_Carrera': 'Carrera',
        'Id_Asignatura': 'Asignatura',
        'Campus': 'Campus',
        'Id_Grupo_Creditos': 'Grupo'
    }
    prefijo = prefijos.get(columna, 'ID')
    return f'{prefijo}_{contador}'


def transformar_hash_a_etiqueta(chunk, columna):
    if columna not in chunk.columns:
        return chunk
    try:
        serie_trabajando = chunk[columna].copy()
        for idx in chunk.index:
            valor = chunk.at[idx, columna]
            if pd.notna(valor) and str(valor).strip() != '' and str(valor) != '0.0':
                valor_str = str(valor).strip()
                if len(valor_str) > 5:
                    if valor_str not in mapeos_globales[columna]:
                        contador = len(mapeos_globales[columna]) + 1
                        etiqueta = crear_etiqueta_legible(columna, valor_str, contador)
                        mapeos_globales[columna][valor_str] = etiqueta
                    serie_trabajando.at[idx] = mapeos_globales[columna][valor_str]
        chunk[columna] = serie_trabajando
    except Exception as e:
        print(f"   Error transformando {columna}: {e}")
    return chunk


def transformar_valores_categoricos(chunk):
    # Diccionarios de mapeo para columnas específicas
    cols_map = {
        'Nivel_Educativo_Padre': MAPEO_ESTUDIOS,
        'Nivel_Educativo_Madre': MAPEO_ESTUDIOS,
        'Estudiante_Desplazado': MAPEO_DESPLAZADO,
        'Estado_Abandono': MAPEO_ABANDONO,
        'Dedicacion_Estudios': MAPEO_DEDICACION,
        'Tipo_Acceso_Universidad': MAPEO_TIPO_INGRESO,
        'Matricula_Activa': MAPEO_MATRICULA
    }

    for col, mapeo in cols_map.items():
        if col in chunk.columns:
            try:
                chunk[col] = chunk[col].astype(str).replace(mapeo)
            except Exception as e:
                print(f"   Error mapeando {col}: {e}")
    
    try:
        for col in chunk.select_dtypes(include='object').columns:
            chunk[col] = chunk[col].replace('nan', np.nan)
    except Exception as e:
        pass
    
    return chunk


def renombrar_columnas_digitales(chunk):
    """Renombra las columnas de actividad digital"""
    nuevos_nombres = {}
    
    for col in chunk.columns:
        nuevo_nombre = col
        
        # Iterar sobre el diccionario corregido que incluye 'assignment' y 'assigment'
        for patron_viejo, patron_nuevo in PATRON_RENOMBRADO_DIGITAL.items():
            if col.startswith(patron_viejo):
                partes = col.split('_')
                if len(partes) >= 3:
                    try:
                        # Detectar año y mes al final (ej: ..._2021_9)
                        year = partes[-2]
                        month = partes[-1]
                        
                        # Corrección crítica: asegurar mes con dos dígitos (09, not 9)
                        month = month.zfill(2)
                        
                        nuevo_nombre = f"{patron_nuevo}_{year}_{month}"
                        break
                    except:
                        pass
        
        nuevos_nombres[col] = nuevo_nombre
    
    chunk = chunk.rename(columns=nuevos_nombres)
    return chunk


def convertir_columnas_enteras(chunk):
    """Convierte binarios y contadores a enteros"""
    columnas_binarias = [
        'Cerca_De_Finalizacion_Carrera', 'Es_Segunda_Titulacion', 
        'Es_Plan_Antiguo_Adaptado', 'Tiene_Impagos_Matricula'
    ]
    
    for col in columnas_binarias:
        if col in chunk.columns:
            try:
                chunk[col] = chunk[col].astype(str)
                chunk[col] = chunk[col].replace({'nan': '0', 'NA': '0', 'NaN': '0'})
                chunk[col] = chunk[col].str.replace(',', '.').str.replace('.0', '')
                chunk[col] = pd.to_numeric(chunk[col], errors='coerce').fillna(0).astype(int)
            except:
                pass
    
    # Columnas digitales (incluyendo la nueva Tareas_Entregadas)
    for col in chunk.columns:
        patrones_enteros = [
            'Dias_Acceso_LMS', 'Examenes_Enviados_LMS', 'Eventos_Recursos_LMS', 
            'Dias_Acceso_Recursos_LMS', 'Dias_Acceso_Wifi_Campus', 'Eventos_LMS', 
            'Visitas_LMS', 'Tareas_Entregadas_LMS'
        ]
        if any(patron in col for patron in patrones_enteros):
            try:
                chunk[col] = chunk[col].astype(str).replace('nan', '0')
                chunk[col] = chunk[col].str.replace(',', '.').str.replace('.0', '')
                chunk[col] = pd.to_numeric(chunk[col], errors='coerce').fillna(0).astype(int)
            except:
                pass
    
    return chunk


def limpiar_y_transformar_chunk(chunk):
    try:
        # 1. Renombrar columnas principales
        chunk = chunk.rename(columns=RENOMBRADO_COLUMNAS)
        
        # 2. Renombrar columnas digitales (Aquí se arregla el pft_assignment)
        chunk = renombrar_columnas_digitales(chunk)
        
        # 3. Transformar hashes
        for col in ['Id_Estudiante', 'Id_Carrera', 'Id_Asignatura', 'Campus', 'Id_Grupo_Creditos']:
            if col in chunk.columns:
                chunk = transformar_hash_a_etiqueta(chunk, col)
        
        # 4. Transformar valores categóricos
        chunk = transformar_valores_categoricos(chunk)
        
        # 5. Convertir a enteros
        chunk = convertir_columnas_enteras(chunk)
        
        # 6. Convertir fechas
        for col in ['Fecha_Extraccion_Datos', 'baja_fecha']:
            if col in chunk.columns:
                chunk[col] = pd.to_datetime(chunk[col], errors='coerce')

        # 7. Rellenar créditos vacíos con 0
        columnas_creditos = [col for col in chunk.columns if 'Creditos' in col]
        for col in columnas_creditos:
            if col in chunk.columns:
                chunk[col] = chunk[col].fillna('0')
        
        return chunk
        
    except Exception as e:
        print(f"   Error procesando chunk: {e}")
        raise e


def procesar_dataset(archivo_entrada, archivo_salida, archivo_mapeo):
    print(f"\n{'='*70}")
    print(f"PROCESANDO V2: {archivo_entrada}")
    print(f"{'='*70}\n")
    
    chunks_procesados = []
    
    try:
        for i, chunk in enumerate(pd.read_csv(archivo_entrada, sep=';', encoding='utf-8',chunksize=CHUNK_SIZE, dtype=str), 1):
            print(f"Procesando chunk {i}...", end='\r')
            chunk_limpio = limpiar_y_transformar_chunk(chunk)
            chunks_procesados.append(chunk_limpio)
        
        print(f"\nConcatenando chunks...")
        dataset_completo = pd.concat(chunks_procesados, ignore_index=True)
        
        print(f"Guardando dataset...")
        dataset_completo.to_csv(archivo_salida, sep=';', index=False, encoding='utf-8', decimal=',', quoting=1)
        
        print(f"Generando mapeo...")
        generar_archivo_mapeo(archivo_mapeo)
        
        print(f"FINALIZADO: {archivo_salida} ({len(dataset_completo)} filas)")
        return True
        
    except FileNotFoundError:
        print(f"ERROR: No se encontró {archivo_entrada}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def generar_archivo_mapeo(archivo_salida):
    registros = []
    # Mapeos de hashes
    for columna, mapeo in mapeos_globales.items():
        for hash_orig, etiqueta in mapeo.items():
            registros.append({'columna': columna, 'tipo': 'Hash', 'original': hash_orig, 'nuevo': etiqueta})
    # Mapeos categóricos
    for col, mapa in {'Estudios': MAPEO_ESTUDIOS, 'Desplazado': MAPEO_DESPLAZADO, 'Abandono': MAPEO_ABANDONO, 'Ingreso': MAPEO_TIPO_INGRESO}.items():
        for orig, nuevo in mapa.items():
            registros.append({'columna': col, 'tipo': 'Cat', 'original': orig, 'nuevo': nuevo})
            
    pd.DataFrame(registros).to_csv(archivo_salida, sep=';', index=False, encoding='utf-8')


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("INICIANDO LIMPIEZA V2")
    
    exito1 = procesar_dataset(ARCHIVO_DATASET1, SALIDA_DATASET1, MAPEO_DATASET1)
    
    if exito1:
        # Reiniciar mapeos para el segundo archivo
        for key in mapeos_globales: mapeos_globales[key] = {}
        procesar_dataset(ARCHIVO_DATASET2, SALIDA_DATASET2, MAPEO_DATASET2)