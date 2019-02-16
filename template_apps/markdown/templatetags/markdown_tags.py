from django import template
import markdown

register = template.Library()


@register.filter(name='markdown')
def markdown_filter(value):
    return markdown.markdown(value, output_format='html5')