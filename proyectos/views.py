# proyectos/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, HttpResponse, Http404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Sum
from django.contrib import messages
from django.core.mail import send_mail
from django.db import models
import csv, os, mimetypes

from .models import Proyecto, Perfil, Usuario
from .forms import ProyectoForm, RegistroForm, PerfilForm, UsuarioForm
from .utils import extraer_texto, generar_sinopsis
from .filters import ProyectoFilter
from django.http import HttpResponse

# =========================================
# INICIO (PÁGINA PRINCIPAL) ⭐⭐⭐⭐⭐
# =========================================
def inicio(request):
    proyectos = Proyecto.objects.all()

    # valores GET
    q = request.GET.get("q", "")
    tipo = request.GET.get("tipo", "")
    carrera = request.GET.get("carrera", "")

    # filtrado
    if q:
        proyectos = proyectos.filter(titulo__icontains=q)

    if tipo:
        proyectos = proyectos.filter(tipo=tipo)

    if carrera:
        proyectos = proyectos.filter(carrera=carrera)

    # PAGINACIÓN
    paginator = Paginator(proyectos, 9)
    page_number = request.GET.get("page")
    proyectos_paginados = paginator.get_page(page_number)

    # construimos la URL sin "page"
    querystring = request.GET.copy()
    if "page" in querystring:
        querystring.pop("page")
    querystring = querystring.urlencode()

    return render(request, "inicio.html", {
        "proyectos": proyectos_paginados,
        "querystring": querystring,
    })


# =========================================
# SUBIR PROYECTO
# =========================================
@login_required
def subir(request):
    if request.method == "POST":
        form = ProyectoForm(request.POST, request.FILES)

        if form.is_valid():
            titulo = form.cleaned_data['titulo']
            # Validar duplicados para el mismo usuario
            if Proyecto.objects.filter(titulo=titulo, creado_por=request.user).exists():
                messages.error(request, "Ya tienes un proyecto con ese nombre.")
                return redirect("subir")
            
            proyecto = form.save(commit=False)
            proyecto.creado_por = request.user
            proyecto.autor = request.user.get_full_name() or request.user.username

            # Extraer texto
            archivo = request.FILES.get("archivo")
            texto_extraido = ""

            if archivo:
                try:
                    texto_extraido = extraer_texto(archivo)
                except Exception as e:
                    messages.warning(request, f"No se pudo leer el archivo: {str(e)}")

            # IA sinopsis
            try:
                if texto_extraido.strip():
                    proyecto.sinopsis_ia = generar_sinopsis(texto_extraido)
                else:
                    texto_base = f"{proyecto.titulo}\n{proyecto.descripcion}"
                    proyecto.sinopsis_ia = generar_sinopsis(texto_base)
            except Exception as e:
                proyecto.sinopsis_ia = ""
                messages.warning(request, f"No se pudo generar sinopsis automática: {str(e)}")

            proyecto.save()
            messages.success(request, "Proyecto subido correctamente.")
            return redirect("inicio")

        messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = ProyectoForm()

    return render(request, "subir.html", {"form": form})


# =========================================
# PERFIL
# =========================================
@login_required
def perfil(request):
    usuario = request.user
    perfil, creado = Perfil.objects.get_or_create(usuario=usuario)

    if request.method == "POST":
        usuario_form = UsuarioForm(request.POST, instance=usuario)
        perfil_form = PerfilForm(request.POST, request.FILES, instance=perfil)

        if usuario_form.is_valid() and perfil_form.is_valid():
            usuario_form.save()
            perfil_form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("perfil")

    else:
        usuario_form = UsuarioForm(instance=usuario)
        perfil_form = PerfilForm(instance=perfil)

    return render(request, "perfil.html", {
        "usuario_form": usuario_form,
        "perfil_form": perfil_form,
        "perfil": perfil,
    })


