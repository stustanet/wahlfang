from django import template

register = template.Library()

@register.simple_tag
def applicant_name(application):
    return application.get_display_name()
