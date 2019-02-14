from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, Q
from django.utils.translation import ugettext_lazy as _
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.admin.edit_handlers import (
    FieldPanel, InlinePanel, MultiFieldPanel, FieldRowPanel, StreamFieldPanel)
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images import get_image_model_string
from wagtail.snippets.models import register_snippet
from wagtail.search import index

from ElysiumServer.models import STANDARD_BLOCKS

from taggit.models import TaggedItemBase, Tag
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from .utils import unique_slugify
import datetime


# Helper function to get note context
def get_note_context(context):
    """ Get context data useful on all note related pages """
    context['authors'] = get_user_model().objects.filter(
        owned_pages__live=True,
        owned_pages__content_type__model='notepage'
    ).annotate(Count('owned_pages')).order_by('-owned_pages__count')
    '''
    context['all_categories'] = NoteCategory.objects.all()
    context['root_categories'] = NoteCategory.objects.filter(
        parent=None,
    ).prefetch_related(
        'children',
    ).annotate(
        note_count=Count('notepage'),
    )
    '''
    return context


def limit_author_choices():
    """ Limit choices in note author field based on config settings """
    LIMIT_AUTHOR_CHOICES = getattr(settings, 'NOTE_LIMIT_AUTHOR_CHOICES_GROUP', None)
    if LIMIT_AUTHOR_CHOICES:
        if isinstance(LIMIT_AUTHOR_CHOICES, str):
            limit = Q(groups__name=LIMIT_AUTHOR_CHOICES)
        else:
            limit = Q()
            for s in LIMIT_AUTHOR_CHOICES:
                limit = limit | Q(groups__name=s)
        if getattr(settings, 'NOTE_LIMIT_AUTHOR_CHOICES_ADMIN', False):
            limit = limit | Q(is_staff=True)
    else:
        limit = {'is_staff': True}
    return limit


# Note Index Page
class NoteIndexPage(Page):
    @property
    def notes(self):
        # Get list of note pages that are descendants of this page
        notes = NotePage.objects.descendant_of(self).live()
        notes = notes.order_by(
            '-date'
        ).select_related('owner').prefetch_related(
            'tagged_note_items__tag',
            'categories',
            'categories__category',
        )
        return notes

    def get_context(self, request, tag=None, category=None, author=None, *args,
                    **kwargs):
        context = super(NoteIndexPage, self).get_context(
            request, *args, **kwargs)
        notes = self.notes
        '''
        if tag is None:
            tag = request.GET.get('tag')
        if tag:
            notes = notes.filter(tags__slug=tag)
            category = request.GET.get('category')
        if category:
            notes = notes.filter(categories__category__name=category)
            category = NoteCategory.objects.filter(name=category)
        '''
        if author:
            if isinstance(author, str) and not author.isdigit():
                notes = notes.filter(author__username=author)
            else:
                notes = notes.filter(author_id=author)

        # Pagination
        page = request.GET.get('page')
        page_size = 10
        if hasattr(settings, 'NOTE_PAGINATION_PER_PAGE'):
            page_size = settings.NOTE_PAGINATION_PER_PAGE

        paginator = None
        if page_size is not None:
            paginator = Paginator(notes, page_size)  # Show 10 notes per page
            try:
                notes = paginator.page(page)
            except PageNotAnInteger:
                notes = paginator.page(1)
            except EmptyPage:
                notes = paginator.page(paginator.num_pages)

        context['notes'] = notes
        #context['category'] = category
        #context['tag'] = tag
        context['author'] = author
        context['COMMENTS_APP'] = settings.COMMENTS_APP
        context['paginator'] = paginator
        context = get_note_context(context)

        return context

    class Meta:
        verbose_name = _('Note Index')

    subpage_types = ['note.NoteSubjectIndexPage']


class NoteSubjectIndexPage(Page):
    body = StreamField(STANDARD_BLOCKS)
    date = models.DateField(
        _("Post date"), default=datetime.datetime.today,
        help_text=_("This date may be displayed on the note post. It is not "
                    "used to schedule posts to go live at a later date.")
    )
    header_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Header Image')
    )

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    settings_panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('go_live_at'),
                FieldPanel('expire_at'),
            ], classname="label-above"),
        ], 'Scheduled publishing', classname="publishing"),
        FieldPanel('date'),
     ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        ImageChooserPanel('header_image'),
        StreamFieldPanel('body', classname="full title"),
    ]

    subpage_types = ['note.NoteSubjectPage']
    parent_page_types = ['note.NoteIndexPage']

    class Meta:
        verbose_name = _('Subject Index Page')


class NoteSubjectPage(Page):
    body = StreamField(STANDARD_BLOCKS)
    date = models.DateField(
        _("Post date"), default=datetime.datetime.today,
        help_text=_("This date may be displayed on the note post. It is not "
                    "used to schedule posts to go live at a later date.")
    )
    header_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Header Image')
    )

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    settings_panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('go_live_at'),
                FieldPanel('expire_at'),
            ], classname="label-above"),
        ], 'Scheduled publishing', classname="publishing"),
        FieldPanel('date'),
     ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        ImageChooserPanel('header_image'),
        StreamFieldPanel('body', classname="full title"),
    ]

    subpage_type = ['note.NoteSubjectPage', 'note.NotePage']
    parent_page_types = ['note.NoteSubjectIndexPage']

    class Meta:
        verbose_name = _('Subject Page')


# Note Page
class NotePage(Page):
    body = StreamField(STANDARD_BLOCKS)
    #tags = ClusterTaggableManager(through='note.NotePageTag', blank=True)
    date = models.DateField(
        _("Post date"), default=datetime.datetime.today,
        help_text=_("This date may be displayed on the note post. It is not "
                    "used to schedule posts to go live at a later date.")
    )
    header_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Header Image')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        limit_choices_to=limit_author_choices,
        verbose_name=_('Author'),
        on_delete=models.SET_NULL,
        related_name='author_note_pages',
    )

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    #note_categories = models.ManyToManyField('note.NoteCategory', through='note.NoteCategoryNotePage', blank=True)

    settings_panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('go_live_at'),
                FieldPanel('expire_at'),
            ], classname="label-above"),
        ], 'Scheduled publishing', classname="publishing"),
        FieldPanel('date'),
        FieldPanel('author'),
    ]

    content_panels = [
        FieldPanel('title', classname="full title"),
        #MultiFieldPanel([
        #    FieldPanel('tags'),
        #    InlinePanel('categories', label=_("Categories")),
        #], heading="Tags and Categories"),
        ImageChooserPanel('header_image'),
        StreamFieldPanel('body', classname="full title"),
    ]

    def save_revision(self, *args, **kwargs):
        if not self.author:
            self.author = self.owner
        return super(NotePage, self).save_revision(*args, **kwargs)

    def get_absolute_url(self):
        return self.url

    def get_note_index(self):
        # Find closest ancestor which is a note index
        return self.get_ancestors().type(NoteIndexPage).last()

    def get_context(self, request, *args, **kwargs):
        context = super(NotePage, self).get_context(request, *args, **kwargs)
        context['notes'] = self.get_note_index().noteindexpage.notes
        context = get_note_context(context)
        context['COMMENTS_APP'] = settings.COMMENTS_APP
        return context

    class Meta:
        verbose_name = _('Note Page')
        verbose_name_plural = _('Note Pages')

    parent_page_types = ['note.NoteSubjectPage']