# =========================================
# DESCARGAR ARCHIVOS
# =========================================
def descargar(request, proyecto_id):
    proyecto = Proyecto.objects.get(id=proyecto_id)
    file_path = proyecto.archivo.path

    try:
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "application/octet-stream"

        response = FileResponse(open(file_path, 'rb'), content_type=mime_type)
        response['Content-Disposition'] = f'attachment; filename="{proyecto.archivo.name.split('/')[-1]}"'

        proyecto.descargas += 1
        proyecto.save()

        return response

    except FileNotFoundError:
        raise Http404("El archivo no existe")


# =========================================
# DASHBOARD
# =========================================
@login_required
def dashboard(request):
    proyectos = Proyecto.objects.all()
    total_proyectos = proyectos.count()
    total_descargas = proyectos.aggregate(total=Sum('descargas'))['total'] or 0

    return render(request, 'dashboard.html', {
        'proyectos': proyectos,
        'total_proyectos': total_proyectos,
        'total_descargas': total_descargas,
    })


# =========================================
# EXPORTAR CSV
# =========================================
def export_csv(request):
    proyectos = Proyecto.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="proyectos.csv"'

    writer = csv.writer(response)
    writer.writerow(['id','titulo','autor','carrera','año','tipo','fecha_subida','descargas'])

    for p in proyectos:
        writer.writerow([p.id,p.titulo,p.autor,p.carrera,p.año,p.tipo,p.fecha_subida,p.descargas])

    return response


# =========================================
# REGISTRO
# =========================================
def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()

            send_mail(
                "Bienvenido",
                f"Hola {user.first_name}, tu cuenta fue creada exitosamente.",
                "tu_correo@gmail.com",
                [user.email],
            )

            messages.success(request, "Registro exitoso.")
            return redirect("login")

    else:
        form = RegistroForm()

    return render(request, "registro.html", {"form": form})


# =========================================
# ROLES
# =========================================
def es_admin(user):
    return user.rol == "admin"

def es_estudiante(user):
    return user.rol == "estudiante"


@user_passes_test(es_admin)
def dashboard_admin(request):
    return render(request, "dashboard_admin.html")


@user_passes_test(es_estudiante)
def subir_proyecto(request):
    return render(request, "subir.html")


# =========================================
# MIS PROYECTOS
# =========================================
@login_required
def mis_proyectos(request):
    proyectos = Proyecto.objects.filter(creado_por=request.user)
    return render(request, "mis_proyectos.html", {"proyectos": proyectos})

# =========================================
#  EDITAR PROYECTO 
# =========================================
def editar_proyecto(request, id):
    proyecto = get_object_or_404(Proyecto, id=id, creado_por=request.user)

    if request.method == "POST":
        form = ProyectoForm(request.POST, request.FILES, instance=proyecto)
        if form.is_valid():
            form.save()
            return redirect('mis_proyectos')
    else:
        form = ProyectoForm(instance=proyecto)

        return render(request, "editar_proyecto.html", {"form": form})

# =========================================
#  ELIMINAR PROYECTO 
# =========================================

def eliminar_proyecto(request, id):
    proyecto = get_object_or_404(Proyecto, id=id, creado_por=request.user)

    if request.method == "POST":
        # Eliminar el archivo físico si existe
        if proyecto.archivo:
            if os.path.isfile(proyecto.archivo.path):
                os.remove(proyecto.archivo.path)
        proyecto.delete()
        return redirect('mis_proyectos')

    return render(request, "confirmar_eliminar.html", {"proyecto": proyecto})



# =========================================
# VER PROYECTO
# =========================================
def ver_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    return render(request, "ver_proyecto.html", {"proyecto": proyecto})


# =========================================
# GENERAR SINOPSIS ia
# =========================================
def generar_sinopsis_view(request):
    sinopsis = None

    if request.method == "POST":
        texto = request.POST.get("texto", "")
        sinopsis = generar_sinopsis(texto)

    return render(request, "generar_sinopsis.html", {"sinopsis": sinopsis})


