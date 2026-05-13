# proyectos/forms.py
from django import forms
from .models import Proyecto
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 
from .models import Usuario
from .models import Perfil

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

AÑO_CHOICES = [(year, year) for year in range(2020, 2031)]  # años 2020-2030

class ProyectoForm(forms.ModelForm):
    carrera = forms.ChoiceField(choices=CARRERA_CHOICES, widget=forms.Select(attrs={"class": "form-control"}))
    tipo = forms.ChoiceField(choices=TIPO_CHOICES, widget=forms.Select(attrs={"class": "form-control"}))
    año = forms.ChoiceField(choices=AÑO_CHOICES, widget=forms.Select(attrs={"class": "form-control"}))

    class Meta:
        model = Proyecto
        fields = ['titulo', 'descripcion', 'carrera', 'año', 'tipo', 'portada', 'archivo']
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "portada": forms.FileInput(attrs={"class": "form-control"}),
            "archivo": forms.FileInput(attrs={"class": "form-control"}),
        }

class RegistroForm(UserCreationForm):
    matricula = forms.CharField(max_length=20)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = Usuario
        fields = [
            "username", "first_name", "last_name", "email",
            "matricula", "avatar",
            "password1", "password2"
        ]

        labels = {
            "username": "Nombre de usuario",
            "first_name": "Nombre",
            "last_name": "Apellidos",
            "email": "Correo",
            "matricula": "Número de matrícula",
            "avatar": "Foto de perfil",
            "password1": "Contraseña",
            "password2": "Repetir contraseña",
        }

        
def clean(self):
    cleaned = super().clean()
    if cleaned.get("password") != cleaned.get("password2"):
         raise forms.ValidationError("Las contraseñas no coinciden.")
    return cleaned


def clean_email(self):
    email = self.cleaned_data["email"]
    if User.objects.filter(email=email).exists():
        raise forms.ValidationError("Este email ya está registrado.")
    return email

def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
            perfil = Perfil.objects.create(
                user=user,
                matricula=self.cleaned_data["matricula"],
                avatar=self.cleaned_data.get("avatar") or "avatars/default.png",
                rol="estudiante",  # por defecto
            )
        return user


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ["avatar"]
        widgets = {
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }
