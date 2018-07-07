from wagtail.core import blocks
from wagtail.core.fields import StreamField

from wagtailcodeblock.blocks import CodeBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.images.blocks import ImageChooserBlock

class QuoteBlock(blocks.TextBlock):
    class Meta:
        template = 'blocks/quote.html'
        icon = 'openquote'
        label = 'Quote'
        '''
        body = StreamField([
            ('rich_text', blocks.RichTextBlock(icon='doc-full', label='Rich Text')),
            ('code', CodeBlock(icon='code')),
            ('quote', QuoteBlock(icon='openquote')),
            ('html', blocks.RawHTMLBlock(icon='site', label='HTML')
        ])
        '''