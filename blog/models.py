from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.admin.edit_handlers import (
    FieldPanel, InlinePanel, MultiFieldPanel, FieldRowPanel, StreamFieldPanel)
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images import get_image_model_string
from wagtail.snippets.models import register_snippet
from wagtail.search import index

from wagtail.core import blocks
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtailcodeblock.blocks import CodeBlock
from ElysiumServer.models import QuoteBlock

from taggit.models import TaggedItemBase, Tag
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from .utils import unique_slugify
import datetime


# Helper function to get blog context
def get_blog_context(context):
    """ Get context data useful on all blog related pages """
    context['authors'] = get_user_model().objects.filter(
        owned_pages__live=True,
        owned_pages__content_type__model='blogpage'
    ).annotate(Count('owned_pages')).order_by('-owned_pages__count')
    context['all_categories'] = BlogCategory.objects.all()
    context['root_categories'] = BlogCategory.objects.filter(
        parent=None,
    ).prefetch_related(
        'children',
    ).annotate(
        blog_count=Count('blogpage'),
    )
    return context


def limit_author_choices():
    """ Limit choices in blog author field based on config settings """
    LIMIT_AUTHOR_CHOICES = getattr(settings, 'BLOG_LIMIT_AUTHOR_CHOICES_GROUP', None)
    if LIMIT_AUTHOR_CHOICES:
        if isinstance(LIMIT_AUTHOR_CHOICES, str):
            limit = Q(groups__name=LIMIT_AUTHOR_CHOICES)
        else:
            limit = Q()
            for s in LIMIT_AUTHOR_CHOICES:
                limit = limit | Q(groups__name=s)
        if getattr(settings, 'BLOG_LIMIT_AUTHOR_CHOICES_ADMIN', False):
            limit = limit | Q(is_staff=True)
    else:
        limit = {'is_staff': True}
    return limit




# Blog Index Page
class BlogIndexPage(Page):
    @property
    def blogs(self):
        # Get list of blog pages that are descendants of this page
        blogs = BlogPage.objects.descendant_of(self).live()
        blogs = blogs.order_by(
            '-date'
        ).select_related('owner').prefetch_related(
            'tagged_items__tag',
            'categories',
            'categories__category',
        )
        return blogs

    def get_context(self, request, tag=None, category=None, author=None, *args,
                    **kwargs):
        context = super(BlogIndexPage, self).get_context(
            request, *args, **kwargs)
        blogs = self.blogs

        if tag is None:
            tag = request.GET.get('tag')
        if tag:
            blogs = blogs.filter(tags__slug=tag)
        if category is None:  # Not coming from category_view in views.py
            if request.GET.get('category'):
                category = get_object_or_404(BlogCategory, slug=request.GET.get('category'))
        if category:
            if not request.GET.get('category'):
                category = get_object_or_404(BlogCategory, slug=category)
            blogs = blogs.filter(categories__category__name=category)
        if author:
            if isinstance(author, str) and not author.isdigit():
                blogs = blogs.filter(author__username=author)
            else:
                blogs = blogs.filter(author_id=author)

        # Pagination
        page = request.GET.get('page')
        page_size = 10
        if hasattr(settings, 'BLOG_PAGINATION_PER_PAGE'):
            page_size = settings.BLOG_PAGINATION_PER_PAGE

        paginator = None
        if page_size is not None:
            paginator = Paginator(blogs, page_size)  # Show 10 blogs per page
            try:
                blogs = paginator.page(page)
            except PageNotAnInteger:
                blogs = paginator.page(1)
            except EmptyPage:
                blogs = paginator.page(paginator.num_pages)

        context['blogs'] = blogs
        context['category'] = category
        context['tag'] = tag
        context['author'] = author
        context['COMMENTS_APP'] = settings.COMMENTS_APP
        context['paginator'] = paginator
        context = get_blog_context(context)

        return context

    class Meta:
        verbose_name = _('Blog Index')
    subpage_types = ['blog.BlogPage']


class BlogCategoryIndexPage(Page):
    @property
    def categories(self):
        # Get list of blog pages that are descendants of this page
        categories = BlogCategory.objects.all()
        categories = categories.order_by('name')
        return categories

    def get_context(self, request, tag=None, category=None, author=None, *args,
                    **kwargs):
        context = super(BlogCategoryIndexPage, self).get_context(request, *args, **kwargs)

        categories = self.categories

        '''
        # Pagination
        page = request.GET.get('page')
        page_size = 10
        if hasattr(settings, 'BLOG_PAGINATION_PER_PAGE'):
            page_size = settings.BLOG_PAGINATION_PER_PAGE

        paginator = None
        if page_size is not None:
            paginator = Paginator(blogs, page_size)  # Show 10 blogs per page
            try:
                blogs = paginator.page(page)
            except PageNotAnInteger:
                blogs = paginator.page(1)
            except EmptyPage:
                blogs = paginator.page(paginator.num_pages)

        context['blogs'] = blogs
        context['category'] = category
        context['tag'] = tag
        context['author'] = author
        context['COMMENTS_APP'] = settings.COMMENTS_APP
        context['paginator'] = paginator
        '''
        context = get_blog_context(context)

        return context

    class Meta:
        verbose_name = _('Blog Category Index')


