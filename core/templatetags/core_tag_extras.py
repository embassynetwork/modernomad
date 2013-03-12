from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='split')
@stringfilter
def split(value, arg):
	''' split the string 'value' on all occurences of 'arg' '''
	return value.split(arg) 
