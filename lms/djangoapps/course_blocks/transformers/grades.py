"""
Grades Transformer
"""
from django.contrib.auth.models import User
from django.test.client import RequestFactory

from lms.djangoapps.courseware import module_render
from openedx.core.lib.block_structure.transformer import BlockStructureTransformer

class GradesBlockTransformer(BlockStructureTransformer):
    """
    """
    VERSION = 1

    FIELDS_TO_COLLECT = [u'graded', u'weight', u'has_score']

    @classmethod
    def name(cls):
        """
        Unique identifier for the transformer's class;
        same identifier used in setup.py.
        """
        return u'grades'

    @classmethod
    def collect(cls, block_structure):
        """
        Collects any information that's necessary to execute this
        transformer's transform method.
        """
        block_structure.request_xblock_fields(*cls.FIELDS_TO_COLLECT)

        # get max_score from XModule/XBlock.  Need Context w/ user.
        cls.collect_max_scores(block_structure)

    @staticmethod
    def _iter_xmodules(block_structure):
        request = RequestFactory().get('/dummy-collect-max-grades')
        request.user = User.objects.get(pk=1)
        request.session = {}
        for block_locator in block_structure.topological_traversal():
            course_id = unicode(block_locator.course_key)
            usage_id = block_locator._to_deprecated_string()
            module, __ = module_render.get_module_by_usage_id(request, course_id, usage_id)
            yield module

    @classmethod
    def collect_max_scores(cls, block_structure):
        for module in cls._iter_xmodules(block_structure):
            cls._collect_max_score(block_structure, module)

    @classmethod
    def _collect_max_score(cls, block_structure, module):
        score = module.max_score()
        block_structure.set_transformer_block_field(module.location, cls, 'max_score', score)

    def transform(self, block_structure, usage_context):
        pass
