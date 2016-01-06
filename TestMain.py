import unittest
from StringIO import StringIO

from main import main

class CommandLineTestCase(unittest.TestCase):
    def test_with_empty_arguments(self):
        """should start the input prompt routine"""
        out = StringIO()
        m = main([], lambda:"test", out)
        output = out.getvalue().strip()
        self.assertNotEqual(output, "", "there should be an output")

