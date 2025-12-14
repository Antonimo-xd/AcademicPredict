"""
===============================================================================
REGRESIÓN LOGÍSTICA - ENTRENAMIENTO SIN DATA LEAKAGE
===============================================================================

CONCEPTO EDUCATIVO: ¿Qué es Regresión Logística?
------------------------------------------------
A pesar del nombre "regresión", es un algoritmo de CLASIFICACIÓN.
Es el modelo más SIMPLE y CLÁSICO de Machine Learning.

ANALOGÍA EDUCATIVA: La Línea Divisoria
---------------------------------------
Imagina que tienes estudiantes en un gráfico 2D:
- Eje X: Rendimiento académico
- Eje Y: Asistencia a clases

Regresión Logística busca trazar una LÍNEA que separe:
- Estudiantes que abandonan (un lado de la línea)
- Estudiantes que continúan (otro lado de la línea)

En realidad, con 43 features, ¡es un HIPERPLANO en 43 dimensiones!

MATEMÁTICA SIMPLIFICADA:
------------------------
1. Calcula una puntuación lineal:
   z = w1*feature1 + w2*feature2 + ... + w43*feature43 + b
   
2. Aplica función sigmoide para convertir a probabilidad:
   P(abandono) = 1 / (1 + e^(-z))
   
3. Si P > 0.5 → predice "abandono"
   Si P < 0.5 → predice "no abandono"

VENTAJAS:
✅ Muy rápido de entrenar
✅ Fácil de interpretar (coeficientes = importancia)
✅ Poco propenso a overfitting
✅ Funciona bien como BASELINE (referencia)

DESVENTAJAS:
❌ Asume relaciones LINEALES (no captura patrones complejos)
❌ Menos preciso que XGBoost o redes neuronales
❌ No captura interacciones entre variables automáticamente

¿POR QUÉ LO USAMOS?
------------------
1. BASELINE: Comparar qué tan mejor es XGBoost
2. INTERPRETABILIDAD: Entender relación directa de cada variable
3. SIMPLICIDAD: Más fácil de explicar a stakeholders
4. VELOCIDAD: Predicciones en milisegundos

DIFERENCIA CLAVE vs VERSIÓN CON LEAKAGE:
----------------------------------------
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
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    roc_auc_score, 
    roc_curve,
    precision_recall_curve,
    average_precision_score
)
import joblib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Paths de archivos
TRAIN_TEST_PATH = 'modelos_ml/train_test_splits_SIN_LEAKAGE.pkl'
MODEL_OUTPUT_PATH = 'modelos_ml/logistic_regression_model_SIN_LEAKAGE.pkl'
RESULTS_DIR = 'resultados_ml/'

# Configuración del modelo
"""
EXPLICACIÓN DE HIPERPARÁMETROS:
-------------------------------

max_iter=1000:
  - Número máximo de iteraciones del optimizador
  - Regresión Logística usa optimización iterativa
  - 1000 iteraciones es suficiente para convergencia

solver='lbfgs':
  - Algoritmo de optimización
  - LBFGS = Limited-memory Broyden-Fletcher-Goldfarb-Shanno
  - Eficiente para datasets medianos/grandes
  - Alternativas: 'newton-cg', 'sag', 'saga'

class_weight='balanced':
  - Ajusta pesos automáticamente para clases desbalanceadas
  - Clase minoritaria (abandono) recibe más peso
  - Equivalente a: weight = n_samples / (n_classes * n_samples_per_class)

random_state=42:
  - Semilla para reproducibilidad
  - Afecta la inicialización del solver

penalty='l2':
  - Regularización L2 (Ridge)
  - Previene overfitting penalizando coeficientes grandes
  - L2 es la más común (suaviza coeficientes)

C=1.0:
  - Inverso de la fuerza de regularización
  - Valores pequeños = más regularización
  - Valores grandes = menos regularización
  - 1.0 es el valor por defecto (balance)
