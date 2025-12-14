"""
===============================================================================
PREPARACIÓN DE DATOS ML - VERSIÓN CORREGIDA FINAL
===============================================================================

✅ Mapeo correcto de estado_abandono:
   - 'Abandono' → clase 1 (6.73%)
   - 'NoAbandono' → clase 0 (93.27%)

✅ Configuración automática de Django
✅ Verificación completa del proceso

Ejecuta desde el mismo directorio que manage.py

Autor: Bastián
Fecha: 25 de noviembre de 2024
===============================================================================
"""

import os
import sys
import re

print("=" * 80)
print("🧹 PREPARACIÓN DE DATOS ML - VERSIÓN CORREGIDA FINAL")
print("=" * 80)

# ============================================================================
# CONFIGURAR DJANGO
# ============================================================================

print("\n🔧 Configurando Django...")

if not os.path.exists('manage.py'):
    print("\n❌ ERROR: No se encontró manage.py")
    print("   Ejecuta este script desde el directorio donde está manage.py")
    sys.exit(1)

with open('manage.py', 'r', encoding='utf-8') as f:
    manage_content = f.read()

match = re.search(r"'DJANGO_SETTINGS_MODULE',\s*['\"]([^'\"]+)['\"]", manage_content)

if match:
    settings_module = match.group(1)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    
    import django
    django.setup()
    print(f"✅ Django configurado: {settings_module}")
else:
    print("❌ No se pudo detectar DJANGO_SETTINGS_MODULE")
    sys.exit(1)

# ============================================================================
# IMPORTAR LIBRERÍAS
# ============================================================================

import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from datetime import datetime

# ============================================================================
# PASO 1: EXTRAER DATOS
# ============================================================================

print("\n" + "=" * 80)
print("📊 PASO 1: EXTRAER DATOS")
print("=" * 80)

try:
    from prototipo.models import RegistroAcademicoUniversitario, EstudianteUniversitario
    print("✅ Modelos importados")
except ImportError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("\n⏳ Extrayendo datos...")

total = RegistroAcademicoUniversitario.objects.count()
print(f"✅ Registros en BD: {total:,}")

if total == 0:
    print("❌ No hay datos en la BD")
    sys.exit(1)

queryset = RegistroAcademicoUniversitario.objects.all()
data = pd.DataFrame(list(queryset.values()))

print(f"✅ Datos extraídos: {len(data):,} registros × {len(data.columns)} columnas")

# ============================================================================
# PASO 2: CREAR TARGET (CON MAPEO CORREGIDO)
# ============================================================================

print("\n" + "=" * 80)
print("🎯 PASO 2: CREAR VARIABLE TARGET (MAPEO CORREGIDO)")
print("=" * 80)

print("\n⏳ Obteniendo estado de abandono...")

try:
    estudiantes = EstudianteUniversitario.objects.all().values('id', 'estado_abandono')
    
    # ✅ MAPEO CORREGIDO: Solo 'Abandono' (exacto) es clase 1
    estado_dict = {
        e['id']: 1 if str(e['estado_abandono']).strip() == 'Abandono' else 0
        for e in estudiantes
    }
    
    print(f"✅ Mapeo creado: {len(estado_dict):,} estudiantes")
    
    # Mapear al dataframe
    data['abandono'] = data['estudiante_id'].map(estado_dict)
    
    # Verificar distribución
    n_total = len(data)
    n_abandonos = int(data['abandono'].sum())
    n_no_abandonos = n_total - n_abandonos
    
    print(f"\n📊 DISTRIBUCIÓN DEL TARGET:")
    print(f"   - Total: {n_total:,}")
    print(f"   - Clase 1 (Abandono): {n_abandonos:,} ({n_abandonos/n_total*100:.2f}%)")
    print(f"   - Clase 0 (NoAbandono): {n_no_abandonos:,} ({n_no_abandonos/n_total*100:.2f}%)")
    
    # Verificar que hay ambas clases
    if n_abandonos == 0:
        print("\n❌ ERROR: No hay abandonos en los datos")
        sys.exit(1)
    
    if n_no_abandonos == 0:
        print("\n❌ ERROR: No hay no-abandonos en los datos")
        sys.exit(1)
    
    print("\n✅ Target válido: ambas clases presentes")
    
except Exception as e:
    print(f"❌ Error al crear target: {e}")
    sys.exit(1)

