#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DIAGNÓSTICO DE DATA LEAKAGE
============================

📚 EXPLICACIÓN EDUCATIVA:

Data Leakage ocurre cuando usamos información del FUTURO para predecir el PRESENTE.

EJEMPLO:
- Queremos predecir abandono en 2021
- Pero usamos "créditos totales acumulados" que incluye datos de 2022-2023
- El modelo aprende que "pocos créditos = abandono"
- ¡Pero esos créditos son BAJOS porque ya abandonó! (causalidad inversa)

REGLA DE ORO:
Solo usar información disponible ANTES del punto de predicción.
"""

import pickle
import pandas as pd
import numpy as np

print("="*80)
print("🔍 DIAGNÓSTICO DE DATA LEAKAGE")
print("="*80)

# ================================================================
# 1. CARGAR FEATURE IMPORTANCE
# ================================================================

print("\n📊 Cargando resultados de XGBoost...")

with open('modelos_ml/xgboost_results.pkl', 'rb') as f:
    results = pickle.load(f)

importance_df = results['feature_importance']

print(f"✅ {len(importance_df)} features analizadas")

# ================================================================
# 2. CLASIFICAR VARIABLES POR RIESGO DE LEAKAGE
# ================================================================

print("\n🚨 CLASIFICACIÓN DE VARIABLES:")
print("="*80)

# Variables con ALTO RIESGO de data leakage
ALTO_RIESGO = [
    'tiene_impagos',                    # ¿Registrado después del abandono?
    'progreso_carrera',                 # Calculado con créditos post-abandono
    'creditos_apro_titulo_global',      # Total histórico (incluye futuro)
    'creditos_pend_titulo_global',      # Calculado al final de la carrera
    'creditos_apro_total',              # Agregado histórico
    'rendimiento_semestre2',            # Podría ser el semestre de abandono
    'tasa_exito_acumulada',             # Feature derivada de totales
]

# Variables con RIESGO MEDIO
MEDIO_RIESGO = [
    'creditos_apro_anio1',              # OK si es año previo, NO si es año actual
    'creditos_apro_anio2',
    'creditos_apro_anio3',
    'creditos_apro_anio4',
    'creditos_apro_anio5',
    'creditos_apro_anio6',
    'anios_desde_ingreso',              # OK pero podría correlacionar con abandono tardío
]

# Variables SEGURAS (información pre-matrícula)
BAJO_RIESGO = [
    'anio_ingreso',
    'nota10',
    'nota14',
    'tipo_acceso_*',                    # Todas las dummies de tipo_acceso
    'nivel_educativo_padre',
    'nivel_educativo_madre',
    'dedicacion_estudios',
    'es_desplazado',
]

# ================================================================
# 3. ANALIZAR TOP FEATURES
# ================================================================

print("\n🏆 TOP 20 FEATURES CON CLASIFICACIÓN DE RIESGO:")
print("-"*80)

for idx, row in importance_df.head(20).iterrows():
    feature = row['Feature']
    importance = row['Importance']
    
    # Clasificar riesgo
    if feature in ALTO_RIESGO:
        riesgo = "🔴 ALTO"
    elif feature in MEDIO_RIESGO:
        riesgo = "🟡 MEDIO"
    elif any(feature.startswith(safe) for safe in ['tipo_acceso_', 'nivel_']):
        riesgo = "🟢 BAJO"
    else:
        riesgo = "⚪ REVISAR"
    
    print(f"{idx+1:2d}. {feature:40s} | {importance:.4f} | {riesgo}")

# ================================================================
# 4. CONTEO POR CATEGORÍA DE RIESGO
# ================================================================

print("\n📊 RESUMEN DE RIESGOS:")
print("-"*80)

alto_count = 0
medio_count = 0
bajo_count = 0
revisar_count = 0

for feature in importance_df['Feature']:
    if feature in ALTO_RIESGO:
        alto_count += 1
    elif feature in MEDIO_RIESGO:
        medio_count += 1
    elif any(feature.startswith(safe) for safe in ['tipo_acceso_', 'nivel_']):
        bajo_count += 1
    else:
        revisar_count += 1

print(f"🔴 ALTO RIESGO:   {alto_count:3d} features")
print(f"🟡 RIESGO MEDIO:  {medio_count:3d} features")
print(f"🟢 BAJO RIESGO:   {bajo_count:3d} features")
print(f"⚪ A REVISAR:     {revisar_count:3d} features")

# ================================================================
# 5. IMPACTO ACUMULADO DE VARIABLES DE ALTO RIESGO
# ================================================================

print("\n🔍 IMPACTO DE VARIABLES DE ALTO RIESGO:")
print("-"*80)

# Filtrar variables de alto riesgo en el top
alto_riesgo_top = importance_df[importance_df['Feature'].isin(ALTO_RIESGO)]

importancia_total_alto_riesgo = alto_riesgo_top['Importance'].sum()
importancia_total = importance_df['Importance'].sum()

porcentaje_alto_riesgo = (importancia_total_alto_riesgo / importancia_total) * 100

print(f"Importancia acumulada de variables de ALTO RIESGO: {porcentaje_alto_riesgo:.2f}%")
print(f"\n💡 INTERPRETACIÓN:")
if porcentaje_alto_riesgo > 30:
    print("   🚨 CRÍTICO: Más del 30% de la importancia viene de variables sospechosas")
    print("   🚨 El modelo está haciendo 'trampa' con información del futuro")
    print("   🚨 Los resultados (99.76% accuracy) NO son generalizables")
elif porcentaje_alto_riesgo > 15:
    print("   ⚠️ MODERADO: 15-30% de importancia en variables sospechosas")
    print("   ⚠️ El modelo tiene sesgo significativo")
elif porcentaje_alto_riesgo > 5:
    print("   ⚠️ LEVE: 5-15% de importancia en variables sospechosas")
    print("   ⚠️ Revisar definición temporal de estas variables")
else:
    print("   ✅ ACEPTABLE: <5% de importancia en variables sospechosas")

# ================================================================
# 6. VARIABLES ESPECÍFICAS A REVISAR
# ================================================================

print("\n🔍 ANÁLISIS DETALLADO DE VARIABLES PROBLEMÁTICAS:")
print("="*80)

problemas = {
    'tiene_impagos': {
        'importancia': importance_df[importance_df['Feature'] == 'tiene_impagos']['Importance'].values[0] if 'tiene_impagos' in importance_df['Feature'].values else 0,
        'problema': 'Impagos suelen registrarse DESPUÉS del abandono definitivo',
        'solucion': 'Usar solo impagos registrados ANTES del período de predicción'
    },
    'progreso_carrera': {
        'importancia': importance_df[importance_df['Feature'] == 'progreso_carrera']['Importance'].values[0] if 'progreso_carrera' in importance_df['Feature'].values else 0,
        'problema': 'Calculado con créditos_apro_titulo_global (incluye toda la carrera)',
        'solucion': 'Calcular progreso solo hasta el año N-1 al predecir año N'
    },
    'creditos_apro_titulo_global': {
        'importancia': importance_df[importance_df['Feature'] == 'creditos_apro_titulo_global']['Importance'].values[0] if 'creditos_apro_titulo_global' in importance_df['Feature'].values else 0,
        'problema': 'Acumula TODOS los créditos de la carrera (incluye futuro)',
        'solucion': 'Usar solo créditos acumulados hasta año anterior'
    }
}

for var, info in problemas.items():
    if info['importancia'] > 0:
        print(f"\n🔴 {var}")
        print(f"   Importancia: {info['importancia']:.4f} ({(info['importancia']/importancia_total)*100:.2f}%)")
        print(f"   Problema: {info['problema']}")
        print(f"   Solución: {info['solucion']}")

# ================================================================
# 7. RECOMENDACIONES
# ================================================================

print("\n" + "="*80)
print("💡 RECOMENDACIONES PARA TU TESIS")
print("="*80)

print("""
🎯 PASOS A SEGUIR:

