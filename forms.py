from datetime import date, time, datetime

from django import forms

from .models import canchas_activas


class CanchaForm(forms.Form):
    nombre = forms.CharField(max_length=80, label='Nombre de la cancha')
    tipo = forms.ChoiceField(
        choices=[('Futbol 5', 'Fútbol 5'), ('Volley playa', 'Vóley playa')],
        label='Tipo de cancha',
    )
    precio_hora = forms.DecimalField(
        min_value=0,
        max_digits=8,
        decimal_places=2,
        label='Precio por hora',
    )
    activa = forms.BooleanField(
        required=False, initial=True, label='Cancha activa'
    )


class _CanchaFechaHoraForm(forms.Form):
    """Base común: elegir una cancha activa y un intervalo horario válido."""

    cancha_id = forms.ChoiceField(label='Cancha')
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), label='Fecha'
    )
    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}), label='Hora de inicio'
    )
    hora_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}), label='Hora de finalización'
    )

    def __init__(self, *args, canchas=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cancha_id'].choices = [
            (str(cancha['id']), cancha['nombre'])
            for cancha in canchas_activas(canchas or [])
        ]

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']
        if fecha < date.today():
            raise forms.ValidationError('La fecha no puede estar en el pasado.')
        return fecha

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get('hora_inicio')
        fin = cleaned.get('hora_fin')
        if inicio and fin and inicio >= fin:
            self.add_error(
                'hora_fin', 'La hora final debe ser posterior a la hora inicial.'
            )
        return cleaned


class ReservaForm(_CanchaFechaHoraForm):
    nombre_cliente = forms.CharField(max_length=100, label='Nombre del cliente')
    telefono = forms.CharField(max_length=30, label='Teléfono')

    field_order = [
        'cancha_id',
        'nombre_cliente',
        'telefono',
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
                second=0, microsecond=0
            )
            if hora_inicio < hora_actual:
                self.add_error(
                    'hora_inicio', 'No puedes consultar una hora pasada.'
                )
        return cleaned