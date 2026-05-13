# proyectos/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

# ------------------------------------
# VALIDADORES
# ------------------------------------
def validar_imagen(img):
    if img.size > 3 * 1024 * 1024:
        raise ValidationError("La imagen no debe superar 3MB.")
    if not img.name.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise ValidationError("Formato de imagen no permitido.")

def validar_archivo(file):
    if file.size > 20 * 1024 * 1024:
        raise ValidationError("Archivo demasiado grande (máx 20MB).")


# ------------------------------------
# ROLES
# ------------------------------------
ROLE_CHOICES = (
    ("estudiante", "Estudiante"),
    ("admin", "Administrador"),
)


# ------------------------------------
# USUARIO PERSONALIZADO
# ------------------------------------
class Usuario(AbstractUser):

    matricula = models.CharField(
        max_length=9,
        unique=True,
        validators=[
            RegexValidator(
                r'^\d{9}$',
                'La matrícula debe tener exactamente 9 dígitos.'
            )
        ],
        null=True, blank=True  # opcional si lo necesitas
    )

    rol = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="estudiante"
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        default="avatars/default.png",
        blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.rol})"


# ------------------------------------
# PERFIL (UNO A UNO)
# ------------------------------------
class Perfil(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to="avatars/",
        default="avatars/default.png",
        blank=True
    )

    def __str__(self):
        return self.usuario.username


# ------------------------------------
# PROYECTOS
# ------------------------------------
class Proyecto(models.Model):
    CARRERA_CHOICES = [
        ("Ingeniería en Sistemas Computacionales", "Ingeniería en Sistemas Computacionales"),
        ("Mecatrónica", "Mecatrónica"),
        ("Ingeniería en Sistemas Automotrices", "Ingeniería en Sistemas Automotrices"),
        ("Arquitectura", "Arquitectura"),
        ("Contabilidad", "Contabilidad"),
    ]

    TIPO_CHOICES = [
        ("Informe de Investigación", "Informe de Investigación"),
        ("Proyecto de Investigación", "Proyecto de Investigación"),
    ]

    AÑO_CHOICES = [(year, year) for year in range(2020, 2031)]

    titulo = models.CharField(max_length=250)
    autor = models.CharField(max_length=200, editable=False)
    descripcion = models.TextField(blank=True)

    tipo = models.CharField(
        max_length=100,
        choices=TIPO_CHOICES,        # 👈 AGREGADO
        blank=True
    )

    carrera = models.CharField(
        max_length=150,
        choices=CARRERA_CHOICES,     # 👈 AGREGADO
        blank=True
    )

    año = models.PositiveIntegerField(
        choices=AÑO_CHOICES,         # 👈 AGREGADO
        null=True,
        blank=True
    )

    portada = models.ImageField(
        upload_to='portadas/',
        null=True,
        blank=True,
        validators=[validar_imagen]
    )

    archivo = models.FileField(
        upload_to='proyectos/',
        validators=[validar_archivo]
    )

    sinopsis_ia = models.TextField(blank=True, null=True)

    descargas = models.PositiveIntegerField(default=0)

    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_subida']

    def __str__(self):
        return self.titulo
