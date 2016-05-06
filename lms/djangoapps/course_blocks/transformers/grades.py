"""
Grades Transformer
"""
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
        # get max_score from lms/djangoapps/courseware/grades.py:MaxScoreCache
