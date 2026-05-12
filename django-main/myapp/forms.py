from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Recurso, Reserva


class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(label="Correo")
    first_name = forms.CharField(label="Nombre", max_length=150)
    last_name = forms.CharField(label="Apellido", max_length=150, required=False)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = [
            "recurso",
            "responsable",
            "correo",
            "fecha",
            "hora_inicio",
            "hora_fin",
            "descripcion",
        ]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "hora_inicio": forms.TimeInput(attrs={"type": "time"}),
            "hora_fin": forms.TimeInput(attrs={"type": "time"}),
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, recurso=None, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["recurso"].queryset = Recurso.objects.filter(activo=True)

        if recurso:
            self.fields["recurso"].initial = recurso

        if usuario and usuario.is_authenticated:
            nombre = usuario.get_full_name() or usuario.username
            self.fields["responsable"].initial = nombre
            self.fields["correo"].initial = usuario.email


class ConsultaFechaForm(forms.Form):
    fecha = forms.DateField(
        label="Consultar por fecha",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )


class CancelarReservaForm(forms.Form):
    motivo_cancelacion = forms.CharField(
        label="Motivo de cancelacion",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
