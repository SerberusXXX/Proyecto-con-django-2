from datetime import date, time, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import ReservaForm
from .models import Recurso, Reserva


class ReservaFormTests(TestCase):
    def setUp(self):
        self.fecha = timezone.localdate() + timedelta(days=1)
        self.salon_a = Recurso.objects.create(
            nombre="Salon A",
            tipo=Recurso.SALON,
            ubicacion="Bloque A",
            capacidad=30,
            descripcion="Salon de clase",
        )
        self.salon_b = Recurso.objects.create(
            nombre="Salon B",
            tipo=Recurso.SALON,
            ubicacion="Bloque B",
            capacidad=25,
            descripcion="Salon auxiliar",
        )

    def datos_validos(self, **overrides):
        data = {
            "recurso": self.salon_a.id,
            "responsable": "Laura Gomez",
            "correo": "laura@example.com",
            "fecha": self.fecha,
            "hora_inicio": time(9, 0),
            "hora_fin": time(10, 0),
            "descripcion": "Clase de programacion",
        }
        data.update(overrides)
        return data

    def test_crea_reserva_valida(self):
        form = ReservaForm(data=self.datos_validos())

        self.assertTrue(form.is_valid())

    def test_rechaza_hora_fin_anterior(self):
        form = ReservaForm(data=self.datos_validos(hora_fin=time(8, 30)))

        self.assertFalse(form.is_valid())
        self.assertIn("hora_fin", form.errors)

    def test_rechaza_reserva_cruzada_para_mismo_recurso(self):
        Reserva.objects.create(
            recurso=self.salon_a,
            responsable="Laura Gomez",
            correo="laura@example.com",
            fecha=self.fecha,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
        )

        form = ReservaForm(
            data=self.datos_validos(
                responsable="Carlos Ruiz",
                correo="carlos@example.com",
                hora_inicio=time(9, 30),
                hora_fin=time(10, 30),
            )
        )

        self.assertFalse(form.is_valid())
        self.assertIn("hora_inicio", form.errors)

    def test_permite_mismo_horario_si_recurso_es_distinto(self):
        Reserva.objects.create(
            recurso=self.salon_a,
            responsable="Laura Gomez",
            correo="laura@example.com",
            fecha=self.fecha,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
        )

        form = ReservaForm(data=self.datos_validos(recurso=self.salon_b.id))

        self.assertTrue(form.is_valid())


class ReservaViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="laura", email="laura@example.com", password="ClaveSegura123"
        )
        self.recurso = Recurso.objects.create(
            nombre="Auditorio",
            tipo=Recurso.AUDITORIO,
            ubicacion="Edificio principal",
            capacidad=80,
            descripcion="Auditorio principal",
        )

    def test_catalogo_publico_carga_correctamente(self):
        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Encuentra el salon")

    def test_crear_reserva_requiere_login(self):
        response = self.client.get(reverse("crear_reserva"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_cancelar_reserva_cambia_estado(self):
        self.client.login(username="laura", password="ClaveSegura123")
        reserva = Reserva.objects.create(
            recurso=self.recurso,
            usuario=self.user,
            responsable="Laura Gomez",
            correo="laura@example.com",
            fecha=date.today() + timedelta(days=2),
            hora_inicio=time(14, 0),
            hora_fin=time(15, 0),
        )

        response = self.client.post(
            reverse("cancelar_reserva", args=[reserva.id]),
            {"motivo_cancelacion": "Cambio de horario"},
            follow=True,
        )

        reserva.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(reserva.estado, Reserva.CANCELADA)
