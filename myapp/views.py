from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    CancelarReservaForm,
    ConsultaFechaForm,
    RegistroUsuarioForm,
    ReservaForm,
)
from .models import Recurso, Reserva


def index(request):
    consulta_form = ConsultaFechaForm(request.GET or None)
    recursos = Recurso.objects.filter(activo=True).prefetch_related("reservas")
    fecha_consulta = timezone.localdate()

    if consulta_form.is_valid() and consulta_form.cleaned_data.get("fecha"):
        fecha_consulta = consulta_form.cleaned_data["fecha"]

    recursos_estado = [
        {
            "recurso": recurso,
            "disponible": recurso.esta_disponible(fecha_consulta),
            "reservas": recurso.reservas.filter(
                fecha=fecha_consulta, estado=Reserva.ACTIVA
            ).order_by("hora_inicio"),
        }
        for recurso in recursos
    ]

    return render(
        request,
        "myapp/index.html",
        {
            "consulta_form": consulta_form,
            "fecha_consulta": fecha_consulta,
            "recursos_estado": recursos_estado,
        },
    )


def detalle_recurso(request, recurso_id):
    recurso = get_object_or_404(Recurso, pk=recurso_id, activo=True)
    consulta_form = ConsultaFechaForm(request.GET or None)
    fecha_consulta = timezone.localdate()

    if consulta_form.is_valid() and consulta_form.cleaned_data.get("fecha"):
        fecha_consulta = consulta_form.cleaned_data["fecha"]

    reservas = recurso.reservas.filter(
        fecha=fecha_consulta, estado=Reserva.ACTIVA
    ).order_by("hora_inicio")

    return render(
        request,
        "myapp/recurso_detalle.html",
        {
            "consulta_form": consulta_form,
            "fecha_consulta": fecha_consulta,
            "recurso": recurso,
            "reservas": reservas,
        },
    )


def registro(request):
    if request.user.is_authenticated:
        return redirect("panel")

    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, "Cuenta creada correctamente.")
            return redirect("panel")
    else:
        form = RegistroUsuarioForm()

    return render(request, "registration/registro.html", {"form": form})


@login_required
def panel(request):
    consulta_form = ConsultaFechaForm(request.GET or None)
    reservas = Reserva.objects.filter(usuario=request.user)
    fecha_consulta = None

    if consulta_form.is_valid():
        fecha_consulta = consulta_form.cleaned_data.get("fecha")
        if fecha_consulta:
            reservas = reservas.filter(fecha=fecha_consulta)

    resumen = {
        "activas": Reserva.objects.filter(
            usuario=request.user, estado=Reserva.ACTIVA
        ).count(),
        "canceladas": Reserva.objects.filter(
            usuario=request.user, estado=Reserva.CANCELADA
        ).count(),
        "hoy": Reserva.objects.filter(
            usuario=request.user, fecha=timezone.localdate(), estado=Reserva.ACTIVA
        ).count(),
    }

    return render(
        request,
        "myapp/panel.html",
        {
            "consulta_form": consulta_form,
            "fecha_consulta": fecha_consulta,
            "reservas": reservas,
            "resumen": resumen,
        },
    )


@login_required
def agenda_privada(request):
    consulta_form = ConsultaFechaForm(request.GET or None)
    fecha_consulta = timezone.localdate()

    if consulta_form.is_valid() and consulta_form.cleaned_data.get("fecha"):
        fecha_consulta = consulta_form.cleaned_data["fecha"]

    recursos = Recurso.objects.filter(activo=True).prefetch_related("reservas")
    agenda = [
        {
            "recurso": recurso,
            "reservas": recurso.reservas.filter(
                fecha=fecha_consulta, estado=Reserva.ACTIVA
            ).order_by("hora_inicio"),
        }
        for recurso in recursos
    ]

    return render(
        request,
        "myapp/agenda_privada.html",
        {
            "agenda": agenda,
            "consulta_form": consulta_form,
            "fecha_consulta": fecha_consulta,
        },
    )


@login_required
def crear_reserva(request, recurso_id=None):
    recurso = None
    if recurso_id:
        recurso = get_object_or_404(Recurso, pk=recurso_id, activo=True)

    if request.method == "POST":
        form = ReservaForm(request.POST, recurso=recurso, usuario=request.user)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            reserva.save()
            messages.success(request, "Reserva registrada correctamente.")
            return redirect("panel")
    else:
        form = ReservaForm(recurso=recurso, usuario=request.user)

    return render(request, "myapp/form.html", {"form": form, "recurso": recurso})


@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id, usuario=request.user)

    if reserva.esta_cancelada:
        messages.info(request, "La reserva ya estaba cancelada.")
        return redirect("panel")

    if request.method == "POST":
        form = CancelarReservaForm(request.POST)
        if form.is_valid():
            reserva.estado = Reserva.CANCELADA
            reserva.motivo_cancelacion = form.cleaned_data["motivo_cancelacion"]
            reserva.save()
            messages.success(request, "Reserva cancelada correctamente.")
            return redirect("panel")
    else:
        form = CancelarReservaForm()

    return render(
        request,
        "myapp/cancelar.html",
        {
            "form": form,
            "reserva": reserva,
        },
    )
