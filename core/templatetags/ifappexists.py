from django.template import Library
from django import template
from django.conf import settings

register = Library()

@register.tag
def ifappexists(parser, token):
    """ Conditional Django template tag to check if one or more apps exist.

    From: https://gist.github.com/xtranophilist/6637377

    Usage: {% ifappexists tag %} ... {% endifappexists %}, or
           {% ifappexists tag inventory %} ... {% else %} ... {% endifappexists %}

    """
    try:
        tokens = token.split_contents()
        apps = []
        apps += tokens[1:]
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifappexists' requires at least 1 argument.")

    nodelist_true = parser.parse(('else', 'endifappexists'))
    token = parser.next_token()

    if token.contents == 'else':
        nodelist_false = parser.parse(('endifappexists',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()

    return AppCheckNode(apps, nodelist_true, nodelist_false)


class AppCheckNode(template.Node):
    def __init__(self, apps, nodelist_true, nodelist_false):
        self.apps = apps
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        allowed = False
        for app in self.apps:

            if app.startswith('"') and app.endswith('"'):
                app = app[1:-1]

            if app.startswith("'") and app.endswith("'"):
                app = app[1:-1]

            if app in settings.INSTALLED_APPS:
                allowed = True
            else:
                break

        if allowed:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)