"""

LOGREG_CONFIG = {
    'max_iter': 1000,
    'solver': 'lbfgs',
    'class_weight': 'balanced',
    'random_state': 42,
    'penalty': 'l2',
    'C': 1.0,
    'n_jobs': -1
}

print("=" * 80)
print("📊 ENTRENAMIENTO: REGRESIÓN LOGÍSTICA SIN DATA LEAKAGE")
print("=" * 80)
print(f"\n📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\n📁 Cargando datos desde: {TRAIN_TEST_PATH}")

# ============================================================================
# 1. CARGAR DATOS LIMPIOS (SIN LEAKAGE)
# ============================================================================

try:
    with open(TRAIN_TEST_PATH, 'rb') as f:
        data = pickle.load(f)
    
    # Para Regresión Logística NO usamos datos balanceados con SMOTE
    # Usamos class_weight='balanced' en su lugar
    X_train = data['X_train']  # ← Datos originales (sin SMOTE)
    X_test = data['X_test']
    y_train = data['y_train']  # ← Labels originales (sin SMOTE)
    y_test = data['y_test']
    feature_names = data['feature_names']
    
    print(f"\n✅ Datos cargados exitosamente")
    print(f"\n📊 ESTADÍSTICAS DEL DATASET SIN LEAKAGE:")
    print(f"   - Features totales: {len(feature_names)}")
    print(f"   - Registros train: {X_train.shape[0]:,}")
    print(f"   - Registros test: {X_test.shape[0]:,}")
    print(f"   - Balance en train: {np.sum(y_train == 1):,} abandonos / {np.sum(y_train == 0):,} no abandonos")
    print(f"   - Balance en test: {np.sum(y_test == 1):,} abandonos / {np.sum(y_test == 0):,} no abandonos")
    print(f"   - Ratio desbalance: {np.sum(y_train == 0) / np.sum(y_train == 1):.2f}:1")
    
    print(f"\n💡 NOTA IMPORTANTE:")
    print(f"   Regresión Logística NO usa datos balanceados con SMOTE.")
    print(f"   En su lugar, usa class_weight='balanced' que ajusta pesos internamente.")
    print(f"   Esto evita 'inflar' artificialmente el dataset.")
    
except FileNotFoundError:
    print(f"\n❌ ERROR: No se encontró el archivo {TRAIN_TEST_PATH}")
    print("\n💡 SOLUCIÓN: Primero debes ejecutar preparar_datos_ml_SIN_LEAKAGE.py")
    exit(1)

# ============================================================================
# 2. ENTRENAR REGRESIÓN LOGÍSTICA
# ============================================================================

print("\n" + "=" * 80)
print("🎯 PASO 2: ENTRENAMIENTO DEL MODELO")
print("=" * 80)

print(f"\n🔧 Configuración del modelo:")
for key, value in LOGREG_CONFIG.items():
    if key != 'n_jobs':  # Omitir n_jobs en el print
        print(f"   - {key}: {value}")

"""
CONCEPTO EDUCATIVO: Proceso de entrenamiento
--------------------------------------------
Regresión Logística entrena encontrando los pesos (w1, w2, ..., w43) 
que MINIMIZAN la función de pérdida (log loss):

1. Inicializa pesos aleatoriamente
2. FOR iteración = 1 to 1000:
   a. Calcula predicciones con pesos actuales
   b. Calcula log loss (error)
   c. Calcula gradiente (dirección de mejora)
   d. Actualiza pesos en dirección del gradiente
   e. Si converge (loss no cambia) → termina
3. Devuelve pesos finales

MATEMÁTICA:
Loss = -1/N * Σ[y*log(ŷ) + (1-y)*log(1-ŷ)]
donde:
- y = etiqueta real (0 o 1)
- ŷ = probabilidad predicha

