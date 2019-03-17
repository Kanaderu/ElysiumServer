from wagtail.core import blocks
from wagtail.core.blocks import BooleanBlock

from wagtailcodeblock.blocks import CodeBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.images.blocks import ImageChooserBlock
from template_apps.markdown.utils import MarkdownBlock

from django.utils.translation import ugettext_lazy as _


# load in wagtail hooks
class QuoteBlock(blocks.TextBlock):
    class Meta:
        template = 'blocks/quote.html'
        icon = 'openquote'
        label = 'Quote'


class GoogleMapBlock(blocks.StructBlock):
    map_long = blocks.CharBlock(required=True, max_length=255)
    map_lat = blocks.CharBlock(required=True, max_length=255)
    map_zoom_level = blocks.CharBlock(default=14, required=True, max_length=3)

    class Meta:
        template = 'blocks/google_map.html'
        icon = 'site'
        label = 'Google Map'


COLUMN_BLOCKS = [
    ('heading', blocks.CharBlock(icon='title', classname='full title')),
    ('paragraph', blocks.RichTextBlock()),
    ('image', ImageChooserBlock()),
    ('embedded_video', EmbedBlock(icon='media')),
    ('code', CodeBlock(label=_('Code'))),
    ('table', TableBlock()),
    ('html', blocks.RawHTMLBlock(icon='site', label=_('HTML'))),
    ('quote', QuoteBlock(icon='openquote')),
    ('google_map', GoogleMapBlock()),
]


COLOUR_CHOICES = [('white', 'White'),
                  ('black', 'Black')]


class TwoColumnBlock(blocks.StructBlock):
    background = blocks.ChoiceBlock(choices=COLOUR_CHOICES, default="white")
    left_column = blocks.StreamBlock(COLUMN_BLOCKS, icon='arrow-left', label='Left column content')
    right_column = blocks.StreamBlock(COLUMN_BLOCKS, icon='arrow-right', label='Right column content')

    class Meta:
        template = 'blocks/two_column_block.html'
        icon = 'list-ul'
        label = 'Two Columns'


class ThreeColumnBlock(blocks.StructBlock):
    background = blocks.ChoiceBlock(choices=COLOUR_CHOICES, default="white")
    left_column = blocks.StreamBlock(COLUMN_BLOCKS, icon='arrow-left', label='Left column content')
    middle_column = blocks.StreamBlock(COLUMN_BLOCKS, icon='horizontalrule', label='Middle column content')
    right_column = blocks.StreamBlock(COLUMN_BLOCKS, icon='arrow-right', label='Right column content')

    class Meta:
        template = 'blocks/three_column_block.html'
        icon = 'list-ul'
        label = 'Three Columns'


class ParallaxBlock(blocks.StructBlock):
    video = DocumentChooserBlock(required=True, icon='media')
    poster_image = ImageChooserBlock(required=True, icon='image')
    focus = BooleanBlock(required=False, help_text=_('Auto focus to parallax on page load'), )

    class Meta:
        template = 'blocks/parallax_block.html'
        icon = 'arrows-up-down'
        label = 'Parallax Video'
    #class Meta:
    #    template = 'blocks/person_block.html'


STANDARD_BLOCKS = [
    ('markdown', MarkdownBlock()),
    ('heading', blocks.CharBlock(icon='title', classname='full title')),
    ('paragraph', blocks.RichTextBlock()),
    ('image', ImageChooserBlock()),
    ('embedded_video', EmbedBlock(icon='media')),
    ('code', CodeBlock(label=_('Code'))),
    ('table', TableBlock()),
    ('html', blocks.RawHTMLBlock(icon='site', label=_('HTML'))),
    ('quote', QuoteBlock(icon='openquote')),
    ('google_map', GoogleMapBlock()),
    ('two_column_block', TwoColumnBlock()),
    ('three_column_block', ThreeColumnBlock()),
    ('parallax', ParallaxBlock()),
]
