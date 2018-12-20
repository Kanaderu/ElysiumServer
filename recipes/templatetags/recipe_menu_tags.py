from django import template
from recipes.models import *
register = template.Library()


@register.inclusion_tag('tags/recipe_menu.html', takes_context=True)
def recipe_menu(context):
    sorted_categories_by_group_index = RecipeCategory.objects.all().order_by('-group_index')
    num_groups = sorted_categories_by_group_index[0].group_index
    return {
        'recipe_categories': RecipeCategory.objects.all().order_by('group_index'),
        'num_groups': num_groups
    }


@register.inclusion_tag('tags/recipe_aside_menu.html', takes_context=True)
def recipe_aside_menu(context):
    sorted_categories_by_group_index = RecipeCategory.objects.all().order_by('-group_index')
    num_groups = sorted_categories_by_group_index[0].group_index
    return {
        'recipe_categories': RecipeCategory.objects.all().order_by('group_index'),
        'num_groups': num_groups
    }
