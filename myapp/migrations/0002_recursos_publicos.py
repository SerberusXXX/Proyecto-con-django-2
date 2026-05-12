import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


RECURSOS_INICIALES = [
    (1, "Salon A", "salon", "Bloque A - Piso 2", 30, "Salon para clases teoricas y reuniones academicas."),
    (2, "Salon B", "salon", "Bloque B - Piso 1", 25, "Espacio flexible para tutorias, clases cortas y grupos de estudio."),
    (3, "Laboratorio", "laboratorio", "Bloque C - Sala 305", 20, "Laboratorio con computadores para practicas de software."),
    (4, "Auditorio", "auditorio", "Edificio principal", 80, "Auditorio para conferencias, charlas y presentaciones."),
    (5, "Equipo de video", "equipo", "Oficina de medios", 1, "Equipo portatil para grabacion o apoyo audiovisual."),
]


def crear_recursos(apps, schema_editor):
    Recurso = apps.get_model("myapp", "Recurso")
    for pk, nombre, tipo, ubicacion, capacidad, descripcion in RECURSOS_INICIALES:
        Recurso.objects.update_or_create(
            pk=pk,
            defaults={
                "nombre": nombre,
                "tipo": tipo,
                "ubicacion": ubicacion,
                "capacidad": capacidad,
                "descripcion": descripcion,
                "activo": True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("myapp", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Recurso",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=100, verbose_name="nombre")),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("salon", "Salon"),
                            ("auditorio", "Auditorio"),
                            ("laboratorio", "Laboratorio"),
                            ("equipo", "Equipo"),
                        ],
                        max_length=20,
                        verbose_name="tipo",
                    ),
                ),
                ("ubicacion", models.CharField(max_length=120, verbose_name="ubicacion")),
                ("capacidad", models.PositiveIntegerField(default=1, verbose_name="capacidad")),
                ("descripcion", models.TextField(verbose_name="descripcion")),
                ("activo", models.BooleanField(default=True, verbose_name="activo")),
            ],
            options={
                "verbose_name": "recurso",
                "verbose_name_plural": "recursos",
                "ordering": ["tipo", "nombre"],
            },
        ),
        migrations.RunPython(crear_recursos, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="reserva",
            name="recurso",
        ),
        migrations.AddField(
            model_name="reserva",
            name="recurso",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="reservas",
                to="myapp.recurso",
                verbose_name="recurso",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="reserva",
            name="usuario",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="reservas",
                to="auth.user",
                verbose_name="usuario",
            ),
        ),
        migrations.AlterModelOptions(
            name="reserva",
            options={
                "ordering": ["fecha", "hora_inicio", "recurso__nombre"],
                "verbose_name": "reserva",
                "verbose_name_plural": "reservas",
            },
        ),
    ]
