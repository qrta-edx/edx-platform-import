"""
Test the behavior of the GradesTransformer
"""

from student.tests.factories import UserFactory

from ...api import get_course_blocks
from ..grades import GradesBlockTransformer
from .helpers import CourseStructureTestCase


class GradesBlockTransformerTestCase(CourseStructureTestCase):
    """
    Verify behavior of the GradesBlockTransformer
    """

    course_dict = [
        {
            u'org': u'GradesBlockTestOrg',
            u'course': u'GB101',
            u'run': u'cannonball',
            u'#type': u'course',
            u'#ref': u'course',
            u'#children': [
                {
                    u'metadata': {
                        u'graded': True,
                        u'max_score': 10,
                        u'weight': 1,
                        u'has_score': True,
                    },
                    u'#type': u'problem',
                    u'#ref': u'problem_1',

                },
                {
                    u'metadata': {
                        u'graded': False,
                        u'max_score': 5,
                        u'weight': 2,
                        u'has_score': True,
                    },
                    u'#type': u'problem',
                    u'#ref': u'problem_2',
                },
            ],
        },
    ]

    TRANSFORMER_CLASS_TO_TEST = GradesBlockTransformer

    def setUp(self):
        super(GradesBlockTransformerTestCase, self).setUp()
        self.blocks = self.build_course(self.course_dict)
        self.course = self.blocks[u'course']

    def test_asdkljgasdgkjsfhdglkjsfghlksafglkjz(self):
        pass

    def test_grades_collected(self):
        password = u'test'
        student = UserFactory.create(is_staff=False, username=u'test_student', password=password)
        #staff = UserFactory.create(is_staff=True, username=u'test_staff', password=password)

        self.client.login(username=student.username, password=password)
        block_structure = get_course_blocks(student, self.course.location, self.transformers)

        problem_expectations = self.course_dict[0][u'#children']
        for problem, expected_result in [
                (self.blocks[u'problem_1'], problem_expectations[0]),
                (self.blocks[u'problem_2'], problem_expectations[1]),
        ]:
            for field in [u'weight', u'graded', u'has_score']:  # u'max_score fails
                self.assertEqual(
                    block_structure.get_xblock_field(problem.location, field),
                    expected_result[u'metadata'].get(field)
                )
