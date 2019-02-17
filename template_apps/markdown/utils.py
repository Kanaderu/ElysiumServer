from django import forms
from wagtail.core import blocks
from django.db.models import TextField
from wagtail.utils.widgets import WidgetWithScript
from django.forms import Media
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from bleach import clean as bleach_clean
from markdown import markdown
from pymdownx import superfences, arithmatex


def render(text):

    formatted_html = markdown(
        text,
        extensions=[
            'pymdownx.arithmatex',
            'pymdownx.highlight',
            'pymdownx.caret',
            'pymdownx.mark',
            'pymdownx.tilde',
            'pymdownx.progressbar',
            'pymdownx.smartsymbols',
            'pymdownx.tasklist',

            # contains: pymdownx.betterem, pymdownx.superfences, markdown.extensions.footnotes,
            # markdown.extensions.attr_list, markdown.extensions.def_list, markdown.extensions.tables
            # markdown.extensions.abbr, pymdownx.extrarawhtml
            'pymdownx.extra',

            'markdown.extensions.meta',
            'markdown.extensions.nl2br',
            'markdown.extensions.sane_lists',
            'markdown.extensions.smarty',
            'markdown.extensions.toc',
            'markdown.extensions.wikilinks',
        ],
        extension_configs={
            # settings to switch from MathJax to KaTex
            'pymdownx.arithmatex': {
                'generic': True,
                'preview': False,
            },
            'pymdownx.highlight': {
                'use_pygments': False,
                'css_class': 'highlight line-numbers'
            },
            'pymdownx.extra': {
                'pymdownx.superfences': {
                    'custom_fences': [
                        {
                            'name': 'flow',
                            'class': 'uml-flowchart',
                            'format': superfences.fence_div_format
                        },
                        {
                            'name': 'sequence',
                            'class': 'uml-sequence-diagram',
                            'format': superfences.fence_div_format
                        },
                        {
                            'name': 'math',
                            'class': 'arithmatex',
                            'format': arithmatex.inline_generic_format
                        },
                    ]
                }
            }
        },
        output_format='html5'
    )

    # Sanitizing html with bleach to avoid code injection
    sanitized_html = bleach_clean(
        formatted_html,
        # Allowed tags, attributes and styles
        tags=[
            'p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'tt', 'pre', 'em', 'strong', 'ul', 'li',
            'dl', 'dd', 'dt', 'code', 'img', 'a', 'table', 'tr', 'th', 'td', 'tbody', 'caption', 'colgroup',
            'thead', 'tfoot', 'blockquote', 'ol', 'hr', 'br', 'sub', 'sup', 'strike', 'del', 'mark', 'input', 'label',
            #'script'
        ],
        attributes={
            '*': ['class', 'style', 'id'],
            'a': ['href', 'target', 'rel'],
            'img': ['src', 'alt'],
            'tr': ['rowspan', 'colspan'],
            'td': ['rowspan', 'colspan', 'align'],
            'input': ['name', 'type', 'disabled', 'checked', 'id'],
            'ul': ['class'],
            'li': ['class'],
            'div': ['class'],
            'span': ['class'],
            'label': ['for'],
            #'script': ['type', 'mode'],
        },
        styles=[
            'color', 'background-color', 'font-family', 'font-weight', 'font-size', 'width', 'height',
            'text-align', 'border', 'border-top', 'border-bottom', 'border-left', 'border-right', 'padding',
            'padding-top', 'padding-bottom', 'padding-left', 'padding-right', 'margin', 'margin-top',
            'margin-bottom', 'margin-left', 'margin-right'
        ]
    )
    
    return mark_safe(sanitized_html)


class MarkdownTextarea(WidgetWithScript, forms.widgets.Textarea):
    """
    Textarea that uses SimpleMDE to display a preview of markdown
    """
    def __init__(self, **kwargs):
        super(MarkdownTextarea, self).__init__(**kwargs)

    def render_js_init(self, id_, name, value):
        return 'simplemdeAttach("{0}");'.format(id_)


class MarkdownBlock(blocks.TextBlock):
    """
    Markdown block using SimpleMDE plugin
    """
    def __init__(self, **kwargs):
        if 'classname' in kwargs:
            kwargs['classname'] += ' markdown'
        else:
            kwargs['classname'] = 'markdown'
        super(MarkdownBlock, self).__init__(**kwargs)

    @cached_property
    def field(self):
        field_kwargs = {'widget': MarkdownTextarea()}
        field_kwargs.update(self.field_options)
        return forms.CharField(**field_kwargs)

    @property
    def media(self):
        return Media(
            js=[
                'js/simplemde.min.js',
                'js/simplemde.attach.js'
            ],
            css={
                'all': ('css/simplemde.min.css',)
            }
        )

    def render_basic(self, value, context=None):
        return render(value)

    class Meta:
        icon = 'snippet'
        label = 'Markdown'


class MarkdownField(TextField):
    def formfield(self, **kwargs):
        defaults = {
            'widget': MarkdownTextarea
        }
        defaults.update(kwargs)
        return super(MarkdownField, self).formfield(**defaults)

    def __init__(self, **kwargs):
        super(MarkdownField, self).__init__(**kwargs)
