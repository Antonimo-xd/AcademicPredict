"""
===============================================================================
ISOLATION FOREST - ENTRENAMIENTO SIN DATA LEAKAGE
===============================================================================

CONCEPTO EDUCATIVO: ¿Qué es Isolation Forest?
----------------------------------------------
Isolation Forest es un algoritmo de DETECCIÓN DE ANOMALÍAS, no de predicción
directa. No predice "abandonará o no", sino que identifica estudiantes con
comportamiento ATÍPICO.

INTUICIÓN:
Imagina un bosque de árboles de decisión. Los estudiantes "normales" están
todos juntos (necesitas muchas preguntas para aislarlos). Los estudiantes
"raros" están solos (pocas preguntas los aíslan).

EJEMPLO PRÁCTICO:
- Estudiante normal: Notas medias + asistencia media + comportamiento típico
  → Necesitas ~10 preguntas para aislarlo del grupo
  
- Estudiante anómalo: Notas altas + CERO asistencia LMS + comportamiento extraño
  → Necesitas solo 2-3 preguntas para aislarlo
  → ¡ALERTA! Posible caso de riesgo

APLICACIÓN EN NUESTRO PROYECTO:
-------------------------------
Usamos Isolation Forest como PRIMERA LÍNEA de detección:
1. Identifica estudiantes con patrones atípicos
2. Genera "anomaly scores" (puntajes de anomalía)
3. Estos scores se pueden usar solos O combinarse con otros modelos

DIFERENCIA CLAVE vs VERSIÓN CON LEAKAGE:
---------------------------------------
❌ ANTES: 66 features (incluía información del futuro)
✅ AHORA: 43 features (solo información disponible PRE-deserción)

Autor: Bastián
Fecha: Noviembre 2024
Proyecto: AcademicPredict
===============================================================================
"""

import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Paths de archivos
TRAIN_TEST_PATH = 'modelos_ml/train_test_splits_SIN_LEAKAGE.pkl'
MODEL_OUTPUT_PATH = 'modelos_ml/isolation_forest_model_SIN_LEAKAGE.pkl'
RESULTS_DIR = 'resultados_ml/'

# Configuración del modelo
"""
EXPLICACIÓN DE HIPERPARÁMETROS:
-------------------------------
- contamination: % esperado de anomalías (estudiantes en riesgo)
  En nuestro caso: 0.058 (5.8%) porque esa es la tasa histórica de deserción
  
- n_estimators: Número de árboles en el "bosque"
  Más árboles = más preciso pero más lento
  100 es un buen balance
  
- max_samples: Cuántas muestras usa cada árbol
  'auto' = usa 256 muestras automáticamente (eficiente)
  
- random_state: Semilla para reproducibilidad
  42 es una convención (referencia a "Guía del Autoestopista Galáctico")
"""
ISO_FOREST_CONFIG = {
    'contamination': 0.058,  # 5.8% tasa de deserción
    'n_estimators': 100,
    'max_samples': 'auto',
    'random_state': 42,
    'n_jobs': -1  # Usa todos los cores del CPU
}

print("=" * 80)
print("🌲 ENTRENAMIENTO: ISOLATION FOREST SIN DATA LEAKAGE")
print("=" * 80)
print(f"\n📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\n📁 Cargando datos desde: {TRAIN_TEST_PATH}")

# ============================================================================
# 1. CARGAR DATOS LIMPIOS (SIN LEAKAGE)
# ============================================================================

"""
CONCEPTO EDUCATIVO: ¿Por qué cargar pickle?
-------------------------------------------
Los datos ya fueron:
1. Limpiados (sin leakage)
2. Normalizados con StandardScaler
3. Divididos en train/test con stratify
4. Balanceados con SMOTE (solo train)

Cargar el pickle nos ahorra repetir todo ese proceso.
"""

