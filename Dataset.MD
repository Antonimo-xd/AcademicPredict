# 📊 Dataset - AcademicPredict

---

## 🎓 **Fuente del Dataset**

### **Título Completo:**
**"University Student Dropout: A Longitudinal Dataset of Demographic, Socioeconomic, and Academic Indicators"**

### **Publicación:**
- 📰 **Journal**: Data (MDPI)
- 📅 **Año**: 2025
- 🔢 **Volumen**: 10, Número 10
- 📄 **Páginas**: 162
- 🔗 **URL**: https://www.mdpi.com/2306-5729/10/10/162
- 🆔 **DOI**: https://doi.org/10.3390/data10100162
- 📖 **Publisher**: MDPI (Multidisciplinary Digital Publishing Institute)

---

## 📋 **Descripción del Dataset**

### **Características Generales:**

| Característica | Detalle |
|---------------|---------|
| **Registros** | +150,000 estudiantes |
| **Variables** | 77 variables por registro |
| **Tipo de datos** | Longitudinal (múltiples años) |
| **Período** | Múltiples cohortes académicas |
| **Origen** | Universidad europea |
| **Anonimización** | ✅ Datos completamente anonimizados |
| **Formato** | CSV con separador `;` y decimal `,` |
| **Tamaño aproximado** | 300-500 MB |

---

## 🔬 **Categorías de Variables**

### **1. Datos Demográficos (5-10 variables)**
- Código de estudiante (anonimizado)
- Año de ingreso a la universidad
- Año de inicio de estudios
- Campus
- Tipo de acceso

### **2. Datos Socioeconómicos (10-15 variables)**
- Nivel educativo del padre
- Nivel educativo de la madre
- Dedicación de estudios (Tiempo Completo/Parcial)
- Situación de desplazamiento
- Becas y ayudas financieras

### **3. Datos Académicos Previos (5-10 variables)**
- Nota de selectividad base
- Nota de selectividad total
- Orden de preferencia de carrera
- Tipo de bachillerato/secundaria

### **4. Rendimiento Académico por Año (20-25 variables)**
- Año académico
- Código de asignatura
- Créditos matriculados
- Créditos aprobados
- Créditos acumulados
- Nota final de asignatura
- Número de evaluaciones
- Aprobado/Suspenso

### **5. Datos del LMS (Learning Management System) (20-25 variables)**
- Accesos totales al LMS
- Accesos por semana (semana 1 a semana 20)
- Días activos en el LMS
- Recursos descargados
- Participación en foros
- Entrega de tareas

### **6. Variable Objetivo (Target) (1 variable)**
- **Abandono** (True/False)
  - `True`: Estudiante abandonó los estudios
  - `False`: Estudiante continúa o completó estudios

---

## 📊 **Estadísticas del Dataset**

### **Distribución de Clases:**
```
Estudiantes Activos/Graduados: ~94%
Estudiantes que Abandonaron:   ~6%
```

**⚠️ Desbalanceo de clases:** El dataset presenta un desbalanceo significativo, lo cual requiere técnicas especiales como SMOTE para el entrenamiento de modelos ML.

### **Variables Numéricas:**
- Notas: Escala 0-20 (sistema europeo)
- Créditos: 0-300+ (acumulativo)
- Accesos LMS: 0-1000+ por semestre
- Edad al ingreso: Típicamente 18-30 años

### **Variables Categóricas:**
- Campus: 3-5 ubicaciones diferentes
- Tipo de acceso: ~10 categorías
- Nivel educativo padres: ~5 niveles
- Dedicación: 2 categorías (Completo/Parcial)

---

## 🎯 **Uso en AcademicPredict**

### **Script de Limpieza del Dataset**

El proyecto incluye un script completo de preprocesamiento que transforma el dataset crudo de MDPI al formato requerido por AcademicPredict.

**Ubicación:** `scripts/limpiar_dataset_DEFINITIVO.py`

**Características del script:**
- ✅ Convierte hashes a etiquetas legibles (`Estudiante_1`, `Carrera_1`)
- ✅ Renombra 114 columnas a nombres descriptivos en español
- ✅ Transforma valores categóricos (A/B → Abandono/NoAbandono)
- ✅ Corrige formato europeo (`;` separador, `,` decimal)
- ✅ Procesa archivos grandes por chunks (5000 filas)
- ✅ Genera archivo de mapeo completo
- ✅ Maneja columnas LMS con fechas (año_mes)

**Uso:**
```bash
# 1. Colocar dataset crudo en la carpeta del script
# Archivos requeridos:
# - dataset_2021_hash.csv
# - dataset_2022_hash.csv

# 2. Ejecutar el script
python scripts/limpiar_dataset_DEFINITIVO.py

# 3. Archivos generados:
# - dataset_2021_ultra_limpio.csv
# - dataset_2022_ultra_limpio.csv
# - mapeo_completo_2021.csv
# - mapeo_completo_2022.csv
```

**Ver documentación completa:** [PREPROCESAMIENTO.md](PREPROCESAMIENTO.md)

---

### **Preprocesamiento Aplicado:**

1. **Limpieza de Datos:**
   - Conversión de hashes a códigos legibles
   - Formato europeo (`;` y `,`) a estándar
   - Codificación UTF-8
   - Eliminación de duplicados

