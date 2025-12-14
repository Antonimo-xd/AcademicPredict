from django.core.management.base import BaseCommand
from prototipo.models import RegistroAcademicoUniversitario
import pandas as pd
from decimal import Decimal

class Command(BaseCommand):
    help = 'Compara fila por fila el CSV contra la Base de Datos para asegurar integridad perfecta.'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Ruta al archivo CSV ultra limpio')
        parser.add_argument('--sample', type=int, default=1000, help='Número de filas aleatorias a verificar (Default: 1000)')
        parser.add_argument('--full', action='store_true', help='Verificar el archivo COMPLETO (puede tardar)')

    def handle(self, *args, **options):
        ruta_csv = options['csv_path']
        sample_size = options['sample']
        check_full = options['full']

        print(f"📂 Cargando CSV: {ruta_csv} ...")
        # Leemos todo como string para no perder precisión decimal antes de tiempo
        df = pd.read_csv(ruta_csv, sep=';', encoding='utf-8', dtype=str)
        
        total_filas = len(df)
        print(f"📊 Total filas en CSV: {total_filas}")

        if not check_full:
            print(f"🎲 Seleccionando muestra aleatoria de {sample_size} registros...")
            if sample_size > total_filas: sample_size = total_filas
            df = df.sample(n=sample_size, random_state=42)
        else:
            print("⚠️  MODO COMPLETO ACTIVADO: Esto verificará todas las filas.")

        errores = []
        aciertos = 0

        print("\n🔍 INICIANDO COMPARACIÓN CRUZADA (CSV vs DB)...\n")

        for index, row in df.iterrows():
            try:
                # 1. Identificar al estudiante y registro único
                id_est = row['Id_Estudiante']
                anio = int(row['Anio_Academico'])
                id_asig = row['Id_Asignatura']

                # Buscar en DB
                registro = RegistroAcademicoUniversitario.objects.filter(
                    estudiante__codigo_estudiante=id_est,
                    anio_academico=anio,
                    asignatura__codigo_asignatura=id_asig
                ).select_related('estudiante', 'asignatura').first()

                if not registro:
                    errores.append(f"Fila {index}: ❌ NO EXISTE EN DB - Estudiante: {id_est}, Asignatura: {id_asig}")
                    continue

                # 2. DEFINIR REGLAS DE COMPARACIÓN
                # (Campo CSV, Campo Modelo DB, Tipo de Dato)
                comparaciones = [
                    # Estudiante
                    ('Estado_Abandono', registro.estudiante.estado_abandono, 'str'),
                    ('Dedicacion_Estudios', registro.estudiante.dedicacion_estudios, 'str'),
                    ('Nota_Selectividad_Total', registro.estudiante.nota_selectividad_total, 'decimal'),
                    
                    # Registro - Créditos Clave
                    ('Creditos_Matriculados_Total_Anio', registro.creditos_matriculados_total_anio, 'decimal'),
                    ('Creditos_Aprobados_Total_Por_Periodo', registro.creditos_aprobados_total_anio, 'decimal'),
                    ('Creditos_Matriculados_Movilidad', registro.creditos_matriculados_movilidad, 'decimal'),
                    
                    # Registro - Rendimiento
                    ('Rendimiento_Academico_Total_Anio', registro.rendimiento_total_anio, 'decimal'),
                    ('Nota_Final_Asignatura', registro.nota_final_asignatura, 'decimal'),

                ]

                fila_ok = True
                
                for col_csv, val_db, tipo in comparaciones:
                    val_csv_raw = row.get(col_csv, '')
                    
                    # Normalizar valor CSV
                    if tipo == 'decimal':
                        val_csv = self.limpiar_decimal(val_csv_raw)
                        # Normalizar valor DB (Decimal a float para comparar o Decimal vs Decimal)
                        if val_db is None: val_db = Decimal('0.00')
                        
                        # Comparación con tolerancia mínima para flotantes
                        if abs(val_csv - val_db) > Decimal('0.01'):
                            errores.append(f"Fila {index} ({col_csv}): CSV='{val_csv}' != DB='{val_db}'")
                            fila_ok = False
                            
                    elif tipo == 'str':
                        val_csv = str(val_csv_raw).strip()
                        val_db = str(val_db).strip()
                        if val_csv != val_db:
                            errores.append(f"Fila {index} ({col_csv}): CSV='{val_csv}' != DB='{val_db}'")
                            fila_ok = False

                if fila_ok:
                    aciertos += 1

                if index % 100 == 0:
                    print(f"   Verificando... {aciertos} OK | {len(errores)} Errores", end='\r')

            except Exception as e:
                errores.append(f"Fila {index}: Excepción {str(e)}")

        print("\n\n" + "="*60)
        print("📊 RESULTADO FINAL DE LA VALIDACIÓN")
        print("="*60)
        print(f"✅ Registros idénticos: {aciertos}")
        print(f"❌ Discrepancias encontradas: {len(errores)}")
        
        if len(errores) > 0:
            print("\n⚠️  MUESTRA DE ERRORES (Primeros 5):")
            for err in errores[:5]:
                print(f"   - {err}")
            print(f"\n(Y {len(errores)-5} errores más...)")
        else:
            print("\n🎉 ¡FELICIDADES! La base de datos es un espejo exacto del CSV.")

    def limpiar_decimal(self, valor):
        """Convierte string '5,5' a Decimal('5.5')"""
        if pd.isna(valor) or valor == '' or valor == 'nan': return Decimal('0.00')
        return Decimal(str(valor).replace(',', '.'))