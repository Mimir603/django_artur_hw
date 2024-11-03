from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()

@register.filter(name='cur', is_safe=True)
# @stringfilter
def currency(value, name='тг.'):
    if not value:
        value = 0
    return f'{value:.2f} {name}'

@register.filter(expects_localtime=True)
def datetimefilter(value):
    pass


@register.filter
def somefilter(value):
    return mark_safe(escape(value))  # SafeText

# register.filter('currency', currency)


# @register.simple_tag(takes_context=True)
# def lst(context, sep, *args):
@register.simple_tag
def lst(sep, *args):
    # return f'{sep.join(args)} (итого {len(args)})'
    return mark_safe(f'{sep.join(args)} <strong>(итого: {len(args)})</strong>')


@register.inclusion_tag('tags/ulist.html')
def ulist(*args):
    return {'items': args}
