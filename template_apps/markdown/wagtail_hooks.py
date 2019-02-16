from django.conf import settings
from wagtail.core import hooks


@hooks.register('insert_editor_js')
def editor_js():
    s = '<script src="{0}js/simplemde.min.js"></script>\n'
    s += '<script src="{0}js/simplemde.attach.js"></script>\n'
    return s.format(settings.STATIC_URL)


@hooks.register('insert_editor_css')
def editor_css():
    s = '<link rel="stylesheet" href="{0}css/simplemde.min.css" />\n'
    s += '<link rel="stylesheet" href="{0}css/all.css" />\n'
    return s.format(settings.STATIC_URL)