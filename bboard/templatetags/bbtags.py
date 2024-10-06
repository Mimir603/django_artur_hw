from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='cur', is_safe=True)
# @stringfilter иногда бывает лучше
def currency(value, name='Тг.'):
    if not value:
        value = 0
    return f'{value:.2f} {name}'


# помогает работать со временем
@register.filter(expects_localtime=True)
def datetimefilter(value):
    pass


@register.filter
def somefilter(value):
    return mark_safe(escape(value))

# register.filter('currency', currency)


@register.simple_tag
def lst(sep, *args):
    return mark_safe(f'{sep.join(args)} <strong>(итого: {len(args)})</strong>')


@register.inclusion_tag('tags/ulist.html')
def ulist(*args):
    return {'items': args}
