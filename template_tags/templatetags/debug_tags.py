from django import template
register = template.Library()


@register.filter(name='get_obj_attr')
def get_obj_attr(obj, attr):
    return getattr(obj, attr)


@register.filter(name='get_obj_dir')
def get_obj_dir(obj):
    return dir(obj)


@register.filter(name='class_name')
def class_name(x):
    return x.__class__.__name__
