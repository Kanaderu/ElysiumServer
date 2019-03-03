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

from wagtail.contrib.settings.models import BaseSetting, register_setting

from django.db import models

from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.snippets.models import register_snippet

from ElysiumServer.editor import STANDARD_BLOCKS


# load in wagtail hooks
@register_snippet
class SiteDescriptions(models.Model):
    #footer_description = models.TextField(name='footer_description', blank=True, null=False)
    footer_description = StreamField(STANDARD_BLOCKS)

    panels = [
        StreamFieldPanel('footer_description'),
    ]

    def __init__(self):
        self.text = 'Site Descriptions'

    def __str__(self):
        return self.text


@register_setting(icon='group')
class SocialMediaSettings(BaseSetting):
    facebook = models.URLField(help_text='Facebook URL', blank=True, null=True)
    twitter = models.CharField(max_length=255, help_text='Twitter username, without the @', blank=True, null=True)
    instagram = models.CharField(max_length=255, help_text='Instagram username, without the @', blank=True, null=True)
    google_plus = models.CharField(max_length=255, help_text='Google+ username, without the +', blank=True, null=True)

    class Meta:
        verbose_name = _('Social Media')


class BlankPage(Page):
    body = StreamField(STANDARD_BLOCKS)

    content_panels = Page.content_panels + [
        StreamFieldPanel('body', classname="full"),
    ]

    class Meta:
        verbose_name = _('Blank Page')

'''
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
'''