LBFGS usa aproximación de segunda derivada (más rápido que gradiente simple)
"""

logreg_model = LogisticRegression(**LOGREG_CONFIG)

print("\n⏳ Entrenando modelo de Regresión Logística...")
print("   (Esto debería tomar menos de 1 minuto)")

logreg_model.fit(X_train, y_train)

# Verificar convergencia
if logreg_model.n_iter_[0] < LOGREG_CONFIG['max_iter']:
    print(f"✅ Modelo convergió en {logreg_model.n_iter_[0]} iteraciones")
else:
    print(f"⚠️  Modelo alcanzó máximo de iteraciones ({LOGREG_CONFIG['max_iter']})")
    print("   Considera aumentar max_iter si ves este mensaje")

# ============================================================================
# 3. GENERAR PREDICCIONES
# ============================================================================

print("\n" + "=" * 80)
print("🎯 PASO 3: GENERACIÓN DE PREDICCIONES")
print("=" * 80)

# Predicciones en conjunto de test
y_pred = logreg_model.predict(X_test)
y_pred_proba = logreg_model.predict_proba(X_test)[:, 1]  # Probabilidad de abandono

print("\n📊 DISTRIBUCIÓN DE PREDICCIONES:")
print(f"   - Predichos como NO ABANDONO: {np.sum(y_pred == 0):,} ({np.sum(y_pred == 0)/len(y_pred)*100:.2f}%)")
print(f"   - Predichos como ABANDONO: {np.sum(y_pred == 1):,} ({np.sum(y_pred == 1)/len(y_pred)*100:.2f}%)")

print("\n📊 ESTADÍSTICAS DE PROBABILIDADES:")
print(f"   - Probabilidad promedio de abandono: {y_pred_proba.mean():.4f}")
print(f"   - Probabilidad mínima: {y_pred_proba.min():.4f}")
print(f"   - Probabilidad máxima: {y_pred_proba.max():.4f}")

# ============================================================================
# 4. EVALUACIÓN DEL MODELO
# ============================================================================

print("\n" + "=" * 80)
print("📈 PASO 4: EVALUACIÓN DEL MODELO")
print("=" * 80)

# Reporte de clasificación
print("\n📊 REPORTE DE CLASIFICACIÓN:")
print("\n" + classification_report(y_test, y_pred, 
                                   target_names=['No Abandono', 'Abandono'],
                                   digits=4))

# Matriz de confusión
cm = confusion_matrix(y_test, y_pred)

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
accuracy = (tp + tn) / (tp + tn + fp + fn)

# ROC-AUC
roc_auc = roc_auc_score(y_test, y_pred_proba)
avg_precision = average_precision_score(y_test, y_pred_proba)

print(f"\n🎯 MÉTRICAS CLAVE:")
print(f"   - Precision: {precision:.4f} ({precision*100:.2f}%)")
print(f"   - Recall: {recall:.4f} ({recall*100:.2f}%)")
print(f"   - F1-Score: {f1:.4f}")
print(f"   - Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"   - ROC-AUC: {roc_auc:.4f}")
print(f"   - Average Precision: {avg_precision:.4f}")

# ============================================================================
# 5. ANÁLISIS DE COEFICIENTES (FEATURE IMPORTANCE)
# ============================================================================

print("\n" + "=" * 80)
print("📊 PASO 5: ANÁLISIS DE COEFICIENTES")
print("=" * 80)

"""
CONCEPTO EDUCATIVO: Coeficientes en Regresión Logística
-------------------------------------------------------
Los coeficientes representan la IMPORTANCIA y DIRECCIÓN de cada feature:

MAGNITUD (valor absoluto):
- Coeficiente grande = feature muy importante
- Coeficiente pequeño = feature poco importante

SIGNO:
- Positivo (+): Aumenta probabilidad de abandono
  Ejemplo: coef_edad = +0.5 → Mayor edad → Más abandono
  
- Negativo (-): Disminuye probabilidad de abandono
  Ejemplo: coef_rendimiento = -0.8 → Mayor rendimiento → Menos abandono

INTERPRETACIÓN MATEMÁTICA:
Si coef_rendimiento = -0.8:
- Por cada aumento de 1 desviación estándar en rendimiento
- Las log-odds de abandono disminuyen en 0.8
- O equivalentemente, las odds se multiplican por e^(-0.8) = 0.45

