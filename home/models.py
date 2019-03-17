from django.db import models
from django.utils.translation import ugettext_lazy as _

from wagtail.core.models import Page
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import StreamFieldPanel

from ElysiumServer.editor import STANDARD_BLOCKS, ParallaxBlock


# load in wagtail hooks
@register_setting(icon='doc-empty')
class DescriptionSettings(BaseSetting):
    footer_description = StreamField(STANDARD_BLOCKS, blank=True, null=True)

    panels = [
        StreamFieldPanel('footer_description'),
    ]

    class Meta:
        verbose_name = _('Site Descriptions')


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


class LandingPage(Page):
    parallax = StreamField(STANDARD_BLOCKS)

    content_panels = Page.content_panels + [
        StreamFieldPanel('parallax'),
    ]

    class Meta:
        verbose_name = _('Landing Page')

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