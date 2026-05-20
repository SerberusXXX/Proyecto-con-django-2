from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("recursos/<int:recurso_id>/", views.detalle_recurso, name="detalle_recurso"),
    path("registro/", views.registro, name="registro"),
    path("panel/", views.panel, name="panel"),
    path("agenda/", views.agenda_privada, name="agenda_privada"),
    path("reservas/nueva/", views.crear_reserva, name="crear_reserva"),
    path(
        "recursos/<int:recurso_id>/reservar/",
        views.crear_reserva,
        name="crear_reserva_recurso",
    ),
    path(
        "reservas/<int:reserva_id>/cancelar/",
        views.cancelar_reserva,
        name="cancelar_reserva",
    ),
]