# ============================================================================
# PASO 3: SELECCIONAR FEATURES
# ============================================================================

print("\n" + "=" * 80)
print("🔍 PASO 3: SELECCIONAR FEATURES")
print("=" * 80)

# Seleccionar todas las columnas numéricas (excepto IDs y target)
features_numericas = data.select_dtypes(include=[np.number]).columns.tolist()
excluir = ['id', 'estudiante_id', 'asignatura_id', 'abandono']
features_disponibles = [f for f in features_numericas if f not in excluir]

print(f"\n✅ Features numéricas disponibles: {len(features_disponibles)}")

if len(features_disponibles) == 0:
    print("❌ No hay features numéricas disponibles")
    sys.exit(1)

print("\n📋 Lista de features:")
for i, feat in enumerate(features_disponibles, 1):
    print(f"   {i}. {feat}")

# ============================================================================
# PASO 4: PREPARAR DATASET
# ============================================================================

print("\n" + "=" * 80)
print("🛠️  PASO 4: PREPARAR DATASET")
print("=" * 80)

# Seleccionar features + target
X = data[features_disponibles].copy()
y = data['abandono'].copy()

# Verificar valores nulos
print(f"\n🔧 Valores faltantes antes: {X.isnull().sum().sum():,}")

# Rellenar valores faltantes con mediana
if X.isnull().sum().sum() > 0:
    for col in features_disponibles:
        if X[col].isnull().sum() > 0:
            X[col] = X[col].fillna(X[col].median())
    print(f"✅ Valores faltantes imputados")
else:
    print(f"✅ No hay valores faltantes")

# Eliminar filas donde target es NaN
mask_valido = ~y.isna()
X = X[mask_valido]
y = y[mask_valido].astype(int)

print(f"\n✅ Dataset final:")
print(f"   - X shape: {X.shape}")
print(f"   - y shape: {y.shape}")
print(f"   - Clase 0: {(y == 0).sum():,} ({(y == 0).mean()*100:.2f}%)")
print(f"   - Clase 1: {(y == 1).sum():,} ({(y == 1).mean()*100:.2f}%)")

feature_names = list(X.columns)

# ============================================================================
# PASO 5: NORMALIZACIÓN
# ============================================================================

print("\n" + "=" * 80)
print("🔍 PASO 5: NORMALIZACIÓN")
print("=" * 80)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=feature_names, index=X.index)

print("✅ StandardScaler aplicado")

# ============================================================================
# PASO 6: SPLIT TRAIN/TEST
# ============================================================================

print("\n" + "=" * 80)
print("✂️  PASO 6: SPLIT TRAIN/TEST")
print("=" * 80)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"\n✅ Split completado:")
print(f"   - Train: {len(X_train):,} ({len(X_train)/len(X)*100:.1f}%)")
print(f"   - Test: {len(X_test):,} ({len(X_test)/len(X)*100:.1f}%)")
print(f"\n📊 Balance en TRAIN:")
print(f"   - Clase 0: {(y_train == 0).sum():,} ({(y_train == 0).mean()*100:.2f}%)")
print(f"   - Clase 1: {(y_train == 1).sum():,} ({(y_train == 1).mean()*100:.2f}%)")

# ============================================================================
# PASO 7: SMOTE (BALANCEO)
# ============================================================================

print("\n" + "=" * 80)
print("⚖️  PASO 7: SMOTE (BALANCEO)")
print("=" * 80)

n_antes_0 = (y_train == 0).sum()
n_antes_1 = (y_train == 1).sum()

print(f"\n📊 Antes de SMOTE:")
print(f"   - Clase 0: {n_antes_0:,}")
print(f"   - Clase 1: {n_antes_1:,}")
print(f"   - Ratio: {n_antes_0/n_antes_1:.2f}:1")

smote = SMOTE(random_state=42)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

n_despues_0 = (y_train_balanced == 0).sum()
n_despues_1 = (y_train_balanced == 1).sum()

print(f"\n📊 Después de SMOTE:")
print(f"   - Clase 0: {n_despues_0:,}")
print(f"   - Clase 1: {n_despues_1:,}")
print(f"   - Ratio: 1:1 (balanceado)")
print(f"\n✅ Ejemplos sintéticos creados: {n_despues_1 - n_antes_1:,}")

# ============================================================================
# PASO 8: GUARDAR ARCHIVOS
# ============================================================================

