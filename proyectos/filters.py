# proyectos/filters.py
import django_filters
from django import forms
from .models import Proyecto

class ProyectoFilter(django_filters.FilterSet):
    buscar = django_filters.CharFilter(
        field_name='titulo',
        lookup_expr='icontains',
        label="Buscar",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por título...'
        })
    )

    tipo = django_filters.ChoiceFilter(
        choices=[
            ('Informe', 'Informe'),
            ('Proyecto de Investigación', 'Proyecto de Investigación'),
        ],
        label='Tipo de Proyecto',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    carrera = django_filters.ChoiceFilter(
    field_name='carrera',
    lookup_expr='icontains',
    choices=lambda: Proyecto.objects.values_list('carrera', 'carrera').distinct(),
    label='Carrera',
    widget=forms.Select(attrs={'class': 'form-select'})
)


    class Meta:
        model = Proyecto
        fields = ['buscar', 'tipo', 'carrera']
