# simulacao/templatetags/custom_filters.py
from django import template

register = template.Library()


@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def currency(value):
    from simulacao.formatacao import formatar_moeda_brl
    return formatar_moeda_brl(value)
