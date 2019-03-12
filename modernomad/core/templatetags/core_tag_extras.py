from django import template
from django.template.defaultfilters import stringfilter
import itertools
from django.template import NodeList
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='split')
@stringfilter
def split(value, arg):
    ''' split the string 'value' on all occurences of 'arg' '''
    return value.split(arg)


@register.filter
def subsets_size(value, set_size):
    ''' Breaks up a list into subsets (lists) of size <set_size>, with the last set
    containing the remainder if less than set_size. use like so:
        {% for subset in coming_month|subsets_size: 6 %}
        ...
        {% endfor %}
    '''

    set_len = int(set_size)
    i = iter(value)
    while True:
        chunk = list(itertools.islice(i, set_len))
        if chunk:
            yield chunk
        else:
            break

# from http://djangosnippets.org/snippets/1576/
@register.tag()
def ifusergroup(parser, token):
    """ Check to see if the currently logged in user belongs to a specific
    group. Requires the Django authentication contrib app and middleware.

    Usage: {% ifusergroup Admins %} ... {% endifusergroup %}, or
           {% ifusergroup Admins|Group1|Group2 %} ... {% endifusergroup %}, or
           {% ifusergroup Admins %} ... {% else %} ... {% endifusergroup %}

    """
    try:
        tag, group = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifusergroup' requires 1 argument.")

    nodelist_true = parser.parse(('else', 'endifusergroup'))
    token = parser.next_token()

    if token.contents == 'else':
        nodelist_false = parser.parse(('endifusergroup',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()

    return GroupCheckNode(group, nodelist_true, nodelist_false)


class GroupCheckNode(template.Node):
    def __init__(self, group, nodelist_true, nodelist_false):
        self.group = group
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        user = template.Variable('user').resolve(context)

        if user is None or not user.is_authenticated():
            return self.nodelist_false.render(context)

        try:
            for group in self.group.split("|"):

                if Group.objects.get(name=group) in user.groups.all():
                    return self.nodelist_true.render(context)
        except Group.DoesNotExist:
            return self.nodelist_false.render(context)
        return self.nodelist_false.render(context)

