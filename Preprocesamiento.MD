# 🔧 Preprocesamiento del Dataset - AcademicPredict

---

## 📝 **Descripción General**

El script `limpiar_dataset_DEFINITIVO.py` es una herramienta crítica que transforma el dataset crudo de MDPI en un formato limpio, legible y listo para importar en AcademicPredict.

**Autor:** Desarrollado por el equipo AcademicPredict  
**Versión:** 2.0 (Corregida)  
**Ubicación:** `scripts/limpiar_dataset_DEFINITIVO.py`

---

## 🎯 **¿Qué Hace el Script?**

### **Transformaciones Principales:**

| Transformación | Antes | Después |
|---------------|-------|---------|
| **Hashes** | `dni_hash: a8f3e2d9c1b4...` | `Id_Estudiante: Estudiante_1` |
| **Columnas** | `caca` | `Anio_Academico` |
| **Categóricos** | `abandono_hash: A` | `Estado_Abandono: Abandono` |
| **LMS** | `pft_events_2021_9` | `Eventos_LMS_2021_09` |
| **Decimales** | `14,5` | `14.5` (interno) |
| **Separador** | `;` | `;` (mantenido) |

---

## 📊 **Estadísticas de Transformación**

### **114 Columnas Renombradas:**

```
ANTES (ejemplo):          →  DESPUÉS:
dni_hash                  →  Id_Estudiante
tit_hash                  →  Id_Carrera
caca                      →  Anio_Academico
estudios_p_hash           →  Nivel_Educativo_Padre
pft_events_2021_9         →  Eventos_LMS_2021_09
```

### **5 Categorías de Variables:**

1. **Identificadores** (5): Estudiante, Carrera, Asignatura, Campus, Grupo
2. **Demográficas** (10): Nivel educativo, dedicación, desplazamiento
3. **Académicas** (40): Créditos matriculados/aprobados, notas, rendimiento
4. **LMS** (30): Eventos, visitas, días activos, tareas
5. **Target** (1): Estado de abandono

---

## 🚀 **Uso del Script**

### **Requisitos Previos:**

```python
# Librerías necesarias
pip install pandas numpy
```

### **Estructura de Archivos:**

```
proyecto/
├── scripts/
│   └── limpiar_dataset_DEFINITIVO.py
├── data/
│   ├── raw/                          # Datasets crudos aquí
│   │   ├── dataset_2021_hash.csv
│   │   └── dataset_2022_hash.csv
│   └── processed/                    # Datasets limpios aquí (generados)
│       ├── dataset_2021_ultra_limpio.csv
│       ├── dataset_2022_ultra_limpio.csv
│       ├── mapeo_completo_2021.csv
│       └── mapeo_completo_2022.csv
```

### **Ejecución:**

```bash
# 1. Navegar a la carpeta del script
cd scripts/

# 2. Ejecutar
python limpiar_dataset_DEFINITIVO.py
```

### **Salida Esperada:**

```
INICIANDO LIMPIEZA V2

======================================================================
PROCESANDO V2: dataset_2021_hash.csv
======================================================================

Procesando chunk 30...
Concatenando chunks...
Guardando dataset...
Generando mapeo...
FINALIZADO: dataset_2021_ultra_limpio.csv (152847 filas)

======================================================================
PROCESANDO V2: dataset_2022_hash.csv
======================================================================

Procesando chunk 25...
Concatenando chunks...
Guardando dataset...
Generando mapeo...
FINALIZADO: dataset_2022_ultra_limpio.csv (145623 filas)
```

---

## 🔍 **Transformaciones Detalladas**

### **1. Conversión de Hashes → Etiquetas Legibles**

**Problema:** El dataset original usa hashes largos para proteger privacidad.

**Ejemplo:**
```
dni_hash: "a8f3e2d9c1b4567890abcdef1234567890abcdef"
```

**Solución:** Mapeo automático a etiquetas numéricas incrementales.

```python
def crear_etiqueta_legible(columna, valor, contador):
    prefijos = {
        'Id_Estudiante': 'Estudiante',
        'Id_Carrera': 'Carrera',
        'Id_Asignatura': 'Asignatura',
        'Campus': 'Campus',
        'Id_Grupo_Creditos': 'Grupo'
    }
    prefijo = prefijos.get(columna, 'ID')
    return f'{prefijo}_{contador}'
```

