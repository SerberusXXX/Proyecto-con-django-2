from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Recurso(models.Model):
    SALON = "salon"
    AUDITORIO = "auditorio"
    LABORATORIO = "laboratorio"
    EQUIPO = "equipo"

    TIPO_CHOICES = [
        (SALON, "Salon"),
        (AUDITORIO, "Auditorio"),
        (LABORATORIO, "Laboratorio"),
        (EQUIPO, "Equipo"),
    ]

    nombre = models.CharField("nombre", max_length=100)
    tipo = models.CharField("tipo", max_length=20, choices=TIPO_CHOICES)
    ubicacion = models.CharField("ubicacion", max_length=120)
    capacidad = models.PositiveIntegerField("capacidad", default=1)
    descripcion = models.TextField("descripcion")
    activo = models.BooleanField("activo", default=True)

    class Meta:
        ordering = ["tipo", "nombre"]
        verbose_name = "recurso"
        verbose_name_plural = "recursos"

    def __str__(self):
        return self.nombre

    def esta_disponible(self, fecha, hora_inicio=None, hora_fin=None):
        if not fecha:
            return True

        reservas = self.reservas.filter(fecha=fecha, estado=Reserva.ACTIVA)

        if hora_inicio and hora_fin:
            reservas = reservas.filter(
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio,
            )

        return not reservas.exists()


class Reserva(models.Model):
    ACTIVA = "activa"
    CANCELADA = "cancelada"

    ESTADO_CHOICES = [
        (ACTIVA, "Activa"),
        (CANCELADA, "Cancelada"),
    ]

    recurso = models.ForeignKey(
        Recurso,
        on_delete=models.PROTECT,
        related_name="reservas",
        verbose_name="recurso",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="reservas",
        verbose_name="usuario",
    )
    responsable = models.CharField("responsable", max_length=120)
    correo = models.EmailField("correo de contacto")
    fecha = models.DateField("fecha")
    hora_inicio = models.TimeField("hora de inicio")
    hora_fin = models.TimeField("hora de fin")
    descripcion = models.TextField("descripcion", blank=True)
    estado = models.CharField(
        "estado", max_length=20, choices=ESTADO_CHOICES, default=ACTIVA
    )
    motivo_cancelacion = models.TextField("motivo de cancelacion", blank=True)
    creada_en = models.DateTimeField("creada en", auto_now_add=True)
    actualizada_en = models.DateTimeField("actualizada en", auto_now=True)

    class Meta:
        ordering = ["fecha", "hora_inicio", "recurso__nombre"]
        verbose_name = "reserva"
        verbose_name_plural = "reservas"

    def __str__(self):
        return f"{self.recurso} - {self.fecha} {self.hora_inicio}"

    @property
    def esta_cancelada(self):
        return self.estado == self.CANCELADA

    def clean(self):
        errors = {}

        if self.hora_inicio and self.hora_fin and self.hora_fin <= self.hora_inicio:
            errors["hora_fin"] = "La hora de fin debe ser posterior a la hora de inicio."

        if self.fecha and self.fecha < timezone.localdate():
            errors["fecha"] = "No se pueden registrar reservas en fechas pasadas."

        if self.recurso and self.fecha and self.hora_inicio and self.hora_fin:
            reservas_cruzadas = Reserva.objects.filter(
                recurso=self.recurso,
                fecha=self.fecha,
                estado=self.ACTIVA,
                hora_inicio__lt=self.hora_fin,
                hora_fin__gt=self.hora_inicio,
            )

            if self.pk:
                reservas_cruzadas = reservas_cruzadas.exclude(pk=self.pk)

            if reservas_cruzadas.exists():
                errors["hora_inicio"] = (
                    "El recurso ya tiene una reserva activa en ese horario."
                )

        if errors:
            raise ValidationError(errors)