IMPORTANTE:
Los datos están NORMALIZADOS (StandardScaler), por eso podemos 
comparar magnitudes directamente.
"""

# Obtener coeficientes
coefficients = logreg_model.coef_[0]

# Crear DataFrame
coef_df = pd.DataFrame({
    'feature': feature_names,
    'coefficient': coefficients,
    'abs_coefficient': np.abs(coefficients)
}).sort_values('abs_coefficient', ascending=False)

print("\n🔝 TOP 20 VARIABLES MÁS IMPORTANTES (por magnitud):\n")
print("Ranking | Variable                          | Coeficiente | Interpretación")
print("-" * 90)

for idx, row in coef_df.head(20).iterrows():
    coef_val = row['coefficient']
    interpretation = "↑ Abandono" if coef_val > 0 else "↓ Abandono"
    print(f"{coef_df.index.get_loc(idx)+1:>3}     | {row['feature']:<32} | {coef_val:>11.4f} | {interpretation}")

# Guardar coeficientes completos
coef_path = f'{RESULTS_DIR}logistic_regression_coefficients_SIN_LEAKAGE.csv'
coef_df.to_csv(coef_path, index=False)
print(f"\n✅ Coeficientes guardados: {coef_path}")

# Analizar signos
positive_coefs = coef_df[coef_df['coefficient'] > 0]
negative_coefs = coef_df[coef_df['coefficient'] < 0]

print(f"\n📊 DISTRIBUCIÓN DE COEFICIENTES:")
print(f"   - Features que AUMENTAN riesgo (+): {len(positive_coefs)}")
print(f"   - Features que DISMINUYEN riesgo (-): {len(negative_coefs)}")

print(f"\n🔝 TOP 5 FEATURES QUE MÁS AUMENTAN RIESGO:")
for idx, row in positive_coefs.head(5).iterrows():
    print(f"   • {row['feature']}: +{row['coefficient']:.4f}")

print(f"\n🔝 TOP 5 FEATURES QUE MÁS DISMINUYEN RIESGO:")
for idx, row in negative_coefs.head(5).iterrows():
    print(f"   • {row['feature']}: {row['coefficient']:.4f}")

# ============================================================================
# 6. VISUALIZACIONES
# ============================================================================

print("\n" + "=" * 80)
print("📊 PASO 6: GENERACIÓN DE VISUALIZACIONES")
print("=" * 80)

# Configurar estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# -------------------------
# 6.1. Matriz de Confusión
# -------------------------
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['No Abandono', 'Abandono'],
            yticklabels=['No Abandono', 'Abandono'],
            cbar_kws={'label': 'Número de estudiantes'},
            ax=ax)
ax.set_xlabel('Predicción', fontsize=12, fontweight='bold')
ax.set_ylabel('Valor Real', fontsize=12, fontweight='bold')
ax.set_title('Regresión Logística - Matriz de Confusión\n(SIN Data Leakage)', 
             fontsize=14, fontweight='bold', pad=20)

# Agregar métricas
metrics_text = f'Precision: {precision:.2%} | Recall: {recall:.2%} | F1: {f1:.4f} | Accuracy: {accuracy:.2%} | ROC-AUC: {roc_auc:.4f}'
plt.text(0.5, -0.15, metrics_text, ha='center', transform=ax.transAxes, fontsize=9)

plt.tight_layout()
confusion_path = f'{RESULTS_DIR}logistic_regression_confusion_matrix_SIN_LEAKAGE.png'
plt.savefig(confusion_path, dpi=300, bbox_inches='tight')
print(f"✅ Guardada: {confusion_path}")
plt.close()

# -------------------------------------
# 6.2. Coeficientes (TOP 30)
# -------------------------------------
fig, ax = plt.subplots(figsize=(12, 10))

top30 = coef_df.head(30).iloc[::-1]  # Invertir para mejor visualización

# Colorear por signo
colors = ['red' if c > 0 else 'blue' for c in top30['coefficient']]

bars = ax.barh(range(len(top30)), top30['coefficient'], color=colors, 
               edgecolor='black', alpha=0.7)
ax.set_yticks(range(len(top30)))
ax.set_yticklabels(top30['feature'], fontsize=10)
ax.set_xlabel('Coeficiente', fontsize=12, fontweight='bold')
ax.set_title('Regresión Logística - TOP 30 Coeficientes\n(SIN Data Leakage)', 
             fontsize=14, fontweight='bold', pad=20)
ax.axvline(0, color='black', linewidth=2, linestyle='-')
ax.grid(True, axis='x', alpha=0.3)

# Leyenda
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='red', alpha=0.7, label='↑ Aumenta riesgo abandono'),
    Patch(facecolor='blue', alpha=0.7, label='↓ Disminuye riesgo abandono')
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

# Agregar valores
for i, (bar, val) in enumerate(zip(bars, top30['coefficient'])):
    x_pos = val + (0.01 if val > 0 else -0.01)
    ha = 'left' if val > 0 else 'right'
    ax.text(x_pos, bar.get_y() + bar.get_height()/2, 
            f'{val:.3f}', va='center', ha=ha, fontsize=8)

plt.tight_layout()
coef_plot_path = f'{RESULTS_DIR}logistic_regression_coefficients_SIN_LEAKAGE.png'
plt.savefig(coef_plot_path, dpi=300, bbox_inches='tight')
print(f"✅ Guardada: {coef_plot_path}")
plt.close()

# -------------------
# 6.3. Curva ROC
# -------------------
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)

fig, ax = plt.subplots(figsize=(10, 8))
ax.plot(fpr, tpr, color='darkorange', lw=2, 
        label=f'Regresión Logística (AUC = {roc_auc:.4f})')
ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', 
        label='Clasificador Aleatorio (AUC = 0.50)')
ax.set_xlim([0.0, 1.0])
ax.set_ylim([0.0, 1.05])
ax.set_xlabel('False Positive Rate (FPR)', fontsize=12, fontweight='bold')
ax.set_ylabel('True Positive Rate (TPR) - Recall', fontsize=12, fontweight='bold')
ax.set_title('Regresión Logística - Curva ROC (SIN Data Leakage)', 
             fontsize=14, fontweight='bold')
ax.legend(loc="lower right", fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
roc_path = f'{RESULTS_DIR}logistic_regression_roc_curve_SIN_LEAKAGE.png'
plt.savefig(roc_path, dpi=300, bbox_inches='tight')
print(f"✅ Guardada: {roc_path}")
plt.close()

# -----------------------------
# 6.4. Precision-Recall Curve
# -----------------------------
precision_curve, recall_curve, _ = precision_recall_curve(y_test, y_pred_proba)

fig, ax = plt.subplots(figsize=(10, 8))
ax.plot(recall_curve, precision_curve, color='blue', lw=2,
        label=f'Regresión Logística (AP = {avg_precision:.4f})')
ax.axhline(y=precision, color='red', linestyle='--', lw=2,
          label=f'Precision actual = {precision:.4f}')
ax.set_xlim([0.0, 1.0])
ax.set_ylim([0.0, 1.05])
ax.set_xlabel('Recall', fontsize=12, fontweight='bold')
ax.set_ylabel('Precision', fontsize=12, fontweight='bold')
ax.set_title('Regresión Logística - Curva Precision-Recall (SIN Data Leakage)', 
             fontsize=14, fontweight='bold')
ax.legend(loc="lower left", fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
pr_path = f'{RESULTS_DIR}logistic_regression_precision_recall_SIN_LEAKAGE.png'
plt.savefig(pr_path, dpi=300, bbox_inches='tight')
print(f"✅ Guardada: {pr_path}")
plt.close()

# ----------------------------------------
# 6.5. Distribución de Probabilidades
# ----------------------------------------
fig, ax = plt.subplots(figsize=(12, 6))

abandono_probs = y_pred_proba[y_test == 1]
no_abandono_probs = y_pred_proba[y_test == 0]

ax.hist(no_abandono_probs, bins=50, alpha=0.6, label='No Abandono Real', 
        color='green', edgecolor='black')
ax.hist(abandono_probs, bins=50, alpha=0.6, label='Abandono Real', 
        color='red', edgecolor='black')

ax.axvline(0.5, color='black', linestyle='--', linewidth=2, 
          label='Umbral de decisión (0.5)')
ax.set_xlabel('Probabilidad Predicha de Abandono', fontsize=12, fontweight='bold')
ax.set_ylabel('Frecuencia', fontsize=12, fontweight='bold')
ax.set_title('Regresión Logística - Distribución de Probabilidades (SIN Data Leakage)', 
             fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
prob_path = f'{RESULTS_DIR}logistic_regression_probability_distribution_SIN_LEAKAGE.png'
plt.savefig(prob_path, dpi=300, bbox_inches='tight')
print(f"✅ Guardada: {prob_path}")
plt.close()

# ============================================================================
# 7. GUARDAR MODELO Y RESULTADOS
# ============================================================================

print("\n" + "=" * 80)
print("💾 PASO 7: GUARDAR MODELO Y RESULTADOS")
print("=" * 80)

# Guardar modelo entrenado
joblib.dump(logreg_model, MODEL_OUTPUT_PATH)
print(f"✅ Modelo guardado: {MODEL_OUTPUT_PATH}")

# Guardar resultados completos
results_data = {
    'y_test': y_test,
    'y_pred': y_pred,
    'y_pred_proba': y_pred_proba,
    'feature_names': feature_names,
    'coefficients': coef_df,
    'metrics': {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'accuracy': accuracy,
        'roc_auc': roc_auc,
        'average_precision': avg_precision,
        'confusion_matrix': cm
    },
    'config': LOGREG_CONFIG
}

results_output_path = MODEL_OUTPUT_PATH.replace('.pkl', '_results.pkl')
with open(results_output_path, 'wb') as f:
    pickle.dump(results_data, f)
print(f"✅ Resultados guardados: {results_output_path}")

# ============================================================================
# 8. RESUMEN FINAL
# ============================================================================

print("\n" + "=" * 80)
print("✅ ENTRENAMIENTO COMPLETADO - REGRESIÓN LOGÍSTICA SIN DATA LEAKAGE")
print("=" * 80)

print(f"\n📊 RESUMEN DE MÉTRICAS FINALES:")
print(f"   - Precision: {precision:.4f} ({precision*100:.2f}%)")
print(f"   - Recall: {recall:.4f} ({recall*100:.2f}%)")
print(f"   - F1-Score: {f1:.4f}")
print(f"   - Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"   - ROC-AUC: {roc_auc:.4f}")
print(f"   - Average Precision: {avg_precision:.4f}")

print(f"\n🔝 TOP 5 COEFICIENTES MÁS IMPORTANTES:")
for idx, row in coef_df.head(5).iterrows():
    direction = "↑" if row['coefficient'] > 0 else "↓"
    print(f"   {coef_df.index.get_loc(idx)+1}. {row['feature']}: {row['coefficient']:.4f} {direction}")

print(f"\n💾 ARCHIVOS GENERADOS:")
print(f"   ✅ {MODEL_OUTPUT_PATH}")
print(f"   ✅ {results_output_path}")
print(f"   ✅ {confusion_path}")
print(f"   ✅ {coef_plot_path}")
print(f"   ✅ {coef_path}")
print(f"   ✅ {roc_path}")
print(f"   ✅ {pr_path}")
print(f"   ✅ {prob_path}")

print(f"\n💡 ROL DE REGRESIÓN LOGÍSTICA:")
print(f"   ✅ BASELINE: Modelo simple para comparación")
print(f"   ✅ INTERPRETABILIDAD: Fácil de explicar a stakeholders")
print(f"   ✅ VELOCIDAD: Predicciones instantáneas")
print(f"   ✅ ROBUSTEZ: Menos propenso a overfitting")
print(f"   ")
print(f"   Aunque probablemente XGBoost tenga mejores métricas,")
print(f"   Regresión Logística es valioso para:")
print(f"   - Entender relación directa de cada variable")
print(f"   - Validar que el problema es predecible")
print(f"   - Deployment en sistemas con recursos limitados")

print("\n" + "=" * 80)
print("🎉 ¡PROCESO FINALIZADO!")
print("=" * 80)
print("\n✅ LOS 3 MODELOS HAN SIDO ENTRENADOS SIN DATA LEAKAGE")
print("\nPróximo paso: Comparar los 3 modelos y elegir el mejor para producción")