**Resultado:**
```
Id_Estudiante: "Estudiante_1"
Id_Estudiante: "Estudiante_2"
...
Id_Carrera: "Carrera_1"
Id_Asignatura: "Asignatura_1"
```

**Beneficios:**
- ✅ Mantiene privacidad (no revela identidades)
- ✅ Legible para humanos
- ✅ Relaciones preservadas (mismo hash → mismo ID)
- ✅ Archivo de mapeo generado para trazabilidad

---

### **2. Renombrado de Columnas**

**Problema:** Nombres de columnas crípticos del dataset original.

#### **Ejemplos de Renombrado:**

| Original | Nuevo | Categoría |
|----------|-------|-----------|
| `caca` | `Anio_Academico` | Temporal |
| `anyo_ingreso` | `Anio_Ingreso_Universidad` | Ingreso |
| `nota10_hash` | `Nota_Selectividad_Base` | Académico |
| `estudios_p_hash` | `Nivel_Educativo_Padre` | Socioeconómico |
| `cred_mat1` | `Creditos_Matriculados_Anio_Carrera_1` | Créditos |
| `pft_events` | `Eventos_LMS` | Digital |

**Total:** 114 columnas renombradas

---

### **3. Transformación de Valores Categóricos**

#### **A. Nivel Educativo (Padre/Madre):**

```python
MAPEO_ESTUDIOS = {
    'F': 'FormacionProfesional',
    'L': 'Licenciatura',
    'M': 'Master',
    'P': 'Primaria',
    'R': 'SinDatos',
    'T': 'TecnicoSuperior'
}
```

**Antes:** `estudios_p_hash: "L"`  
**Después:** `Nivel_Educativo_Padre: "Licenciatura"`

#### **B. Estado de Abandono:**

```python
MAPEO_ABANDONO = {
    'A': 'Abandono',
    'B': 'NoAbandono'
}
```

**Antes:** `abandono_hash: "A"`  
**Después:** `Estado_Abandono: "Abandono"`

#### **C. Tipo de Acceso:**

```python
MAPEO_TIPO_INGRESO = {
    'NAP': 'Selectividad',
    'NAI': 'AccesoInternacional',
    'NAE': 'AccesoExtranjero',
    'NAD': 'AccesoDirecto',
    'NRO': 'Reconocimiento',
    # ... 14 tipos en total
}
```

#### **D. Dedicación de Estudios:**

```python
MAPEO_DEDICACION = {
    'TC': 'TiempoCompleto',
    'TP': 'TiempoParcial'
}
```

#### **E. Estudiante Desplazado:**

```python
MAPEO_DESPLAZADO = {
    'A': 'Desplazado',
    'B': 'NoDesplazado'
}
```

---

### **4. Renombrado de Columnas LMS (Digitales)**

**Problema:** Columnas de actividad digital con formato inconsistente.

**Patrón Original:**
```
pft_events_2021_9          # Eventos en septiembre 2021
pft_visits_2021_10         # Visitas en octubre 2021
pft_assigment_submissions_2021_11  # Tareas (typo en original)
pft_assignment_submissions_2021_12 # Tareas (correcto)
```

**Transformación Aplicada:**

```python
PATRON_RENOMBRADO_DIGITAL = {
    'pft_events': 'Eventos_LMS',
    'pft_visits': 'Visitas_LMS',
    'pft_days_logged': 'Dias_Acceso_LMS',
    'pft_assigment_submissions': 'Tareas_Entregadas_LMS',    # Typo corregido
    'pft_assignment_submissions': 'Tareas_Entregadas_LMS',   # Correcto
    'pft_test_submissions': 'Examenes_Enviados_LMS',
    'pft_total_minutes': 'Minutos_Totales_LMS',
    'resource_events': 'Eventos_Recursos_LMS',
    'n_resource_days': 'Dias_Acceso_Recursos_LMS',
    'n_wifi_days': 'Dias_Acceso_Wifi_Campus',
}
```

**Resultado:**
```
Eventos_LMS_2021_09
Visitas_LMS_2021_10
Tareas_Entregadas_LMS_2021_11
Tareas_Entregadas_LMS_2021_12  # Ambas versiones del typo → mismo nombre
```

**Corrección Crítica:** Mes con dos dígitos (`09` en vez de `9`)

---

### **5. Conversión de Tipos de Datos**

#### **A. Columnas Binarias → Enteros:**

