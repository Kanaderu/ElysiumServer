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
from ElysiumServer.models import QuoteBlock, STANDARD_BLOCKS

from taggit.models import TaggedItemBase, Tag
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from .utils import unique_slugify
import datetime

'''
# Helper function to get blog context
def get_recipe_context(context):
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
'''


# Recipe Index Page
class RecipeIndexPage(Page):
    @property
    def recipes(self):
        # Get list of recipe pages that are descendants of this page
        recipes = RecipePage.objects.descendant_of(self).live()
        recipes = recipes.order_by(
            '-date'
        ).select_related('owner').prefetch_related(
            'tagged_items__tag',
            'categories',
            'categories__category',
        )
        return recipes

    def get_context(self, request, tag=None, category=None, author=None, *args,
                    **kwargs):
        context = super(RecipeIndexPage, self).get_context(
            request, *args, **kwargs)
        recipes = self.recipes

        if tag is None:
            tag = request.GET.get('tag')
        if tag:
            recipes = recipes.filter(tags__slug=tag)
        if category is None:  # Not coming from category_view in views.py
            if request.GET.get('category'):
                category = get_object_or_404(RecipeCategory, slug=request.GET.get('category'))
        if category:
            if not request.GET.get('category'):
                category = get_object_or_404(RecipeCategory, slug=category)
            recipes = recipes.filter(categories__category__name=category)
        #if author:
        #    if isinstance(author, str) and not author.isdigit():
        #        recipes = recipes.filter(author__username=author)
        #    else:
        #        recipes = recipes.filter(author_id=author)

        # Pagination
        page = request.GET.get('page')
        page_size = 10
        if hasattr(settings, 'BLOG_PAGINATION_PER_PAGE'):
            page_size = settings.BLOG_PAGINATION_PER_PAGE

        paginator = None
        if page_size is not None:
            paginator = Paginator(recipes, page_size)  # Show 10 recipes per page
            try:
                recipes = paginator.page(page)
            except PageNotAnInteger:
                recipes = paginator.page(1)
            except EmptyPage:
                recipes = paginator.page(paginator.num_pages)

        context['recipes'] = recipes
        context['category'] = category
        context['tag'] = tag
        context['author'] = author
        context['COMMENTS_APP'] = settings.COMMENTS_APP
        context['paginator'] = paginator
        #context = get_blog_context(context)

        return context

    class Meta:
        verbose_name = _('Recipe Index')
    subpage_types = ['recipes.RecipePage']


class RecipeCategoryIndexPage(Page):
    @property
    def categories(self):
        # Get list of recipe pages that are descendants of this page
        categories = RecipeCategory.objects.all()
        categories = categories.order_by('name')
        return categories

    def get_context(self, request, tag=None, category=None, author=None, *args,
                    **kwargs):
        context = super(RecipeCategoryIndexPage, self).get_context(request, *args, **kwargs)

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
        context = get_blog_context(context)
        '''

        return context

    class Meta:
        verbose_name = _('Recipe Category Index')

# Recipe Category
@register_snippet
class RecipeCategory(models.Model):
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
        verbose_name = _("Recipe Category")
        verbose_name_plural = _("Recipe Categories")

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
        return super(RecipeCategory, self).save(*args, **kwargs)


# Intermediate between Recipe Category and Recipe Page
class RecipeCategoryRecipePage(models.Model):
    category = models.ForeignKey(
        'RecipeCategory', related_name="+", verbose_name=_('Category'),
        on_delete=models.CASCADE,
    )

    page = ParentalKey('recipes.RecipePage', related_name='categories')

    panels = [
        FieldPanel('category'),
    ]


# Recipe Tag
@register_snippet
class RecipeTag(Tag):
    class Meta:
        verbose_name = _("Recipe Tag")
        verbose_name_plural = _("Recipe Tags")
        proxy = True


# Intermediate between Recipe Page and Recipe Tag
class RecipePageTag(TaggedItemBase):
    content_object = ParentalKey('recipes.RecipePage', related_name='tagged_items')


# Recipe Page
class RecipePage(Page):
    ingredients = StreamField([
        ('title', blocks.CharBlock(icon='title', required=False)),
        ('ingredients_list', blocks.ListBlock(blocks.StructBlock([
            ('ingredient', blocks.CharBlock()),
        ]), icon='list-ul')),
    ], verbose_name=_("Ingredient List"))
    prep_time = models.TimeField(blank=True, null=True)
    cook_time = models.TimeField(blank=True, null=True)
    servings = models.IntegerField(blank=True, null=True)
    calories = models.IntegerField(blank=True, null=True)
    summary = StreamField(STANDARD_BLOCKS, blank=True, null=True)
    directions = StreamField(STANDARD_BLOCKS, blank=True, null=True)
    tags = ClusterTaggableManager(through='recipes.RecipePageTag', blank=True)
    date = models.DateField(
        _("Post date"), default=datetime.datetime.today,
        help_text=_("This date may be displayed on the recipe. It is not "
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
    author = models.CharField(max_length=255, default='author/source')

    search_fields = Page.search_fields + [
        index.SearchField('ingredients'),
        index.SearchField('summary'),
        index.SearchField('directions'),
    ]

    recipe_categories = models.ManyToManyField('recipes.RecipeCategory', through='recipes.RecipeCategoryRecipePage', blank=True)

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
        ImageChooserPanel('header_image'),
        MultiFieldPanel([
            FieldPanel('tags'),
            InlinePanel('categories', label=_("Categories")),
        ], heading="Tags and Categories"),
        MultiFieldPanel([
            FieldPanel('prep_time'),
            FieldPanel('cook_time'),
            FieldPanel('servings'),
            FieldPanel('calories'),
        ], heading="Timing and Stats"),
        StreamFieldPanel('summary'),
        StreamFieldPanel('ingredients'),
        StreamFieldPanel('directions', classname="full title"),
    ]

    def get_absolute_url(self):
        return self.url

    def get_recipe_index(self):
        # Find closest ancestor which is a recipes index
        return self.get_ancestors().type(RecipeIndexPage).last()

    def get_context(self, request, *args, **kwargs):
        context = super(RecipePage, self).get_context(request, *args, **kwargs)
        context['recipes'] = self.get_recipe_index().recipeindexpage.recipes
        #context = get_recipe_context(context)
        context['COMMENTS_APP'] = settings.COMMENTS_APP
        return context

    class Meta:
        verbose_name = _('Recipe Page')
        verbose_name_plural = _('Recipe Pages')

    parent_page_types = ['recipes.RecipeIndexPage']
