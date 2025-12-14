# 🎓 AcademicPredict - Sistema de Predicción de Deserción Universitaria

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![Machine Learning](https://img.shields.io/badge/ML-XGBoost%20%7C%20IsolationForest-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**AcademicPredict** es un sistema integral de detección temprana de deserción universitaria que combina análisis de datos, machine learning y gestión de alertas para identificar estudiantes en riesgo y facilitar intervenciones oportunas.

Desarrollado como proyecto de tesis de Ingeniería en Informática.

---

## 📋 **Tabla de Contenidos**

- [Características Principales](#-características-principales)
- [Requisitos del Sistema](#-requisitos-del-sistema)
- [Instalación](#-instalación)
- [Configuración Inicial](#-configuración-inicial)
- [Carga de Datos](#-carga-de-datos)
- [Sistema de Roles](#-sistema-de-roles)
- [Uso del Sistema](#-uso-del-sistema)
- [Arquitectura](#-arquitectura)
- [Tecnologías](#-tecnologías)
- [Créditos](#-créditos)

---

## ✨ **Características Principales**

### 🤖 **Machine Learning Avanzado**
- **Detección de Anomalías**: Isolation Forest para identificar patrones atípicos
- **Predicción de Deserción**: XGBoost con 78% ROC-AUC y 95% de recall
- **Análisis de Factores**: Identificación automática de factores de riesgo por estudiante
- **Validación Temporal**: Solo variables disponibles antes de la deserción

### 📊 **Dashboards Interactivos**
- **Dashboard Básico**: Métricas clave y visualizaciones de deserción
- **Dashboard Avanzado**: Análisis estadístico con heatmaps, box plots y correlaciones
- **Dashboard ML**: Predicciones en tiempo real con filtros avanzados
- **Filtros Dinámicos**: Año académico, carrera, campus, dedicación

### 🔔 **Sistema de Alertas Inteligente**
- Generación automática de alertas basadas en ML
- Priorización de casos (Crítico, Alto, Medio, Bajo)
- Workflow de seguimiento e intervenciones
- Historial completo de acciones

### 👥 **Sistema de Roles y Permisos**
- **Administrador**: Acceso completo, ejecución ML, importación de datos
- **Coordinador**: Gestión de alertas y asignación de casos
- **Coordinador de Carrera**: Vista filtrada por carrera específica
- **Analista**: Gestión de casos asignados únicamente

---

## 💻 **Requisitos del Sistema**

### **Software Requerido**

```
Python >= 3.8
MySQL >= 8.0
pip >= 21.0
```

### **Librerías Python Principales**

```
Django >= 4.2
pandas >= 1.5.0
numpy >= 1.24.0
scikit-learn >= 1.3.0
xgboost >= 2.0.0
scipy >= 1.10.0
imbalanced-learn >= 0.11.0
mysqlclient >= 2.2.0
openpyxl >= 3.1.0
```

---

## 🚀 **Instalación**

### **1. Clonar el Repositorio**

```bash
git clone https://github.com/tu-usuario/AcademicPredict.git
cd AcademicPredict
```

### **2. Crear Entorno Virtual**

**Windows:**
```bash
python -m venv entornovirtual
entornovirtual\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv entornovirtual
source entornovirtual/bin/activate
```

### **3. Instalar Dependencias**

```bash
pip install -r requirements.txt
```

### **4. Configurar Base de Datos**

#### **A. Crear Base de Datos MySQL**

```sql
CREATE DATABASE academicpredict CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'academicpredict_user'@'localhost' IDENTIFIED BY 'tu_contraseña_segura';
GRANT ALL PRIVILEGES ON academicpredict.* TO 'academicpredict_user'@'localhost';
FLUSH PRIVILEGES;
```

#### **B. Configurar `settings.py`**

Edita `academicpredict/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'academicpredict',
        'USER': 'academicpredict_user',
        'PASSWORD': 'tu_contraseña_segura',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}
```

### **5. Aplicar Migraciones**

```bash
python manage.py makemigrations
python manage.py migrate
```

### **6. Crear Superusuario**

```bash
python manage.py createsuperuser
```

Ingresa:
- **Username**: admin (o tu preferencia)
- **Email**: tu_email@ejemplo.com
- **Password**: (contraseña segura)

### **7. Crear Perfil para Superusuario**

```bash
python manage.py shell
```

Ejecuta en el shell de Python:

```python
from django.contrib.auth.models import User
from prototipo.models import PerfilUsuario

admin = User.objects.get(username='admin')  # Cambia 'admin' por tu username
PerfilUsuario.objects.create(usuario=admin, rol='admin')
print("✅ Perfil de administrador creado")
exit()
```

---

## ⚙️ **Configuración Inicial**

### **1. Crear Usuarios de Prueba**

El sistema incluye un comando para crear automáticamente 8 usuarios de prueba con diferentes roles:

```bash
python manage.py crear_usuarios_roles
```

**Usuarios creados:**

| Username | Rol | Email | Contraseña |
|----------|-----|-------|------------|
| `admin_prueba` | Administrador | admin@academicpredict.cl | admin123 |
| `coord_general` | Coordinador | coordinador1@academicpredict.cl | admin123 |
| `coord_academico` | Coordinador | coordinador2@academicpredict.cl | admin123 |
| `coord_ingenieria` | Coordinador de Carrera | coord.ing@academicpredict.cl | admin123 |
| `coord_medicina` | Coordinador de Carrera | coord.med@academicpredict.cl | admin123 |
| `analista_juan` | Analista | juan.analista@academicpredict.cl | admin123 |
| `analista_sofia` | Analista | sofia.analista@academicpredict.cl | admin123 |
| `analista_diego` | Analista | diego.analista@academicpredict.cl | admin123 |

**Para recrear los usuarios:**

```bash
python manage.py crear_usuarios_roles --limpiar
```

### **2. Iniciar Servidor de Desarrollo**

```bash
python manage.py runserver
```

Accede a: **http://localhost:8000**

---

## 📂 **Carga de Datos**

### **1. Preparar Dataset**

El sistema requiere un archivo CSV con **77 variables** en el siguiente formato:

#### **Formato del CSV:**
- **Separador**: `;` (punto y coma)
- **Decimal**: `,` (coma)
- **Encoding**: UTF-8
- **Extensión**: `.csv`

#### **Variables Principales:**

**Datos del Estudiante:**
- `codigo_estudiante` (único)
- `codigo_carrera`
- `anio_ingreso_universidad`
- `anio_inicio_estudios`
- `tipo_acceso_universidad`
- `nota_selectividad_base`
- `nota_selectividad_total`
- `orden_preferencia_carrera`

**Datos Socioeconómicos:**
- `nivel_educativo_padre`
- `nivel_educativo_madre`
- `dedicacion_estudios` (TiempoCompleto/TiempoParcial)
- `es_desplazado` (True/False)

**Datos Académicos (por año):**
- `anio_academico`
- `codigo_asignatura`
- `creditos_matriculados`
- `creditos_aprobados`
- `nota_final_asignatura`

**Datos LMS:**
- `accesos_lms_total`
- `accesos_lms_semana_1` hasta `accesos_lms_semana_20`
- `dias_activos_lms`

**Target:**
- `abandono` (True/False) - Variable objetivo

### **2. Importar Datos**

#### **Opción A: Interfaz Web (Recomendado)**

1. Inicia sesión como **Administrador**
2. Ve a: **Importar Datos** (menú lateral)
3. Selecciona tu archivo CSV
4. Click en **"Iniciar Importación"**
5. Espera a que termine (puede tardar 5-15 minutos para datasets grandes)

#### **Opción B: Script Python**

```python
from prototipo.service.import_service_universidad import ImportadorDatosUniversitarios

ruta_csv = 'ruta/a/tu/dataset.csv'
importador = ImportadorDatosUniversitarios(ruta_csv)
estadisticas = importador.importar_completo()
reporte = importador.generar_reporte()
print(reporte)
```

### **3. Verificar Importación**

```bash
python manage.py shell
```

```python
from prototipo.models import *

print(f"Carreras: {CarreraUniversitaria.objects.count()}")
print(f"Estudiantes: {EstudianteUniversitario.objects.count()}")
print(f"Asignaturas: {AsignaturaUniversitaria.objects.count()}")
print(f"Registros Académicos: {RegistroAcademicoUniversitario.objects.count()}")
exit()
```

---

## 👥 **Sistema de Roles**

### **Roles Disponibles**

#### 🔴 **Administrador**
**Permisos:**
- ✅ Acceso completo al sistema
- ✅ Ejecutar detección ML
- ✅ Importar/exportar datos
- ✅ Gestionar usuarios
- ✅ Acceso al panel de Django Admin

**Casos de uso:**
- Configuración inicial del sistema
- Mantenimiento de datos
- Ejecución de modelos ML
- Supervisión general

#### 🟡 **Coordinador**
**Permisos:**
- ✅ Ver todos los estudiantes
- ✅ Asignar casos a analistas
- ✅ Gestionar alertas
- ✅ Generar reportes
- ❌ NO puede ejecutar ML
- ❌ NO puede importar datos

**Casos de uso:**
- Distribución de casos
- Supervisión de intervenciones
- Generación de reportes institucionales

#### 🔵 **Coordinador de Carrera**
**Permisos:**
- ✅ Ver estudiantes de SU carrera únicamente
- ✅ Asignar casos de su carrera
- ✅ Gestionar alertas de su carrera
- ✅ Generar reportes de su carrera
- ❌ NO puede ejecutar ML
- ❌ NO puede importar datos

**Casos de uso:**
- Gestión específica por programa académico
- Seguimiento de estudiantes de una carrera
- Coordinación con docentes de la carrera

#### 🟢 **Analista**
**Permisos:**
- ✅ Ver SOLO casos asignados a él/ella
- ✅ Registrar intervenciones
- ✅ Marcar casos como resueltos
- ✅ Ver ficha de seguimiento
- ❌ NO puede asignar casos
- ❌ NO puede ver casos de otros analistas
- ❌ NO puede cambiar estado de alertas

**Casos de uso:**
- Atención directa a estudiantes
- Registro de tutorías y reuniones
- Seguimiento personalizado

### **Asignación de Roles**

#### **Método 1: Django Admin**

1. Accede a: `http://localhost:8000/admin/`
2. Ve a: **Perfiles de Usuarios**
3. Edita el usuario
4. Cambia el campo **"Rol"**
5. Guarda

#### **Método 2: Shell de Django**

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from prototipo.models import PerfilUsuario

user = User.objects.get(username='nombre_usuario')
perfil = user.perfil
perfil.rol = 'coordinador'  # admin, coordinador, coordinador_carrera, analista
perfil.save()
print(f"✅ Rol actualizado a: {perfil.get_rol_display()}")
exit()
```

---

## 🎯 **Uso del Sistema**

### **1. Inicio de Sesión**

1. Accede a: `http://localhost:8000/`
2. Ingresa credenciales
3. Serás redirigido al **Home**

### **2. Navegación Principal**

#### **Menú Lateral:**
- 🏠 **Inicio**: Dashboard principal con resumen
- 📂 **Importar Datos**: Carga de datasets (solo Admin)
- 📊 **Dashboard Básico**: Métricas y gráficos de deserción
- 📈 **Dashboard Avanzado**: Análisis estadístico avanzado
- 🔔 **Alertas**: Sistema de alertas y casos
- 👥 **Estudiantes en Seguimiento**: Listado de casos activos
- 📝 **Reportes**: Generación de reportes (Admin/Coordinadores)
- 🤖 **Dashboard ML**: Predicciones de machine learning
- 📋 **Mis Casos Asignados**: Vista personal (solo Analistas)

### **3. Flujo de Trabajo Típico**

#### **Para Administradores:**

1. **Importar datos** desde CSV
2. **Ejecutar detección ML** (Dashboard ML → Botón "Ejecutar Detección")
3. Esperar 2-5 minutos mientras se procesan los modelos
4. **Revisar predicciones** en Dashboard ML
5. **Asignar casos críticos** a analistas
6. **Supervisar intervenciones**

#### **Para Coordinadores:**

1. **Revisar alertas** en Dashboard de Alertas
2. **Filtrar por prioridad** (Críticas → Altas → Medias)
3. **Asignar casos** a analistas según carga de trabajo
4. **Generar reportes** mensuales
5. **Supervisar estado** de intervenciones

#### **Para Analistas:**

1. **Revisar "Mis Casos Asignados"** en el menú
2. **Abrir detalle** de estudiante en riesgo
3. **Registrar intervención** (tutoría, reunión, etc.)
4. **Actualizar ficha de seguimiento**
5. **Marcar como resuelto** cuando corresponda

### **4. Ejecución de Machine Learning**

**⚠️ Solo disponible para Administradores**

1. Ve a: **Dashboard ML**
2. Click en **"Ejecutar Detección"**
3. Espera mientras se procesan los modelos:
   - Isolation Forest (anomalías)
   - XGBoost (predicción de deserción)
   - Regresión (rendimiento futuro)
4. Revisa los resultados:
   - Nivel de riesgo por estudiante
   - Probabilidad de deserción (0-100%)
   - Factores de riesgo identificados
5. Filtra por:
   - Nivel de riesgo
   - Anomalías
   - Código de estudiante

### **5. Gestión de Alertas**

#### **Ver Alertas:**
- Dashboard de Alertas → Tabla con todas las alertas
- Filtros: Estado, Prioridad, Búsqueda

#### **Cambiar Estado de Alerta:**
(Solo Admin/Coordinadores)
- Detalle de Alerta → Cambiar Estado
- Opciones: Pendiente, En Revisión, Resuelta, Descartada

#### **Registrar Intervención:**
- Ficha de Seguimiento → "Nueva Intervención"
- Tipos: Tutoría, Apoyo Psicológico, Orientación, etc.
- Resultado: Exitosa, Parcial, Sin Efecto

### **6. Exportación de Datos**

**Formatos disponibles:**
- 📄 **CSV**: Datos crudos para análisis externo
- 📊 **Excel**: Con formato y filtros
- 📑 **PDF**: Reportes institucionales

**Dónde exportar:**
- Dashboard ML → Botones "Exportar CSV/Excel"
- Listado de Seguimiento → "Exportar Excel"
- Reportes → Generador de reportes personalizados

---

## 🏗️ **Arquitectura**

### **Estructura del Proyecto**

```
AcademicPredict/
├── academicpredict/          # Configuración principal Django
│   ├── settings.py           # Configuración del proyecto
│   ├── urls.py               # URLs principales
│   └── wsgi.py
│
├── prototipo/                # Aplicación principal
│   ├── models.py             # 10 modelos Django
│   ├── views.py              # Vistas Universidad
│   ├── views_ml.py           # Vistas Machine Learning
│   ├── views_roles.py        # Vistas Sistema de Roles
│   ├── views_alertas.py      # Vistas Sistema de Alertas
│   ├── urls_prototipo.py     # URLs Universidad + Roles
│   ├── urls_ml.py            # URLs Machine Learning
│   ├── urls_alertas.py       # URLs Sistema de Alertas
│   ├── admin.py              # Configuración Django Admin
│   │
│   ├── service/              # Lógica de negocio
│   │   ├── import_service_universidad.py
│   │   └── services_alertas.py
│   │
│   ├── ml/                   # Modelos de Machine Learning
│   │   ├── predictor.py      # XGBoost + Isolation Forest
│   │   └── ejecutar_deteccion_ml.py
│   │
│   ├── management/           # Comandos personalizados
│   │   └── commands/
│   │       └── crear_usuarios_roles.py
│   │
│   └── templates/            # Templates HTML
│       ├── base.html
│       ├── home.html
│       ├── dashboard.html
│       ├── dashboard_avanzado.html
│       ├── ml/
│       │   ├── dashboard_ml.html
│       │   └── estudiante_detalle_ml.html
│       └── alertas/
│           ├── dashboard_alertas.html
│           ├── detalle_alerta.html
│           └── ficha_seguimiento.html
│
├── static/                   # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── img/
│
├── media/                    # Archivos subidos
│
├── requirements.txt          # Dependencias Python
└── manage.py                 # Script de gestión Django
```

### **Modelos de Datos**

#### **Modelos Base:**
1. `CarreraUniversitaria` - Programas académicos
2. `EstudianteUniversitario` - Perfil demográfico y socioeconómico
3. `AsignaturaUniversitaria` - Cursos disponibles
4. `RegistroAcademicoUniversitario` - Historial académico completo

#### **Modelos ML:**
5. `PrediccionDesercionUniversitaria` - Resultados de ML
6. `TrazabilidadPrediccionDesercion` - Historial de predicciones

#### **Sistema de Alertas:**
7. `AlertaEstudiante` - Alertas generadas
8. `IntervencionEstudiante` - Acciones realizadas
9. `FichaSeguimientoEstudiante` - Estado de seguimiento

#### **Sistema de Roles:**
10. `PerfilUsuario` - Roles y permisos

---

## 🛠️ **Tecnologías**

### **Backend**
- **Django 4.2**: Framework web principal
- **Python 3.8+**: Lenguaje de programación
- **MySQL 8.0**: Base de datos relacional

### **Machine Learning**
- **XGBoost**: Predicción de deserción (Gradient Boosting)
- **Scikit-learn**: Isolation Forest (detección de anomalías)
- **Pandas**: Procesamiento de datos
- **NumPy**: Operaciones numéricas
- **SciPy**: Análisis estadístico
- **SMOTE**: Balanceo de clases

### **Frontend**
- **Bootstrap 5.3**: Framework CSS
- **Chart.js**: Gráficos interactivos
- **Plotly.js**: Visualizaciones avanzadas (heatmaps, box plots)
- **Font Awesome 6**: Iconografía
- **jQuery**: Interactividad

### **Análisis de Datos**
- **Pearson Correlation**: Matriz de correlaciones
- **Box Plots**: Distribución por grupos
- **Linear Regression**: Tendencias temporales
- **Clustering**: Segmentación de estudiantes

---

## 📊 **Métricas del Modelo ML**

### **XGBoost (Predicción de Deserción)**
- **ROC-AUC**: 78%
- **Recall**: 95%
- **Precisión**: ~70%
- **Features**: 43 variables temporalmente válidas

**Optimización:**
- Hiperparámetros ajustados por Grid Search
- SMOTE para balanceo de clases
- Validación cruzada estratificada

### **Isolation Forest (Detección de Anomalías)**
- **Contamination**: 0.05
- **Features**: Rendimiento académico + Accesos LMS
- **Output**: Score de anomalía (-1 a 1)

### **Variables Clave**
1. Rendimiento académico previo
2. Patrón de accesos LMS
3. Créditos aprobados vs matriculados
4. Nota de selectividad
5. Año de ingreso
6. Tipo de acceso a la universidad

---

## 🐛 **Solución de Problemas Comunes**

### **1. Error: "No module named 'mysqlclient'"**

**Solución Windows:**
```bash
pip install mysqlclient
```

Si falla, instala el binario pre-compilado:
```bash
pip install https://download.lfd.uci.edu/pythonlibs/archived/mysqlclient-2.2.0-cp38-cp38-win_amd64.whl
```

### **2. Error: "Access denied for user"**

**Solución:**
Verifica credenciales en `settings.py` y permisos MySQL:
```sql
GRANT ALL PRIVILEGES ON academicpredict.* TO 'academicpredict_user'@'localhost';
FLUSH PRIVILEGES;
```

### **3. Login no funciona (recarga página)**

**Causa:** Falta crear `PerfilUsuario` para el usuario.

**Solución:**
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
from prototipo.models import PerfilUsuario

user = User.objects.get(username='tu_usuario')
PerfilUsuario.objects.create(usuario=user, rol='admin')
exit()
```

### **4. Error: "Cannot resolve keyword 'usuario'"**

**Causa:** El campo se llama `user` no `usuario`.

**Solución:** Actualiza el código para usar `user` en vez de `usuario`.

### **5. Importación muy lenta**

**Solución:**
- Asegúrate de tener índices en la BD
- Usa datasets <100k registros para pruebas
- Considera usar `bulk_create()` para optimización

### **6. ML no genera predicciones**

**Verificar:**
1. ¿Hay datos en la BD? (`EstudianteUniversitario.objects.count()`)
2. ¿Usuario es Admin? (Solo Admin puede ejecutar ML)
3. ¿Hay suficientes estudiantes? (Mínimo 100 recomendado)

---

## 📖 **Documentación Adicional**

### **Papers y Referencias**
- [XGBoost: A Scalable Tree Boosting System](https://arxiv.org/abs/1603.02754)
- [Isolation Forest Algorithm](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf)
- [SMOTE: Synthetic Minority Over-sampling Technique](https://arxiv.org/abs/1106.1813)

### **Guías de Django**
- [Documentación Oficial Django 4.2](https://docs.djangoproject.com/en/4.2/)
- [Django Rest Framework](https://www.django-rest-framework.org/)

### **Machine Learning**
- [Scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)

---

## 🤝 **Contribuciones**

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 👨‍💻 **Autor**

**Bastián González**
- Ingeniero en Informática
- Proyecto de Tesis - AcademicPredict
- 📧 Email: [tu_email@ejemplo.com]
- 💼 LinkedIn: [tu-perfil]
- 🐙 GitHub: [tu-usuario]

---

## 🙏 **Agradecimientos**

- Universidad [Nombre] por facilitar el dataset
- Profesores guía por su orientación
- Comunidad de Django y Scikit-learn por su excelente documentación
- Anthropic Claude por asistencia en desarrollo

---

## 📈 **Roadmap Futuro**

### **v2.0 (Planificado)**
- [ ] Deep Learning con LSTM para análisis temporal
- [ ] API REST completa
- [ ] Notificaciones por email/SMS
- [ ] Dashboard móvil responsivo
- [ ] Integración con sistemas SIS universitarios
- [ ] Análisis de sentimiento en comentarios
- [ ] Predicción de rendimiento por asignatura

### **v1.5 (En desarrollo)**
- [ ] Tests unitarios completos
- [ ] Documentación API
- [ ] Docker deployment
- [ ] CI/CD con GitHub Actions

---

## 📞 **Soporte**

¿Problemas o preguntas?

1. Revisa la sección [Solución de Problemas](#-solución-de-problemas-comunes)
2. Busca en [Issues](https://github.com/tu-usuario/AcademicPredict/issues)
3. Crea un nuevo Issue con:
   - Descripción del problema
   - Pasos para reproducir
   - Logs relevantes
   - Versión de Python/Django

---

## ⭐ **Dale una Estrella**

Si este proyecto te fue útil, considera darle una ⭐ en GitHub. ¡Gracias!

---

<div align="center">
  <strong>Desarrollado con ❤️ para mejorar la retención universitaria</strong>
</div>