# Blog Category
@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=80, unique=True, verbose_name=_('Category Name'))
    slug = models.SlugField(unique=True, max_length=80)
    parent = models.ForeignKey('self', blank=True, null=True, related_name="children",
        help_text=_(
            'Categories, unlike tags, can have a hierarchy. You might have a '
            'Jazz category, and under that have children categories for Bebop'
            ' and Big Band. Totally optional.'),
        on_delete=models.CASCADE,
    )
    description = models.CharField(max_length=500, blank=True)
    
    menu_image = models.ForeignKey(
        get_image_model_string(),
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name=_('Menu Image'),
    )

    class Meta:
        ordering = ['name']
        verbose_name = _("Blog Category")
        verbose_name_plural = _("Blog Categories")

    panels = [
        FieldPanel('name'),
        FieldPanel('parent'),
        FieldPanel('description'),
        ImageChooserPanel('menu_image'),
    ]

    def __str__(self):
        return self.name

    def clean(self):
        if self.parent:
            parent = self.parent
            if self.parent == self:
                raise ValidationError('Parent category cannot be self.')
            if parent.parent and parent.parent == self:
                raise ValidationError('Cannot have circular Parents.')

    def save(self, *args, **kwargs):
        if not self.slug:
            unique_slugify(self, self.name)
        return super(BlogCategory, self).save(*args, **kwargs)


# Intermediate between Blog Category and Blog Page
class BlogCategoryBlogPage(models.Model):
    category = models.ForeignKey(
        'BlogCategory', related_name="+", verbose_name=_('Category'),
        on_delete=models.CASCADE,
    )

    page = ParentalKey('blog.BlogPage', related_name='categories')

    panels = [
        FieldPanel('category'),
    ]


# Intermediate between Blog Page and Blog Tag
class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('blog.BlogPage', related_name='tagged_items')


# Blog Tag
@register_snippet
class BlogTag(Tag):
    class Meta:
        verbose_name = _("Blog Tag")
        verbose_name_plural = _("Blog Tags")
        proxy = True


# Blog Tag Index Page
class BlogTagIndexPage(Page):

    def get_context(self, request):
        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['blogpages'] = blogpages
        return context

    class Meta:
        verbose_name = _('Blog Tag Index')


# Blog Page
class BlogPage(Page):
    body = StreamField([
        ('heading', blocks.CharBlock(icon='title', classname='full title')),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('embedded_video_sound', EmbedBlock(icon='media', label=_('Embed Video/Sound'))),
        ('code', CodeBlock(label='Code')),
        ('table', TableBlock()),
        ('html', blocks.RawHTMLBlock(icon='site', label=_('HTML'))),
        ('quote', QuoteBlock(icon='openquote')),
    ])
    tags = ClusterTaggableManager(through='blog.BlogPageTag', blank=True)
    date = models.DateField(
        _("Post date"), default=datetime.datetime.today,
        help_text=_("This date may be displayed on the blog post. It is not "
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
        related_name='author_pages',
    )

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    blog_categories = models.ManyToManyField('blog.BlogCategory', through='blog.BlogCategoryBlogPage', blank=True)

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
        MultiFieldPanel([
            FieldPanel('tags'),
            InlinePanel('categories', label=_("Categories")),
        ], heading="Tags and Categories"),
        ImageChooserPanel('header_image'),
        StreamFieldPanel('body', classname="full title"),
    ]

    def save_revision(self, *args, **kwargs):
        if not self.author:
            self.author = self.owner
        return super(BlogPage, self).save_revision(*args, **kwargs)

    def get_absolute_url(self):
        return self.url

    def get_blog_index(self):
        # Find closest ancestor which is a blog index
        return self.get_ancestors().type(BlogIndexPage).last()

    def get_context(self, request, *args, **kwargs):
        context = super(BlogPage, self).get_context(request, *args, **kwargs)
        context['blogs'] = self.get_blog_index().blogindexpage.blogs
        context = get_blog_context(context)
        context['COMMENTS_APP'] = settings.COMMENTS_APP
        return context

    class Meta:
        verbose_name = _('Blog Page')
        verbose_name_plural = _('Blog Pages')

    parent_page_types = ['blog.BlogIndexPage']
