from django import forms
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

        # 1. Validación de coherencia de datos (Responsabilidad del formulario)
        if inicio and fin and inicio >= fin:
            self.add_error('hora_fin', 'La hora final debe ser posterior a la hora inicial.')

        # 2. Validación de regla de negocio delegada al modelo (SRP aplicado)
        if cancha and fecha and inicio and fin and inicio < fin:
            Cancha.objects.select_for_update().get(pk=cancha.pk)
            # Obtenemos el ID de la reserva si es que estamos editando una existente
            reserva_id = self.instance.pk if self.instance.pk else None
            
            # Le "preguntamos" a la cancha si está disponible
            if not cancha.esta_disponible(fecha, inicio, fin, reserva_id):
                raise forms.ValidationError('Ese horario ya esta ocupado para esta cancha.')

        return cleaned