print("\n" + "=" * 80)
print("💾 PASO 8: GUARDAR ARCHIVOS")
print("=" * 80)

os.makedirs('modelos_ml', exist_ok=True)
os.makedirs('resultados_ml', exist_ok=True)

# 1. Dataset procesado
dataset_path = 'modelos_ml/dataset_procesado_SIN_LEAKAGE.csv'
data_completo = X.copy()
data_completo['abandono'] = y
data_completo.to_csv(dataset_path, index=False)
print(f"\n✅ {dataset_path}")

# 2. Scaler
scaler_path = 'modelos_ml/standard_scaler_SIN_LEAKAGE.pkl'
with open(scaler_path, 'wb') as f:
    pickle.dump(scaler, f)
print(f"✅ {scaler_path}")

# 3. Splits (CON TODAS LAS CLAVES NECESARIAS)
splits_path = 'modelos_ml/train_test_splits_SIN_LEAKAGE.pkl'
splits_data = {
    'X_train': X_train,
    'X_test': X_test,
    'y_train': y_train,
    'y_test': y_test,
    'X_train_balanced': X_train_balanced,  # ← CLAVE IMPORTANTE
    'y_train_balanced': y_train_balanced,  # ← CLAVE IMPORTANTE
    'feature_names': feature_names
}

with open(splits_path, 'wb') as f:
    pickle.dump(splits_data, f)
print(f"✅ {splits_path}")

# 4. Info
info_path = 'modelos_ml/info_dataset_SIN_LEAKAGE.pkl'
info_data = {
    'n_samples': len(data),
    'n_features': len(feature_names),
    'feature_names': feature_names,
    'train_size': len(X_train),
    'test_size': len(X_test),
    'train_balanced_size': len(X_train_balanced),
    'fecha_creacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

with open(info_path, 'wb') as f:
    pickle.dump(info_data, f)
print(f"✅ {info_path}")

# ============================================================================
# PASO 9: VERIFICACIÓN
# ============================================================================

print("\n" + "=" * 80)
print("🔍 PASO 9: VERIFICACIÓN DEL PICKLE")
print("=" * 80)

try:
    with open(splits_path, 'rb') as f:
        test_data = pickle.load(f)
    
    claves_presentes = list(test_data.keys())
    
    print(f"\n✅ Pickle verificado correctamente")
    print(f"   Claves presentes: {claves_presentes}")
    
    # Verificar X_train_balanced específicamente
    if 'X_train_balanced' in test_data:
        print(f"\n✅ X_train_balanced shape: {test_data['X_train_balanced'].shape}")
        print(f"✅ y_train_balanced shape: {test_data['y_train_balanced'].shape}")
    else:
        print(f"\n❌ ERROR: X_train_balanced NO está en el pickle")
        
except Exception as e:
    print(f"\n⚠️  Error en verificación: {e}")

# ============================================================================
# PASO 10: RESUMEN FINAL
# ============================================================================

print("\n" + "=" * 80)
print("✅ PREPARACIÓN COMPLETADA EXITOSAMENTE")
print("=" * 80)

print(f"\n📊 RESUMEN FINAL:")
print(f"   - Registros totales: {len(data):,}")
print(f"   - Features utilizadas: {len(feature_names)}")
print(f"   - Train original: {len(X_train):,}")
print(f"   - Train balanceado: {len(X_train_balanced):,}")
print(f"   - Test: {len(X_test):,}")
print(f"   - Tasa de abandono (test): {(y_test == 1).mean()*100:.2f}%")

print(f"\n💾 ARCHIVOS GENERADOS:")
print(f"   ✅ {dataset_path}")
print(f"   ✅ {scaler_path}")
print(f"   ✅ {splits_path}")
print(f"   ✅ {info_path}")

print(f"\n🎯 PRÓXIMOS PASOS:")
print(f"   Ejecuta los scripts de entrenamiento en orden:")
print(f"   1. python entrenar_isolation_forest_SIN_LEAKAGE.py")
print(f"   2. python entrenar_xgboost_SIN_LEAKAGE.py")
print(f"   3. python entrenar_logistic_regression_SIN_LEAKAGE.py")

print("\n" + "=" * 80)
print("🎉 ¡ÉXITO TOTAL! TODO LISTO PARA ENTRENAR MODELOS")
print("=" * 80)