```python
columnas_binarias = [
    'Cerca_De_Finalizacion_Carrera',    # 0 o 1
    'Es_Segunda_Titulacion',             # 0 o 1
    'Es_Plan_Antiguo_Adaptado',          # 0 o 1
    'Tiene_Impagos_Matricula'            # 0 o 1
]
```

**Antes:** `"1,0"`, `"0.0"`, `"NA"`, `"nan"`  
**Después:** `1`, `0`, `0`, `0`

#### **B. Columnas LMS → Enteros:**

```python
patrones_enteros = [
    'Dias_Acceso_LMS',           # Días (entero)
    'Examenes_Enviados_LMS',     # Cantidad (entero)
    'Eventos_LMS',               # Contador (entero)
    'Visitas_LMS',               # Contador (entero)
    'Tareas_Entregadas_LMS'      # Cantidad (entero)
]
```

#### **C. Fechas → DateTime:**

```python
columnas_fecha = ['Fecha_Extraccion_Datos', 'baja_fecha']
```

**Formato:** ISO 8601 (`YYYY-MM-DD`)

#### **D. Créditos → Rellenar con 0:**

```python
# Todas las columnas que contengan "Creditos"
# NaN → "0"
```

---

### **6. Formato de Salida (Europeo)**

**Importante:** El archivo de salida mantiene el formato europeo para compatibilidad con el importador de Django.

```python
dataset_completo.to_csv(
    archivo_salida, 
    sep=';',          # Separador: punto y coma
    decimal=',',      # Decimal: coma
    encoding='utf-8',
    quoting=1         # Comillas para strings
)
```

**Ejemplo de registro:**

```csv
Id_Estudiante;Id_Carrera;Anio_Academico;Nota_Selectividad_Base;Estado_Abandono
Estudiante_1;Carrera_1;2021;14,5;NoAbandono
Estudiante_2;Carrera_2;2021;12,3;Abandono
```

---

## 📋 **Archivo de Mapeo Generado**

El script genera automáticamente un archivo CSV con todos los mapeos aplicados.

**Estructura:**

| columna | tipo | original | nuevo |
|---------|------|----------|-------|
| Id_Estudiante | Hash | a8f3e2d9c1b4... | Estudiante_1 |
| Id_Carrera | Hash | b9g4f3e0d2c5... | Carrera_1 |
| Estudios | Cat | L | Licenciatura |
| Abandono | Cat | A | Abandono |

**Uso del mapeo:**
- ✅ Trazabilidad completa
- ✅ Reversión si es necesaria
- ✅ Documentación de transformaciones
- ✅ Auditoría de datos

---

## ⚙️ **Configuración del Script**

### **Parámetros Editables:**

```python
# Archivos de entrada
ARCHIVO_DATASET1 = 'dataset_2021_hash.csv'
ARCHIVO_DATASET2 = 'dataset_2022_hash.csv'

# Archivos de salida
SALIDA_DATASET1 = 'dataset_2021_ultra_limpio.csv'
SALIDA_DATASET2 = 'dataset_2022_ultra_limpio.csv'

# Archivos de mapeo
MAPEO_DATASET1 = 'mapeo_completo_2021.csv'
MAPEO_DATASET2 = 'mapeo_completo_2022.csv'

# Tamaño de chunks para procesar archivos grandes
CHUNK_SIZE = 5000  # Filas por chunk
```

### **Modificar para Otros Datasets:**

Si tienes otros archivos o nombres diferentes:

```python
# Ejemplo: Un solo archivo
ARCHIVO_DATASET1 = 'mi_dataset.csv'
SALIDA_DATASET1 = 'mi_dataset_limpio.csv'
MAPEO_DATASET1 = 'mapeo_mi_dataset.csv'

# En main, comentar el segundo dataset:
if __name__ == "__main__":
    print("INICIANDO LIMPIEZA V2")
    procesar_dataset(ARCHIVO_DATASET1, SALIDA_DATASET1, MAPEO_DATASET1)
    # procesar_dataset(ARCHIVO_DATASET2, SALIDA_DATASET2, MAPEO_DATASET2)  # Comentado
```

---

## 🐛 **Solución de Problemas**

### **Error: "FileNotFoundError"**

```
ERROR: No se encontró dataset_2021_hash.csv
```

**Solución:**
- Verificar que los archivos CSV estén en la misma carpeta que el script
- O modificar las rutas en la configuración

### **Error: "UnicodeDecodeError"**

```
Error: 'utf-8' codec can't decode byte...
```

