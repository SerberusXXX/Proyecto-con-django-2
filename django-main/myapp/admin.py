from django.contrib import admin

from .models import Recurso, Reserva


@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "ubicacion", "capacidad", "activo")
    list_filter = ("tipo", "activo")
    search_fields = ("nombre", "ubicacion", "descripcion")


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = (
        "recurso",
        "fecha",
        "hora_inicio",
        "hora_fin",
        "responsable",
        "usuario",
        "estado",
    )
    list_filter = ("estado", "recurso", "fecha")
    search_fields = ("responsable", "correo", "descripcion", "usuario__username")
    ordering = ("fecha", "hora_inicio")