try:
    with open(TRAIN_TEST_PATH, 'rb') as f:
        data = pickle.load(f)
    
    X_train = data['X_train_balanced']  # Ya balanceado con SMOTE
    X_test = data['X_test']
    y_train = data['y_train_balanced']
    y_test = data['y_test']
    feature_names = data['feature_names']
    
    print(f"\n✅ Datos cargados exitosamente")
    print(f"\n📊 ESTADÍSTICAS DEL DATASET SIN LEAKAGE:")
    print(f"   - Features totales: {len(feature_names)}")
    print(f"   - Registros train: {X_train.shape[0]:,}")
    print(f"   - Registros test: {X_test.shape[0]:,}")
    print(f"   - Balance en train: {np.sum(y_train == 1):,} abandonos / {np.sum(y_train == 0):,} no abandonos")
    print(f"   - Balance en test: {np.sum(y_test == 1):,} abandonos / {np.sum(y_test == 0):,} no abandonos")
    
except FileNotFoundError:
    print(f"\n❌ ERROR: No se encontró el archivo {TRAIN_TEST_PATH}")
    print("\n💡 SOLUCIÓN: Primero debes ejecutar preparar_datos_ml_SIN_LEAKAGE.py")
    exit(1)

# ============================================================================
# 2. ENTRENAR ISOLATION FOREST
# ============================================================================

print("\n" + "=" * 80)
print("🎯 PASO 2: ENTRENAMIENTO DEL MODELO")
print("=" * 80)

print(f"\n🔧 Configuración del modelo:")
for key, value in ISO_FOREST_CONFIG.items():
    print(f"   - {key}: {value}")

"""
CONCEPTO EDUCATIVO: ¿Cómo entrena Isolation Forest?
---------------------------------------------------
1. Construye 100 árboles de decisión aleatorios
2. Cada árbol hace splits aleatorios en las features
3. Cuenta cuántos splits necesita para aislar cada estudiante
4. Estudiantes fáciles de aislar = ANOMALÍAS (posibles desertores)
5. Estudiantes difíciles de aislar = NORMALES

MATEMÁTICA SIMPLIFICADA:
- Anomaly Score = 2^(-profundidad_promedio / c)
- Donde c = constante de normalización
- Score cercano a 1 = Anomalía
- Score cercano a 0 = Normal
"""

iso_forest = IsolationForest(**ISO_FOREST_CONFIG)

print("\n⏳ Entrenando modelo (esto puede tomar unos minutos)...")
iso_forest.fit(X_train)

print("✅ Modelo entrenado exitosamente")

# ============================================================================
# 3. GENERAR PREDICCIONES Y ANOMALY SCORES
# ============================================================================

print("\n" + "=" * 80)
print("🎯 PASO 3: GENERACIÓN DE PREDICCIONES")
print("=" * 80)

"""
CONCEPTO EDUCATIVO: Diferencia entre predict() y score_samples()
----------------------------------------------------------------
- predict(): Devuelve 1 (normal) o -1 (anomalía) → Clasificación binaria
- score_samples(): Devuelve score continuo → Más información

Nosotros usaremos ambos:
- predict() para métricas de clasificación
- score_samples() para ranking de riesgo
"""

# Predicciones en conjunto de test
y_pred = iso_forest.predict(X_test)
anomaly_scores = iso_forest.score_samples(X_test)

# Convertir predicciones: -1 (anomalía) → 1 (abandono), 1 (normal) → 0 (no abandono)
y_pred_binary = np.where(y_pred == -1, 1, 0)

print("\n📊 DISTRIBUCIÓN DE PREDICCIONES:")
print(f"   - Predichos como NORMALES: {np.sum(y_pred_binary == 0):,} ({np.sum(y_pred_binary == 0)/len(y_pred_binary)*100:.2f}%)")
print(f"   - Predichos como ANOMALÍAS: {np.sum(y_pred_binary == 1):,} ({np.sum(y_pred_binary == 1)/len(y_pred_binary)*100:.2f}%)")

# ============================================================================
# 4. EVALUACIÓN DEL MODELO
# ============================================================================

print("\n" + "=" * 80)
print("📈 PASO 4: EVALUACIÓN DEL MODELO")
print("=" * 80)