**Solución:**
```python
# Cambiar encoding en línea 373:
pd.read_csv(archivo_entrada, sep=';', encoding='latin-1', ...)
```

### **Error: "MemoryError"**

```
MemoryError: Unable to allocate array
```

**Solución:**
```python
# Reducir tamaño de chunks
CHUNK_SIZE = 1000  # En vez de 5000
```

### **Advertencia: "SettingWithCopyWarning"**

```
SettingWithCopyWarning: A value is trying to be set on a copy...
```

**Solución:** Ya manejado con `.copy()` en el código. Si aparece, es seguro ignorarlo.

---

## 📊 **Validación de Resultados**

### **Después de ejecutar el script:**

```python
import pandas as pd

# Cargar dataset limpio
df = pd.read_csv('dataset_2021_ultra_limpio.csv', sep=';', decimal=',')

# Verificar columnas
print("Columnas:", df.columns.tolist())

# Verificar IDs
print("\nPrimeros 5 estudiantes:")
print(df['Id_Estudiante'].head())
# Debería mostrar: Estudiante_1, Estudiante_2, etc.

# Verificar transformaciones categóricas
print("\nValores de Estado_Abandono:")
print(df['Estado_Abandono'].value_counts())
# Debería mostrar: NoAbandono, Abandono (no A, B)

# Verificar columnas LMS
cols_lms = [col for col in df.columns if 'LMS' in col]
print(f"\nColumnas LMS encontradas: {len(cols_lms)}")

# Verificar tamaño
print(f"\nRegistros: {len(df)}")
print(f"Columnas: {len(df.columns)}")
```

---

## 🔄 **Flujo Completo de Datos**

```
1. Dataset MDPI (Crudo)
   ├── dataset_2021_hash.csv (300 MB)
   └── dataset_2022_hash.csv (280 MB)
           ↓
2. Script de Limpieza
   └── limpiar_dataset_DEFINITIVO.py
           ↓
3. Datasets Limpios
   ├── dataset_2021_ultra_limpio.csv
   ├── dataset_2022_ultra_limpio.csv
   ├── mapeo_completo_2021.csv
   └── mapeo_completo_2022.csv
           ↓
4. Importador Django
   └── import_service_universidad.py
           ↓
5. Base de Datos MySQL
   └── academicpredict
```

---

## 📝 **Checklist de Preprocesamiento**

Antes de importar a Django:

- [ ] ✅ Descargar dataset crudo de MDPI
- [ ] ✅ Colocar archivos en carpeta `data/raw/`
- [ ] ✅ Ejecutar `limpiar_dataset_DEFINITIVO.py`
- [ ] ✅ Verificar que se generaron 4 archivos
- [ ] ✅ Validar transformaciones con script de verificación
- [ ] ✅ Revisar archivo de mapeo
- [ ] ✅ Mover datasets limpios a `data/processed/`
- [ ] ✅ Proceder con importación a Django

---

## 🎓 **Notas Técnicas**

### **¿Por qué Processing por Chunks?**

Los datasets son grandes (+150k filas × 77 columnas). Cargar todo en memoria de una vez podría causar:
- Uso excesivo de RAM (>2 GB)
- Lentitud en equipos con poca memoria
- Posibles crashes

**Solución:** Procesar 5000 filas a la vez.

### **¿Por qué Mantener Formato Europeo?**

El importador de Django (`import_service_universidad.py`) está configurado para leer formato europeo:
- Separador: `;`
- Decimal: `,`

Cambiar el formato requeriría modificar el importador.

### **¿Por qué Dos Archivos (2021 y 2022)?**

El dataset MDPI puede venir en múltiples archivos por año académico. El script procesa ambos y resetea los mapeos entre ellos para mantener IDs únicos por archivo.

---

## 🙏 **Créditos**

- **Dataset Original:** MDPI - "University Student Dropout Dataset"
- **Script:** Equipo AcademicPredict (Bastián Vega, Erin Muñoz, Sebastián Araya)
- **Versión:** 2.0 (Correcciones aplicadas)

---

## 📞 **Soporte**

¿Problemas con el preprocesamiento?

1. Revisar esta documentación
2. Verificar configuración de rutas
3. Consultar sección de Solución de Problemas
4. Contactar al equipo: academicpredict@ejemplo.com

---

<div align="center">
  <strong>Script de Preprocesamiento v2.0</strong>
  <br>
  <em>114 columnas renombradas • 5 categorías transformadas • Formato legible</em>
</div>