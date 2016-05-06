"""
Grades Transformer
"""
from openedx.core.lib.block_structure.transformer import BlockStructureTransformer
from lms.djangoapps.courseware.access_utils import check_start_date
from xmodule.course_metadata_utils import DEFAULT_START_DATE

from .utils import get_field_on_block


class GradesBlockTransformer(BlockStructureTransformer):
    """
    TODO: Write this.

    From StartDateTransformer:
    A transformer that enforces the 'start' and 'days_early_for_beta'
    fields on blocks by removing blocks from the block structure for
    which the user does not have access. The 'start' field on a
    block is percolated down to its descendants, so that all blocks
    enforce the 'start' field from their ancestors.  The assumed
    'start' value for a block is then the maximum of its parent and its
    own.

    For a block with multiple parents, the assumed parent start date
    value is a computed minimum of the start dates of all its parents.
    So as long as one parent chain allows access, the block has access.

    Staff users are exempted from visibility rules.
    """
    VERSION = 1

    FIELDS_TO_COLLECT = [u'graded', u'max_score', u'weight', u'has_score']

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
