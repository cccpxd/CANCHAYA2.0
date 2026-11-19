
from datetime import date, datetime

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Cancha, Usuario


class RegistroForm(UserCreationForm):
    username = forms.CharField(label='Nombre de usuario', max_length=150)
    email = forms.EmailField(label='Correo electrónico')
    first_name = forms.CharField(label='Nombre', max_length=150)
    last_name = forms.CharField(label='Apellido', max_length=150)
    telefono = forms.CharField(label='Teléfono', max_length=30)
    password1 = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text='Usa al menos 10 caracteres y evita contraseñas comunes.',
    )
    password2 = forms.CharField(
        label='Confirma tu contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text='Escribe nuevamente la contraseña para confirmarla.',
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')

    field_order = (
        'first_name',
        'last_name',
        'username',
        'email',
        'telefono',
        'password1',
        'password2',
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            Usuario.objects.create(
                user=user,
                telefono=self.cleaned_data['telefono'],
            )

        return user


class CanchaForm(forms.ModelForm):

    class Meta:
        model = Cancha
        fields = ['nombre', 'tipo', 'precio_hora', 'activa']

        labels = {
            'nombre': 'Nombre de la cancha',
            'tipo': 'Tipo de cancha',
            'precio_hora': 'Precio por hora',
            'activa': 'Cancha activa',
        }


class _CanchaFechaHoraForm(forms.Form):
    """Formulario base para elegir una cancha y un intervalo horario."""

    cancha_id = forms.ChoiceField(label='Cancha')

    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Fecha',
    )

    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label='Hora de inicio',
    )

    hora_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label='Hora de finalización',
    )

    def __init__(self, *args, canchas=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Si no recibimos un queryset, consultamos las canchas activas.
        if canchas is None:
            canchas = Cancha.objects.filter(activa=True)

        self.fields['cancha_id'].choices = [
            (str(cancha.id), cancha.nombre)
            for cancha in canchas
        ]

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']

        if fecha < date.today():
            raise forms.ValidationError(
                'La fecha no puede estar en el pasado.'
            )

        return fecha

    def clean(self):
        cleaned = super().clean()

        inicio = cleaned.get('hora_inicio')
        fin = cleaned.get('hora_fin')

        if inicio and fin and inicio >= fin:
            self.add_error(
                'hora_fin',
                'La hora final debe ser posterior a la hora inicial.'
            )

        return cleaned


class ReservaForm(_CanchaFechaHoraForm):
    field_order = [
        'cancha_id',
        'fecha',
        'hora_inicio',
        'hora_fin',
    ]


class DisponibilidadForm(_CanchaFechaHoraForm):

    def clean(self):
        cleaned = super().clean()

        fecha = cleaned.get('fecha')
        hora_inicio = cleaned.get('hora_inicio')

        if fecha == date.today() and hora_inicio:
            hora_actual = datetime.now().time().replace(
                second=0,
                microsecond=0,
            )

            if hora_inicio < hora_actual:
                self.add_error(
                    'hora_inicio',
                    'No puedes consultar una hora pasada.'
                )

        return cleaned
