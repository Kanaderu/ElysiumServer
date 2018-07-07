from django.db import models
from django.utils.translation import ugettext_lazy as _

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
#from wagtail.admin.edit_handlers import FieldPanel

from wagtail.contrib.table_block.blocks import TableBlock

from wagtail.core.fields import StreamField
from wagtail.core import blocks
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.blocks import ImageChooserBlock


from wagtailcodeblock.blocks import CodeBlock
from wagtail.embeds.blocks import EmbedBlock
from ElysiumServer.models import QuoteBlock

class BlankPage(Page):
    body = StreamField([
        ('heading', blocks.CharBlock(icon='title', classname='full title')),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('embedded_video', EmbedBlock(icon='media')),
        ('code', CodeBlock(label=_('Code'))),
        ('table', TableBlock()),
        ('html', blocks.RawHTMLBlock(icon='site', label=_('HTML'))),
        ('quote', QuoteBlock(icon='openquote')),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body', classname="full"),
    ]

    class Meta:
        verbose_name = _('Blank Page')


class CodePage(Page):
    author = models.CharField(max_length=255)
    date = models.DateField("Post date")
    #code = CodeBlock(label='code')

    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('code', CodeBlock(lablel='Code'))
    ])

    content_panels = Page.content_panels + [
        FieldPanel('author'),
        FieldPanel('date'),
        StreamFieldPanel('body'),
    ]
