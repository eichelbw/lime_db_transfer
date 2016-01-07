import os
import unittest
import mock
from StringIO import StringIO

from main import *

class CommandLineTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        if "translated_EDNA_471745.txt" in os.listdir("."):
            os.remove("translated_EDNA_471745.txt")

    def test_with_repeated_empty_arguments(self):
        """should warn the user and exit"""
        mkr = mock.Mock(side_effect=["",""])
        out = StringIO()
        with self.assertRaises(UserWarning):
            m = main([], mkr, out)

    def test_with_initially_empty_arguments(self):
        """should prompt user_for files, then proceed"""
        mkr = mock.Mock(side_effect=["limesurvey_survey_471745.txt",
            "vvexport_471745.txt"])
        out = StringIO()
        trans = main([], mkr, out)
        self.assertEqual(trans.survey_structure.sid, "471745",
                "should produce trans")
        self.assertIn("translated_EDNA_471745.txt", os.listdir("."),
                "should write output")

    def test_with_initially_incomplete_arguments(self):
        """should prompt user_for files, then proceed"""
        mkr = mock.Mock(side_effect=["vvexport_471745.txt"])
        out = StringIO()
        trans = main(["-s limesurvey_survey_471745.txt"], mkr, out)
        self.assertTrue("survey structure txt is limesurvey_survey_471745.txt"
                in out.getvalue())
        mkr = mock.Mock(side_effect=["limesurvey_survey_471745.txt"])
        out = StringIO()
        trans = main(["-v vvexport_471745.txt"], mkr, out)
        self.assertTrue("response vvexport txt is vvexport_471745.txt"
                in out.getvalue())
        self.assertIn("translated_EDNA_471745.txt", os.listdir("."))
