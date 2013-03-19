from django import template
from django.template.defaultfilters import stringfilter
import itertools

register = template.Library()

@register.filter(name='split')
@stringfilter
def split(value, arg):
	''' split the string 'value' on all occurences of 'arg' '''
	return value.split(arg) 


@register.filter
def subsets_size(value, set_size):
    ''' Breaks up a list into subsets (lists) of size <set_size>, with the last set
    containing the remainder if less than set_size '''

    set_len = int(set_size)
    i = iter(value)
    while True:
        chunk = list(itertools.islice(i, set_len))
        if chunk:
            yield chunk
        else:
            break