2. **Feature Engineering:**
   - Cálculo de rendimiento académico (%)
   - Agregación de accesos LMS por períodos
   - Cálculo de progreso de carrera
   - Identificación de patrones temporales

3. **Validación Temporal:**
   - ✅ Solo variables disponibles ANTES del abandono
   - ✅ Eliminación de data leakage
   - ✅ 43 variables temporalmente válidas (de 77 originales)

### **Variables Descartadas (Data Leakage):**

Se descartaron ~34 variables que contenían información posterior al abandono:
- Créditos totales acumulados (conocido solo al final)
- Asignaturas de años posteriores
- Datos de graduación
- Variables de estado final

---

## 📥 **Descarga del Dataset**

### **Opción 1: Fuente Original (MDPI)**

```bash
# Visitar el artículo original
https://www.mdpi.com/2306-5729/10/10/162

# Buscar sección "Data Availability"
# Descargar el dataset desde el repositorio indicado
```

### **Opción 2: Repositorio del Proyecto**

Por limitaciones de tamaño de GitHub (archivos >100 MB), el dataset NO está incluido en este repositorio.

**Descarga desde:**
- 📦 **Google Drive**: [Link a compartir]
- 📦 **Releases**: [GitHub Releases del proyecto]

**Instrucciones:**
```bash
# 1. Descargar el archivo
wget [URL_del_dataset] -O universidad_data.csv

# 2. Colocar en la carpeta correcta
mv universidad_data.csv AcademicPredict/data/raw/

# 3. Verificar
ls -lh data/raw/universidad_data.csv
# Debería mostrar ~300-500 MB
```

---

## 🔐 **Licencia del Dataset**

El dataset está disponible bajo licencia abierta para investigación académica.

**Consulta el artículo original para:**
- Términos de uso específicos
- Restricciones de redistribución
- Requisitos de citación

**⚠️ Importante:**
- ✅ Permitido: Uso académico e investigación
- ✅ Permitido: Publicación de resultados
- ❌ Revisar: Uso comercial (consultar términos)
- ✅ Requerido: Citar el artículo original

---

## 📝 **Cómo Citar**

Si utilizas este dataset en tu investigación, por favor cita:

### **Formato BibTeX:**

```bibtex
@article{mdpi_student_dropout_2025,
  title={University Student Dropout: A Longitudinal Dataset of Demographic, Socioeconomic, and Academic Indicators},
  author={[Autores según aparezcan en el paper]},
  journal={Data},
  volume={10},
  number={10},
  pages={162},
  year={2025},
  publisher={MDPI},
  doi={10.3390/data10100162},
  url={https://www.mdpi.com/2306-5729/10/10/162}
}
```

### **Formato APA:**

```
[Autores]. (2025). University Student Dropout: A Longitudinal Dataset 
of Demographic, Socioeconomic, and Academic Indicators. Data, 10(10), 162. 
https://doi.org/10.3390/data10100162
```

### **Formato IEEE:**

```
[Autores], "University Student Dropout: A Longitudinal Dataset of 
Demographic, Socioeconomic, and Academic Indicators," Data, vol. 10, 
no. 10, p. 162, 2025. DOI: 10.3390/data10100162
```

---

## 🔍 **Trabajos Relacionados**

Este dataset ha sido utilizado en:

- [Lista de papers que usan este dataset]
- [Benchmarks y comparaciones]
- [Otros proyectos de investigación]

**Tu proyecto AcademicPredict contribuye a:**
- Validación de técnicas de ML para deserción universitaria
- Implementación práctica de sistemas de alerta temprana
- Demostración de la importancia de validación temporal en ML

---

## 📧 **Contacto sobre el Dataset**

**Para consultas sobre el dataset original:**
- 📧 Contactar a los autores del paper MDPI
- 🌐 Visitar: https://www.mdpi.com/2306-5729/10/10/162

**Para consultas sobre su uso en AcademicPredict:**
- 📧 Equipo AcademicPredict: academicpredict@ejemplo.com
- 🐙 GitHub Issues: [Link al repositorio]

---

## ✅ **Checklist de Uso del Dataset**

Antes de usar el dataset, verifica:

- [ ] ✅ Leer el artículo original completo
- [ ] ✅ Descargar el dataset desde fuente confiable
- [ ] ✅ Verificar integridad del archivo (tamaño ~300-500 MB)
- [ ] ✅ Colocar en `data/raw/universidad_data.csv`
- [ ] ✅ Revisar términos de licencia
- [ ] ✅ Preparar citación correcta
- [ ] ✅ Ejecutar script de importación
- [ ] ✅ Verificar carga exitosa en la BD

---

## 🙏 **Agradecimientos**

El equipo de AcademicPredict agradece enormemente a los autores del dataset MDPI por:

- 🎓 Compartir datos de investigación de alta calidad
- 📊 Proporcionar +150,000 registros longitudinales
- 🔬 Facilitar la investigación en deserción universitaria
- 📖 Documentación exhaustiva de las variables
- 🌍 Contribuir al conocimiento científico abierto

**Este proyecto no sería posible sin su contribución a la ciencia abierta.**

---

<div align="center">
  <strong>Dataset: University Student Dropout</strong>
  <br>
  <em>MDPI Data Journal • Volume 10, Issue 10, 2025</em>
  <br>
  <a href="https://doi.org/10.3390/data10100162">DOI: 10.3390/data10100162</a>
</div>