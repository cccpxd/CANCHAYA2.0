from django import forms
from django.db.models import Q

from .models import Cancha, Reserva


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['cancha', 'nombre_cliente', 'telefono', 'fecha', 'hora_inicio', 'hora_fin']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cancha'].queryset = Cancha.objects.filter(activa=True)

    def clean(self):
        cleaned = super().clean()
        cancha = cleaned.get('cancha')
        fecha = cleaned.get('fecha')
        inicio = cleaned.get('hora_inicio')
        fin = cleaned.get('hora_fin')

        if inicio and fin and inicio >= fin:
            self.add_error('hora_fin', 'La hora final debe ser posterior a la hora inicial.')

        if cancha and fecha and inicio and fin and inicio < fin:
            ocupado = Reserva.objects.filter(
                cancha=cancha,
                fecha=fecha,
            ).filter(Q(hora_inicio__lt=fin) & Q(hora_fin__gt=inicio))
            if self.instance.pk:
                ocupado = ocupado.exclude(pk=self.instance.pk)
            if ocupado.exists():
                raise forms.ValidationError('Ese horario ya esta ocupado para esta cancha.')

        return cleaned
