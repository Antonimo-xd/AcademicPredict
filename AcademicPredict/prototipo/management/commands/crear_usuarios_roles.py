"""
Comando Django para crear usuarios de prueba del sistema de roles.
AcademicPredict - Bastián González

UBICACIÓN: prototipo/management/commands/crear_usuarios_roles.py

USO:
    python manage.py crear_usuarios_roles
    python manage.py crear_usuarios_roles --limpiar
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from prototipo.models import PerfilUsuario, CarreraUniversitaria


class Command(BaseCommand):
    help = 'Crea usuarios de prueba con diferentes roles para el sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Elimina usuarios de prueba existentes antes de crear nuevos'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('CREACIÓN DE USUARIOS DE PRUEBA - AcademicPredict'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        if options['limpiar']:
            self._limpiar_usuarios()
        
        carreras = self._obtener_carreras()
        
        usuarios_creados = 0
        usuarios_actualizados = 0
        
        # Lista de usuarios a crear
        usuarios = [
            # (username, email, first_name, last_name, rol, carrera_index)
            ('admin_prueba', 'admin@academicpredict.cl', 'Carlos', 'Administrador', 'admin', None),
            ('coord_general', 'coordinador1@academicpredict.cl', 'María', 'Coordinadora', 'coordinador', None),
            ('coord_academico', 'coordinador2@academicpredict.cl', 'Pedro', 'Académico', 'coordinador', None),
            ('coord_ingenieria', 'coord.ing@academicpredict.cl', 'Ana', 'Ingeniería', 'coordinador_carrera', 0),
            ('coord_medicina', 'coord.med@academicpredict.cl', 'Luis', 'Medicina', 'coordinador_carrera', 1),
            ('analista_juan', 'juan.analista@academicpredict.cl', 'Juan', 'Pérez', 'analista', None),
            ('analista_sofia', 'sofia.analista@academicpredict.cl', 'Sofía', 'González', 'analista', None),
            ('analista_diego', 'diego.analista@academicpredict.cl', 'Diego', 'Martínez', 'analista', None),
        ]
        
        for username, email, first_name, last_name, rol, carrera_idx in usuarios:
            # Obtener carrera si aplica
            carrera = None
            if carrera_idx is not None and len(carreras) > carrera_idx:
                carrera = carreras[carrera_idx]
            
            user, creado = self._crear_usuario(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                rol=rol,
                carrera=carrera
            )
            
            if creado:
                usuarios_creados += 1
            else:
                usuarios_actualizados += 1
        
        # Resumen
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('✅ PROCESO COMPLETADO'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'📊 Usuarios creados: {usuarios_creados}')
        self.stdout.write(f'🔄 Usuarios actualizados: {usuarios_actualizados}')
        self.stdout.write(f'📝 Total procesados: {usuarios_creados + usuarios_actualizados}')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('🔑 CREDENCIALES DE ACCESO:'))
        self.stdout.write(self.style.WARNING('-' * 70))
        self.stdout.write('Todos los usuarios tienen la contraseña: admin123')
        self.stdout.write('')
        self._mostrar_tabla_usuarios()

    def _crear_usuario(self, username, email, first_name, last_name, rol, carrera=None):
        """
        Crea o actualiza un usuario con su perfil.
        
        ⚠️ CORRECCIÓN CRÍTICA: El campo se llama 'user' no 'usuario'
        """
        try:
            # 1. Crear o actualizar User
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True,
                    'is_staff': rol == 'admin',
                }
            )
            
            if not user_created:
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.is_active = True
                user.is_staff = rol == 'admin'
            
            user.set_password('admin123')
            user.save()
            
            # 2. Crear o actualizar PerfilUsuario
            # ✅ CORRECCIÓN: El campo es 'user' no 'usuario'
            perfil, perfil_created = PerfilUsuario.objects.get_or_create(
                user=user  # ← AQUÍ ESTABA EL ERROR
            )
            
            # ✅ AHORA SÍ asignar el rol correcto
            perfil.rol = rol
            perfil.carrera_asignada = carrera
            perfil.save()
            
            # Mostrar resultado
            icono = '✅' if user_created else '🔄'
            accion = 'CREADO' if user_created else 'ACTUALIZADO'
            
            self.stdout.write(
                f'{icono} {accion}: {username:20s} | {rol:20s} | {first_name} {last_name}'
            )
            
            if carrera:
                self.stdout.write(
                    f'   └─ Carrera asignada: {carrera.nombre[:50]}'
                )
            
            return user, user_created
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ ERROR al crear {username}: {str(e)}')
            )
            return None, False

    def _obtener_carreras(self):
        """Obtiene las primeras 2 carreras de la BD."""
        carreras = list(CarreraUniversitaria.objects.all()[:2])
        
        if not carreras:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  No hay carreras en la base de datos.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'📚 Carreras encontradas: {len(carreras)}')
            )
            for i, carrera in enumerate(carreras, 1):
                self.stdout.write(f'   {i}. {carrera.codigo_carrera} - {carrera.nombre[:50]}')
        
        self.stdout.write('')
        return carreras

    def _limpiar_usuarios(self):
        """Elimina usuarios de prueba existentes."""
        self.stdout.write(self.style.WARNING('🗑️  Limpiando usuarios de prueba...'))
        
        usuarios_prueba = [
            'admin_prueba', 'coord_general', 'coord_academico',
            'coord_ingenieria', 'coord_medicina',
            'analista_juan', 'analista_sofia', 'analista_diego'
        ]
        
        eliminados = 0
        for username in usuarios_prueba:
            try:
                user = User.objects.get(username=username)
                user.delete()
                eliminados += 1
                self.stdout.write(f'   ✅ Eliminado: {username}')
            except User.DoesNotExist:
                pass
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {eliminados} usuario(s) eliminado(s)')
        )
        self.stdout.write('')

    def _mostrar_tabla_usuarios(self):
        """Muestra tabla con usuarios creados."""
        self.stdout.write('📋 LISTADO DE USUARIOS:')
        self.stdout.write('-' * 70)
        self.stdout.write(
            f'{"USERNAME":20s} | {"ROL":20s} | {"NOMBRE COMPLETO":25s}'
        )
        self.stdout.write('-' * 70)
        
        usuarios = [
            ('admin_prueba', 'Administrador'),
            ('coord_general', 'Coordinador'),
            ('coord_academico', 'Coordinador'),
            ('coord_ingenieria', 'Coordinador de Carrera'),
            ('coord_medicina', 'Coordinador de Carrera'),
            ('analista_juan', 'Analista'),
            ('analista_sofia', 'Analista'),
            ('analista_diego', 'Analista'),
        ]
        
        for username, rol_display in usuarios:
            try:
                user = User.objects.get(username=username)
                nombre = f'{user.first_name} {user.last_name}'
                rol_real = user.perfil.get_rol_display()
                self.stdout.write(f'{username:20s} | {rol_real:20s} | {nombre:25s}')
            except User.DoesNotExist:
                pass
        
        self.stdout.write('-' * 70)
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('💡 RECORDATORIO:'))
        self.stdout.write('   - Contraseña para todos: admin123')
        self.stdout.write('   - Los analistas NO tienen acceso al panel admin')
        self.stdout.write('')