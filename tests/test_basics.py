"""
Markdown XBlock tests
"""
from __future__ import print_function

import unittest

from mock import Mock, patch
from xblock.field_data import DictFieldData
from xblock.test.tools import TestRuntime

import markdown_xblock
from markdown_xblock.html import DEFAULT_EXTRAS


class TestMarkdownXBlock(unittest.TestCase):
    """
    Unit tests for `markdown_xblock`
    """
    def setUp(self):
        self.runtime = TestRuntime()

    def test_render(self):
        """
        Test a basic rendering with default settings.
        """
        field_data = DictFieldData({'data': '# This is h1'})
        block = markdown_xblock.MarkdownXBlock(self.runtime, field_data, None)
        fragment = block.student_view()
        self.assertIn('<div class="markdown_block"><h1>This is h1</h1>\n</div>\n', fragment.content)

    def test_render_with_unsafe(self):
        """
        Test a basic rendering with default settings.
        Expects the content to be sanitized.
        """
        field_data = DictFieldData({'data': '<h1>This is h1</h1>'})
        block = markdown_xblock.MarkdownXBlock(self.runtime, field_data, None)
        fragment = block.student_view()
        self.assertIn(
            '<div class="markdown_block"><p>[HTML_REMOVED]This is h1[HTML_REMOVED]</p>\n</div>\n',
            fragment.content
        )

    def test_render_allow_inline_html(self):
        """
        Test a basic rendering with javascript enabled.
        Expects the content *not* to be sanitized.
        """
        field_data = DictFieldData({'data': '<h1>This is h1</h1>'})
        block = markdown_xblock.MarkdownXBlock(self.runtime, field_data, None)
        settings = {
            "extras": DEFAULT_EXTRAS,
            "safe_mode": False
        }
        with patch('markdown_xblock.html.get_xblock_settings') as get_settings_mock:
            get_settings_mock.return_value = settings
            fragment = block.student_view()
            self.assertIn('<div class="markdown_block"><h1>This is h1</h1>\n</div>\n',
                          fragment.content)

    def test_substitution_no_system(self):
        """
        Test that the substitution is not performed when `system` is not present inside XBlock.
        """
        field_data = DictFieldData({'data': '%%USER_ID%% %%COURSE_ID%%'})
        block = markdown_xblock.MarkdownXBlock(self.runtime, field_data, None)
        fragment = block.student_view()
        self.assertIn('<div class="markdown_block"><p>%%USER_ID%% %%COURSE_ID%%</p>\n</div>\n', fragment.content)

    def test_substitution_not_found(self):
        """
        Test that the keywords are not replaced when they're not found.
        """
        field_data = DictFieldData({'data': 'USER_ID%% %%COURSE_ID%%'})
        block = markdown_xblock.MarkdownXBlock(self.runtime, field_data, None)
        block.system = Mock(anonymous_student_id=None)
        fragment = block.student_view()
        self.assertIn('<div class="markdown_block"><p>USER_ID%% %%COURSE_ID%%</p>\n</div>\n', fragment.content)

    def test_user_id_substitution(self):
        """
        Test replacing %%USER_ID%% with anonymous user ID.
        """
        field_data = DictFieldData({'data': '%%USER_ID%%'})
        block = markdown_xblock.MarkdownXBlock(self.runtime, field_data, None)
        block.system = Mock(anonymous_student_id='test_user')
        fragment = block.student_view()
        self.assertIn('<div class="markdown_block"><p>test_user</p>\n</div>\n', fragment.content)

    def test_course_id_substitution(self):
        """
        Test replacing %%COURSE_ID%% with HTML representation of course key.
        """
        field_data = DictFieldData({'data': '%%COURSE_ID%%'})
        block = markdown_xblock.MarkdownXBlock(self.runtime, field_data, None)
        course_locator_mock = Mock()
        course_locator_mock.html_id = Mock(return_value='test_course')
        block.system = Mock(course_id=course_locator_mock)
        fragment = block.student_view()
        self.assertIn('<div class="markdown_block"><p>test_course</p>\n</div>\n', fragment.content)
