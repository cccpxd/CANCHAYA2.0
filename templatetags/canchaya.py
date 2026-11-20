from django import template

register = template.Library()


@register.filter
def precio(valor):
    """Formatea un valor como pesos colombianos: 48000 -> $48.000."""
    try:
        numero = int(round(float(valor)))
    except (TypeError, ValueError):
        return valor

    return '$' + f'{numero:,}'.replace(',', '.')
