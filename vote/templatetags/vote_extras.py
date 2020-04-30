import random

from django import template

register = template.Library()


@register.simple_tag
def applicant_name(application):
    return application.get_display_name()


@register.filter
def shuffle(items):
    items = list(items)[:]
    random.shuffle(items)
    return items
