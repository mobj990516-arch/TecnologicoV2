# proyectos/admin.py
from django.contrib import admin
from .models import Proyecto

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'carrera', 'año', 'tipo', 'fecha_subida', 'descargas', 'creado_por')
    search_fields = ('titulo', 'autor', 'descripcion', 'sinopsis')
    list_filter = ('carrera', 'tipo', 'fecha_subida')