"""
CONCEPTO EDUCATIVO: Métricas para detección de anomalías
--------------------------------------------------------
Como Isolation Forest no fue entrenado supervisadamente,
sus métricas serán DIFERENTES a XGBoost:

- Precision: De los que marcamos como anomalías, ¿cuántos realmente lo son?
- Recall: De todos los que realmente son anomalías, ¿cuántos detectamos?
- F1-Score: Balance entre precision y recall

INTERPRETACIÓN ESPERADA:
- Precision ~60-70%: 6-7 de cada 10 alertas son correctas
- Recall ~50-60%: Detectamos 5-6 de cada 10 desertores reales
- Esto es NORMAL para detección no supervisada
"""

# Reporte de clasificación
print("\n📊 REPORTE DE CLASIFICACIÓN:")
print("\n" + classification_report(y_test, y_pred_binary, 
                                   target_names=['No Abandono', 'Abandono'],
                                   digits=4))

# Matriz de confusión
cm = confusion_matrix(y_test, y_pred_binary)

print("📊 MATRIZ DE CONFUSIÓN:")
print("\n                Predicho")
print("                No Abandono  |  Abandono")
print("         " + "-" * 40)
print(f"Real No  |     {cm[0][0]:>6,}     |  {cm[0][1]:>6,}")
print(f"Real Sí  |     {cm[1][0]:>6,}     |  {cm[1][1]:>6,}")

# Calcular métricas individuales
tn, fp, fn, tp = cm.ravel()
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print(f"\n🎯 MÉTRICAS CLAVE:")
print(f"   - Precision: {precision:.4f} ({precision*100:.2f}%)")
print(f"   - Recall: {recall:.4f} ({recall*100:.2f}%)")
print(f"   - F1-Score: {f1:.4f}")

# ============================================================================
# 5. VISUALIZACIONES
# ============================================================================

print("\n" + "=" * 80)
print("📊 PASO 5: GENERACIÓN DE VISUALIZACIONES")
print("=" * 80)

# Configurar estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# -------------------------
# 5.1. Matriz de Confusión
# -------------------------
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['No Abandono', 'Abandono'],
            yticklabels=['No Abandono', 'Abandono'],
            cbar_kws={'label': 'Número de estudiantes'},
            ax=ax)
ax.set_xlabel('Predicción', fontsize=12, fontweight='bold')
ax.set_ylabel('Valor Real', fontsize=12, fontweight='bold')
ax.set_title('Isolation Forest - Matriz de Confusión\n(SIN Data Leakage)', 
             fontsize=14, fontweight='bold', pad=20)

# Agregar métricas en el título
plt.text(0.5, -0.15, f'Precision: {precision:.2%} | Recall: {recall:.2%} | F1: {f1:.4f}',
         ha='center', transform=ax.transAxes, fontsize=10)

plt.tight_layout()
confusion_path = f'{RESULTS_DIR}isolation_forest_confusion_matrix_SIN_LEAKAGE.png'
plt.savefig(confusion_path, dpi=300, bbox_inches='tight')
print(f"✅ Guardada: {confusion_path}")
plt.close()

# ----------------------------------
# 5.2. Distribución de Anomaly Scores
# ----------------------------------
"""
CONCEPTO EDUCATIVO: Interpretación de Anomaly Scores
----------------------------------------------------
- Scores NEGATIVOS (más negativos = más anómalos)
- Score ~ -0.5 a 0: Estudiantes muy anómalos (alto riesgo)
- Score ~ 0 a 0.2: Estudiantes normales (bajo riesgo)

Esto nos permite:
1. Clasificar binariamente (anomalía sí/no)
2. RANKING de riesgo (quién es MÁS anómalo)
"""

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Distribución general
axes[0].hist(anomaly_scores, bins=50, edgecolor='black', alpha=0.7, color='steelblue')
axes[0].axvline(anomaly_scores.mean(), color='red', linestyle='--', 
                linewidth=2, label=f'Media: {anomaly_scores.mean():.4f}')
axes[0].set_xlabel('Anomaly Score', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Frecuencia', fontsize=12, fontweight='bold')
axes[0].set_title('Distribución de Anomaly Scores', fontsize=14, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Distribución por clase real
abandono_scores = anomaly_scores[y_test == 1]
no_abandono_scores = anomaly_scores[y_test == 0]

axes[1].hist(no_abandono_scores, bins=30, alpha=0.6, label='No Abandono', 
             color='green', edgecolor='black')
axes[1].hist(abandono_scores, bins=30, alpha=0.6, label='Abandono Real', 
             color='red', edgecolor='black')
axes[1].axvline(abandono_scores.mean(), color='darkred', linestyle='--', 
                linewidth=2, label=f'Media Abandonos: {abandono_scores.mean():.4f}')
axes[1].axvline(no_abandono_scores.mean(), color='darkgreen', linestyle='--', 
                linewidth=2, label=f'Media No Abandonos: {no_abandono_scores.mean():.4f}')
axes[1].set_xlabel('Anomaly Score', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Frecuencia', fontsize=12, fontweight='bold')
axes[1].set_title('Anomaly Scores por Clase Real', fontsize=14, fontweight='bold')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.suptitle('Isolation Forest - Análisis de Anomaly Scores (SIN Data Leakage)',
             fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
scores_path = f'{RESULTS_DIR}isolation_forest_scores_SIN_LEAKAGE.png'
plt.savefig(scores_path, dpi=300, bbox_inches='tight')
print(f"✅ Guardada: {scores_path}")
plt.close()

# ============================================================================
# 6. GUARDAR MODELO
# ============================================================================

print("\n" + "=" * 80)
print("💾 PASO 6: GUARDAR MODELO")
print("=" * 80)

# Guardar modelo entrenado
joblib.dump(iso_forest, MODEL_OUTPUT_PATH)
print(f"✅ Modelo guardado: {MODEL_OUTPUT_PATH}")

# Guardar también los scores para análisis posterior
scores_data = {
    'anomaly_scores': anomaly_scores,
    'y_test': y_test,
    'y_pred': y_pred_binary,
    'feature_names': feature_names,
    'metrics': {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'confusion_matrix': cm
    }
}

scores_output_path = MODEL_OUTPUT_PATH.replace('.pkl', '_scores.pkl')
with open(scores_output_path, 'wb') as f:
    pickle.dump(scores_data, f)
print(f"✅ Scores guardados: {scores_output_path}")

# ============================================================================
# 7. RESUMEN FINAL
# ============================================================================

print("\n" + "=" * 80)
print("✅ ENTRENAMIENTO COMPLETADO - ISOLATION FOREST SIN DATA LEAKAGE")
print("=" * 80)

print(f"\n📊 RESUMEN DE MÉTRICAS:")
print(f"   - Precision: {precision:.4f} ({precision*100:.2f}%)")
print(f"   - Recall: {recall:.4f} ({recall*100:.2f}%)")
print(f"   - F1-Score: {f1:.4f}")
print(f"   - Anomalías detectadas: {np.sum(y_pred_binary == 1):,} / {len(y_pred_binary):,}")

print(f"\n💾 ARCHIVOS GENERADOS:")
print(f"   ✅ {MODEL_OUTPUT_PATH}")
print(f"   ✅ {scores_output_path}")
print(f"   ✅ {confusion_path}")
print(f"   ✅ {scores_path}")

print(f"\n💡 INTERPRETACIÓN:")
print(f"   Este modelo actúa como PRIMERA LÍNEA de detección.")
print(f"   Identifica estudiantes con patrones atípicos que podrían estar en riesgo.")
print(f"   Los anomaly scores pueden usarse para:")
print(f"   - Ranking de prioridad de intervención")
print(f"   - Combinación con otros modelos (ensemble)")
print(f"   - Alertas tempranas automáticas")

print("\n" + "=" * 80)
print("🎉 ¡PROCESO FINALIZADO!")
print("=" * 80)