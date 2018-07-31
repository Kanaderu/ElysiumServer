from django import template
from blog.models import *
from recipes.models import *

register = template.Library()

@register.inclusion_tag('tags/recipe_menus.html', takes_context=True)
def recipe_menus(context):
    return {
        'recipe_category' : RecipeCategory.objects.all().order_by('name')
    }