1. **RECONOCER EL PROBLEMA EN LA TESIS:**
   - "Los resultados iniciales mostraron métricas sospechosamente altas (99.76%)"
   - "Análisis posterior reveló data leakage en variables temporales"
   - "Se procedió a reentrenar eliminando variables con información futura"

2. **VARIABLES A ELIMINAR O CORREGIR:**
   🔴 ELIMINAR COMPLETAMENTE:
      • tiene_impagos (22.50% importancia)
      • creditos_apro_titulo_global (2.53%)
      • creditos_pend_titulo_global (2.18%)
      • tasa_exito_acumulada (derivada de totales)
   
   🟡 RECALCULAR CON VENTANA TEMPORAL:
      • progreso_carrera → usar solo créditos hasta año N-1
      • creditos_apro_total → solo hasta año previo
      • rendimiento_semestre2 → solo si ya ocurrió antes de predicción

3. **MÉTRICAS ESPERADAS DESPUÉS DE CORRECCIÓN:**
   - Accuracy: 70-85% (realista)
   - Precision: 60-75%
   - Recall: 55-70%
   - F1-Score: 60-75%
   
4. **VALOR PARA LA TESIS:**
   ✅ Demuestra pensamiento crítico
   ✅ Muestra comprensión de conceptos ML
   ✅ Proceso iterativo (detectar problema → corregir → validar)

5. **CREAR SCRIPT DE LIMPIEZA:**
   - preparar_datos_ml_SIN_LEAKAGE.py
   - Filtrar variables problemáticas
   - Reentrenar todos los modelos

📚 APRENDIZAJE CLAVE:
"En Machine Learning, métricas PERFECTAS (>98%) suelen indicar un error,
no un éxito. La capacidad de detectar y corregir data leakage es una
habilidad fundamental de un científico de datos."
""")

print("\n" + "="*80)
print("🎯 SIGUIENTE PASO: Crear preparar_datos_ml_SIN_LEAKAGE.py")
print("="*80)

# ================================================================
# 8. GUARDAR DIAGNÓSTICO
# ================================================================

print("\n💾 Guardando diagnóstico...")

diagnostico = {
    'alto_riesgo_features': ALTO_RIESGO,
    'medio_riesgo_features': MEDIO_RIESGO,
    'porcentaje_alto_riesgo': porcentaje_alto_riesgo,
    'top_problematicas': alto_riesgo_top,
    'recomendacion': 'REENTRENAR sin variables de alto riesgo'
}

with open('resultados_ml/diagnostico_data_leakage.pkl', 'wb') as f:
    pickle.dump(diagnostico, f)

print("✅ Diagnóstico guardado: resultados_ml/diagnostico_data_leakage.pkl")

# Guardar también como CSV para fácil revisión
diagnostico_csv = importance_df.copy()
diagnostico_csv['Riesgo_Leakage'] = diagnostico_csv['Feature'].apply(
    lambda x: 'ALTO' if x in ALTO_RIESGO 
    else 'MEDIO' if x in MEDIO_RIESGO
    else 'BAJO' if any(x.startswith(s) for s in ['tipo_acceso_', 'nivel_'])
    else 'REVISAR'
)

diagnostico_csv.to_csv('resultados_ml/diagnostico_features.csv', index=False)
print("✅ Detalles guardados: resultados_ml/diagnostico_features.csv")

print("\n" + "="*80)
print("✅ DIAGNÓSTICO COMPLETADO")
print("="*80)