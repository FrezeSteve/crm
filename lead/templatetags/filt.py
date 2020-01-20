from django import template
from django.forms.fields import CheckboxInput, FileInput, TextInput

register = template.Library()


@register.filter(name='is_checkbox')
def is_checkbox(value):
    return isinstance(value, CheckboxInput)


@register.filter(name='is_fileinput')
def is_fileinput(value):
    return isinstance(value, FileInput)


@register.filter(name='is_textinput')
def is_textinput(value):
    return isinstance(value, TextInput)

