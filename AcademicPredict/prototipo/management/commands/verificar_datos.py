#script para verificar la calidad de los datos en la base de datos y mide los porcentajes

from django.core.management.base import BaseCommand
from django.db.models import Count, Avg, Min, Max, Q

# Importamos tus modelos
from prototipo.models import (
    CarreraUniversitaria,
    EstudianteUniversitario,
    AsignaturaUniversitaria,
    RegistroAcademicoUniversitario
)

class Command(BaseCommand):
    help = 'Realiza una auditoría completa de calidad de datos en la base de datos universitaria.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🔍 INICIANDO AUDITORÍA DE CALIDAD DE DATOS...\n'))

        modelos_a_verificar = [
            CarreraUniversitaria,
            AsignaturaUniversitaria,
            EstudianteUniversitario,
            RegistroAcademicoUniversitario
        ]

        for modelo in modelos_a_verificar:
            self.analizar_modelo(modelo)

        self.stdout.write(self.style.SUCCESS('\n✨ AUDITORÍA FINALIZADA ✨\n'))

    def analizar_modelo(self, modelo):
        nombre_modelo = modelo._meta.verbose_name_plural
        total_registros = modelo.objects.count()

        print("="*80)
        print(f"📊 MODELO: {nombre_modelo.upper()}")
        print(f"   Total de filas: {total_registros:,}")
        print("="*80)

        if total_registros == 0:
            self.stdout.write(self.style.WARNING("   ⚠️  TABLA VACÍA - Salteando análisis.\n"))
            return

        # Iterar sobre todos los campos del modelo
        for campo in modelo._meta.get_fields():
            if campo.many_to_many or campo.one_to_many:
                continue  # Saltamos relaciones inversas

            nombre_campo = campo.name
            tipo_campo = campo.get_internal_type()
            
            # --- 1. ANÁLISIS DE COMPLETITUD (NULOS/VACÍOS) ---
            # Calculamos cuántos valores NO son nulos o vacíos
            filtro_vacio = Q(**{f"{nombre_campo}__isnull": True})
            
            # Para campos de texto, también verificar cadena vacía
            if tipo_campo in ['CharField', 'TextField']:
                filtro_vacio |= Q(**{f"{nombre_campo}": ''})

            nulos = modelo.objects.filter(filtro_vacio).count()
            llenos = total_registros - nulos
            porcentaje_lleno = (llenos / total_registros) * 100

            # Indicador visual de salud
            icono_salud = "✅" if porcentaje_lleno > 95 else "⚠️" if porcentaje_lleno > 70 else "❌"
            
            print(f"\n🔹 Campo: {nombre_campo} ({tipo_campo})")
            print(f"   Salud: {icono_salud} {porcentaje_lleno:.2f}% completado ({llenos:,} registros)")

            # --- 2. ANÁLISIS DE DISTRIBUCIÓN (CATEGÓRICOS/BOOLEANOS) ---
            if tipo_campo in ['CharField', 'BooleanField', 'IntegerField'] and not nombre_campo.startswith('id_') and 'anio' not in nombre_campo:
                # Si tiene pocas variaciones únicas (ej: Campus, Sexo, Abandono), mostramos distribución
                distinct_count = modelo.objects.values(nombre_campo).distinct().count()
                
                if distinct_count < 20: # Solo si hay menos de 20 categorías únicas
                    print(f"   Distribución de valores:")
                    top_valores = modelo.objects.values(nombre_campo).annotate(total=Count('id')).order_by('-total')
                    for val in top_valores:
                        pct = (val['total'] / total_registros) * 100
                        v_str = str(val[nombre_campo])
                        if v_str == '': v_str = '(Vacío)'
                        print(f"     • {v_str:<25}: {val['total']:,} ({pct:.1f}%)")

            # --- 3. ANÁLISIS NUMÉRICO (DECIMALES/ENTEROS) ---
            if tipo_campo in ['DecimalField', 'IntegerField', 'FloatField']:
                # Ignoramos IDs y claves foráneas numéricas
                if not nombre_campo.endswith('_id') and 'anio' not in nombre_campo:
                    stats = modelo.objects.aggregate(
                        min_val=Min(nombre_campo),
                        max_val=Max(nombre_campo),
                        avg_val=Avg(nombre_campo),
                        ceros=Count('id', filter=Q(**{f"{nombre_campo}": 0}))
                    )
                    
                    print(f"   Estadísticas:")
                    print(f"     • Rango: [{stats['min_val']} - {stats['max_val']}]")
                    print(f"     • Promedio: {stats['avg_val']:.2f}")
                    
                    # Alerta de ceros masivos (útil para detectar si la importación falló y dejó todo en 0)
                    pct_ceros = (stats['ceros'] / total_registros) * 100
                    if pct_ceros > 90:
                        print(f"     ⚠️ ALERTA: {pct_ceros:.1f}% de los valores son CERO. ¿Error de importación?")
        
        print("\n")