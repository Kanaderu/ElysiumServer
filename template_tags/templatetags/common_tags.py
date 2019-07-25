from django import template
from django.template.defaultfilters import stringfilter
from ElysiumServer.settings import base
register = template.Library()


class SetVarNode(template.Node):

    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = var_value

    def render(self, context):
        try:
            value = template.Variable(self.var_value).resolve(context)
        except template.VariableDoesNotExist:
            value = ""
        context[self.var_name] = value

        return u""

    def increment(self, context):
        context[self.var_name] = context[self.var_name] + 1


@register.tag(name='set')
def set_var(parser, token):
    """
    {% set some_var = '123' %}
    """
    parts = token.split_contents()
    if len(parts) < 4:
        raise template.TemplateSyntaxError("'set' tag must be of the form: {% set <var_name> = <var_value> %}")

    return SetVarNode(parts[1], parts[3])


class GetSettingsNode(template.Node):

    def __init__(self, settings_param):
        self.settings_param = settings_param

    def render(self, context):
        return self.settings_param

@register.tag(name='settings')
@stringfilter
def get_settings(value, token):
    parts = token.split_contents()
    #print('val is ' + str(parts))
    #print('BLOG_NUM_RECENT_POSTS is ' + str(base.BLOG_NUM_RECENT_POSTS))
    setting = getattr(base, parts[1])
    return GetSettingsNode(setting)
