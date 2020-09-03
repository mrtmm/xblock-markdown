"""This XBlock help creating a secure and easy-to-use HTML blocks in edx-platform."""

import logging

import markdown2
import pkg_resources
from django.conf import settings as django_settings
from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.settings import XBlockWithSettingsMixin
from xblockutils.studio_editable import StudioEditableXBlockMixin, loader

from .utils import _

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
xblock_loader = ResourceLoader(__name__)  # pylint: disable=invalid-name

SETTINGS_KEY = 'markdown'
DEFAULT_EXTRAS = [
    "code-friendly",
    "fenced-code-blocks",
    "footnotes",
    "tables",
    "use-file-vars"
]
DEFAULT_SETTINGS = {
    "extras": DEFAULT_EXTRAS,
    "safe_mode": True
}


def get_xblock_settings():
    """Extract xblock settings."""
    try:
        xblock_settings = django_settings.XBLOCK_SETTINGS
        settings = xblock_settings.get(
            SETTINGS_KEY, DEFAULT_SETTINGS)
    except AttributeError:
        settings = DEFAULT_SETTINGS

    return settings


@XBlock.wants('settings')
class MarkdownXBlock(StudioEditableXBlockMixin, XBlockWithSettingsMixin, XBlock):
    """
    This XBlock provides content editing in Markdown and displays it in HTML.
    """

    display_name = String(
        display_name=_('Display Name'),
        help=_('The display name for this component.'),
        scope=Scope.settings,
        default=_('Markdown')
    )
    data = String(
        help=_('The Markdown content for this module'),
        default=u'',
        scope=Scope.content
    )
    editor = 'markdown'
    editable_fields = ('display_name',)

    @staticmethod
    def resource_string(path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode('utf8')

    @XBlock.supports('multi_device')
    def student_view(self, context=None):  # pylint: disable=unused-argument
        """
        Return a fragment that contains the html for the student view.
        """
        frag = Fragment()
        frag.content = xblock_loader.render_django_template('static/html/lms.html', {'self': self})

        frag.add_css(self.resource_string('public/plugins/codesample/css/prism.css'))
        frag.add_javascript(self.resource_string('public/plugins/codesample/js/prism.js'))

        frag.add_css(self.resource_string('static/css/pygments.css'))

        return frag

    def studio_view(self, context=None):  # pylint: disable=unused-argument
        """
        Return a fragment that contains the html for the Studio view.
        """
        frag = Fragment()
        settings_fields = self.get_editable_fields()
        settings_page = loader.render_django_template('templates/studio_edit.html', {'fields': settings_fields})
        context = {
            'self': self,
            'settings_page': settings_page,
        }

        frag.content = xblock_loader.render_django_template('static/html/studio.html', context)

        self.add_stylesheets(frag)
        self.add_scripts(frag)

        js_data = {
            'editor': self.editor,
            'skin_url': self.runtime.local_resource_url(self, 'public/skin'),
            'external_plugins': self.get_editor_plugins()
        }
        frag.initialize_js('MarkdownXBlock', js_data)

        return frag

    @XBlock.json_handler
    def update_content(self, data, suffix=''):  # pylint: disable=unused-argument
        """
        Update the saved HTML data with the new HTML passed in the JSON 'content' field.
        """
        self.data = data['content']

        return {'content': self.data}

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ('MarkdownXBlock',
             """<vertical_demo>
                    <markdown data="
                        # This is h1
                        ## This is h2
                        ```
                        This is a code block
                        ```
                        * This is
                        * an unordered
                        * list
                        This is a regular paragraph
                        1. This is
                        1. an ordered
                        1. list
                        *This is italic*
                        **This is bold**
                    "/>
                </vertical_demo>
             """),
        ]

    def add_stylesheets(self, frag):
        """
        A helper method to add all necessary styles to the fragment.
        :param frag: The fragment that will hold the scripts.
        """
        frag.add_css(self.resource_string('static/css/html.css'))

        frag.add_css(self.resource_string('public/plugins/codemirror/codemirror-4.8/lib/codemirror.css'))

    def add_scripts(self, frag):
        """
        A helper method to add all necessary scripts to the fragment.
        :param frag: The fragment that will hold the scripts.
        """
        frag.add_javascript(self.resource_string('static/js/tinymce/tinymce.min.js'))
        frag.add_javascript(self.resource_string('static/js/tinymce/themes/modern/theme.min.js'))
        frag.add_javascript(self.resource_string('static/js/html.js'))
        frag.add_javascript(loader.load_unicode('public/studio_edit.js'))

        code_mirror_dir = 'public/plugins/codemirror/codemirror-4.8/'

        frag.add_javascript(self.resource_string(code_mirror_dir + 'lib/codemirror.js'))
        frag.add_javascript(self.resource_string(code_mirror_dir + 'mode/markdown/markdown.js'))

    def get_editor_plugins(self):
        """
        This method will generate a list of external plugins urls to be used in TinyMCE editor.
        These plugins should live in `public` directory for us to generate URLs for.

        const PLUGINS_DIR = "/resource/html5/public/plugins/";
        const EXTERNAL_PLUGINS = PLUGINS.map(function(p) { return PLUGINS_DIR + p + "/plugin.min.js" });

        :return: A list of URLs
        """
        plugin_path = 'public/plugins/{plugin}/plugin.min.js'
        plugins = ['codesample', 'image', 'link', 'lists', 'textcolor', 'codemirror']

        return {
            plugin: self.runtime.local_resource_url(self, plugin_path.format(plugin=plugin)) for plugin in plugins
        }

    def substitute_keywords(self, html):
        """
        Replaces all %%-encoded words using KEYWORD_FUNCTION_MAP mapping functions.

        Iterates through all keywords that must be substituted and replaces them by calling the corresponding functions
        stored in `keywords`. If the function throws a specified exception, the substitution is not performed.

        Functions stored in `keywords` must either:
            - return a replacement string
            - throw `KeyError` or `AttributeError`, `TypeError`.
        """
        data = html
        system = getattr(self, 'system', None)
        if not system:  # This shouldn't happen, but if `system` is missing, then skip substituting keywords.
            return data

        keywords = {
            '%%USER_ID%%': lambda: getattr(system, 'anonymous_student_id'),
            '%%COURSE_ID%%': lambda: getattr(system, 'course_id').html_id(),
        }

        for key, substitutor in keywords.items():
            if key in data:
                try:
                    data = data.replace(key, substitutor())
                except (KeyError, AttributeError, TypeError):
                    # Do not replace the keyword when substitutor is not present.
                    pass

        return data

    @property
    def html(self):
        """
        A property that returns the markdown content data as html.
        """
        settings = get_xblock_settings()
        extras = settings.get("extras", DEFAULT_EXTRAS)
        safe_mode = settings.get("safe_mode", True)

        html = markdown2.markdown(
            self.data,
            extras=extras,
            safe_mode=safe_mode
        )

        html = self.substitute_keywords(html)

        return html

    def get_editable_fields(self):
        """
        This method extracts the editable fields from this XBlock and returns them after validating them.

        Part of this method's copied from StudioEditableXBlockMixin#submit_studio_edits
        with some modifications..
        :return: A list of the editable fields with the information that
                the template needs to render a form field for them.

        """
        fields = []

        # Build a list of all the fields that can be edited:
        for field_name in self.editable_fields:
            field = self.fields[field_name]  # pylint: disable=unsubscriptable-object
            assert field.scope in (Scope.content, Scope.settings), (
                'Only Scope.content or Scope.settings fields can be used with '
                'StudioEditableXBlockMixin. Other scopes are for user-specific data and are '
                'not generally created/configured by content authors in Studio.'
            )
            field_info = self._make_field_info(field_name, field)
            if field_info is not None:
                fields.append(field_info)

        return fields
