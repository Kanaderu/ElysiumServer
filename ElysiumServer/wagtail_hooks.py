from django.conf import settings

import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler
from wagtail.core import hooks
from django.templatetags.static import static
from django.utils.html import format_html
from draftjs_exporter.dom import DOM
from wagtail.admin.rich_text.converters.contentstate_models import Entity
from wagtail.admin.rich_text.converters.html_to_contentstate import AtomicBlockEntityElementHandler


def katex_entity_decorator(props):
    """
    Takes Draft.js ContentState and converts it to HTML for saving in the Database.
    """
    return DOM.create_element('div', {
        'data-katex-text': props['text'],
    })


class KaTeXEntityElementHandler(AtomicBlockEntityElementHandler):
    """
    Takes Database HTML and converts it to Draft.js ContentState for display in the editor.
    """
    mutability = 'MUTABLE'

    def create_entity(self, name, attrs, state, contentstate):
        return Entity('KATEX', 'IMMUTABLE', {
            'text': attrs['data-katex-text'],
        })


@hooks.register('insert_editor_css')
def editor_css():
    return format_html('<link rel="stylesheet" href="{}" />', static('css/all.css'))


@hooks.register('insert_editor_css')
def admin_editor_css():
    return format_html('<link rel="stylesheet" href="{}" />', static('css/ElysiumServer.css'))


# 1. Use the register_rich_text_features hook.
@hooks.register('register_rich_text_features')
def register_strikethrough_feature(features):
    """
    Registering the `strikethrough` feature, which uses the `STRIKETHROUGH` Draft.js inline style type,
    and is stored as HTML with an `<s>` tag.
    """
    feature_name = 'strikethrough'
    type_ = 'STRIKETHROUGH'
    tag = 's'

    # 2. Configure how Draftail handles the feature in its toolbar.
    control = {
        'type': type_,
        'icon': 'fas fa-strikethrough',
        'description': 'Strikethrough',
        'style': {'textDecoration': 'line-through'},
        #'style': {'textDecoration': 'line-through'},
        # This isn’t even required – Draftail has predefined styles for STRIKETHROUGH.
        # 'style': {'textDecoration': 'line-through'},
    }

    # 3. Call register_editor_plugin to register the configuration for Draftail.
    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.InlineStyleFeature(control)
    )

    # 4.configure the content transform from the DB to the editor and back.
    db_conversion = {
        'from_database_format': {tag: InlineStyleElementHandler(type_)},
        'to_database_format': {'style_map': {type_: tag}},
    }

    # 5. Call register_converter_rule to register the content transformation conversion.
    features.register_converter_rule('contentstate', feature_name, db_conversion)

    # 6. (optional) Add the feature to the default features list to make it available
    # on rich text fields that do not specify an explicit 'features' list
    features.default_features.append('strikethrough')


@hooks.register('register_rich_text_features')
def register_superscript_feature(features):
    feature_name = 'superscript'
    type_ = 'SUPERSCRIPT'
    tag = 'sup'

    control = {
        'type': type_,
        'icon': 'fa-superscript',
        'description': 'Superscript',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.InlineStyleFeature(control)
    )

    db_conversion = {
        'from_database_format': {tag: InlineStyleElementHandler(type_)},
        'to_database_format': {'style_map': {type_: tag}},
    }

    features.default_features.append(feature_name)
    features.register_converter_rule('contentstate', feature_name, db_conversion)


@hooks.register('register_rich_text_features')
def register_subscript_feature(features):
    feature_name = 'subscript'
    type_ = 'SUBSCRIPT'
    tag = 'sub'

    control = {
        'type': type_,
        'icon': 'fa-subscript',
        'description': 'Subscript',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.InlineStyleFeature(control)
    )

    db_conversion = {
        'from_database_format': {tag: InlineStyleElementHandler(type_)},
        'to_database_format': {'style_map': {type_: tag}},
    }

    features.default_features.append(feature_name)
    features.register_converter_rule('contentstate', feature_name, db_conversion)


@hooks.register('register_rich_text_features')
def register_monospace_feature(features):
    feature_name = 'monospace'
    type_ = 'CODE'
    tag = 'code'

    control = {
        'type': type_,
        'label': '{ }',
        'description': 'Monospace',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.InlineStyleFeature(control)
    )

    db_conversion = {
        'from_database_format': {tag: InlineStyleElementHandler(type_)},
        'to_database_format': {'style_map': {type_: tag}},
    }

    features.default_features.append(feature_name)
    features.register_converter_rule('contentstate', feature_name, db_conversion)


@hooks.register('register_rich_text_features')
def register_katex_feature(features):
    feature_name = 'katex'
    type_ = 'KATEX'

    control = {
        'type': type_,
        'label': '𝐊',
        'description': 'KaTeX',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.EntityFeature(control,
            js=[static('js/katex.min.js'),
                static('js/wagtail_draftail_katex.js'),
            ],
            css={
                'all': [
                    static('css/katex.min.css')
                ]
            }
        )
    )

    db_conversion = {
        'from_database_format': {'div[data-katex-text]': KaTeXEntityElementHandler()},
        'to_database_format': {'entity_decorators': {type_: katex_entity_decorator}},
    }

    features.default_features.append(feature_name)
    features.register_converter_rule('contentstate', feature_name, db_conversion)
