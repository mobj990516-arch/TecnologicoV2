# proyectos/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('subir/', views.subir, name='subir'),
    path("descargar/<int:proyecto_id>/", views.descargar, name="descargar"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('export/', views.export_csv, name='export_csv'),
    path("registro/", views.registro, name="registro"),
     path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),
    path("perfil/", views.perfil, name="perfil"),
    path("sinopsis/", views.generar_sinopsis_view, name="generar_sinopsis"),
    path("mis-proyectos/", views.mis_proyectos, name="mis_proyectos"),
    path("proyecto/<int:proyecto_id>/", views.ver_proyecto, name="ver_proyecto"),
    path('proyecto/<int:id>/editar/', views.editar_proyecto, name='editar_proyecto'),
    path('proyecto/<int:id>/eliminar/', views.eliminar_proyecto, name='eliminar_proyecto'),

]
