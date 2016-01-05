import sys
import unittest
from StringIO import StringIO
from MedEdNetToEDNATranslator import *
from SurveyStructure import *
import main

class TestMedEdNetToEDNATranslator(unittest.TestCase):

    def setUp(self):
        self.trans = MedEdNetToEDNATranslator('limesurvey_survey_471745.txt',
                'vvexport_471745.txt')

    def tearDown(self):
        self.trans = None

    def test_init(self):
        self.assertIsInstance(self.trans.survey_structure, SurveyStructure)
        self.assertEqual(len(self.trans.survey_structure.indexed_question_list),
                117, "survey_structure should be correctly populated")
        self.assertIsInstance(self.trans.responses, list)

    def test_massage_header(self):
        n_h, offset = self.trans.massage_header(self.trans.responses[:2])
        self.assertEqual(offset, 5, "offset should be 5, got {}".format(offset))
        self.assertEqual(len(n_h), 2, "should only be two headers")
        self.assertEqual(len(n_h[0]), 239,
                "header len should be 239, got {}".format(len(n_h[0])))
        self.assertEqual(len(n_h[0]), len(n_h[1]), "headers should be same len")
        self.assertEqual(n_h[1][offset:117+offset],
                [q.name for q in self.trans.survey_structure.indexed_question_list],
                "indexed question list should equal offset old header[1]")
        for i, q in enumerate(self.trans.survey_structure.indexed_question_list):
            self.assertEqual("responseStatus_" + q.name.replace("_", ""),
                    n_h[1][117 + offset + i],
                    "responseStatus_{0} != {1}".format(q.name.replace("_", ""),
                        n_h[1][117 + offset + i]))

    def test_code_responses(self):
        code_list = ["E111E", "E222E", "E444E", "E555E", "E777E", "E888E",
                "E999E"]
        bad_response_key = ["NA", "N/A", "NOT AVAILABLE", "NONE", "?"]

        iql = self.trans.survey_structure.indexed_question_list
        n_h, offset = self.trans.massage_header(self.trans.responses[:2])
        outp = self.trans.code_responses(self.trans.responses[2:], n_h, offset)
        self.assertEqual(len(outp), 24,
                "should be 24 responses, got {}".format(len(outp)))
        for resp in outp:
            self.assertEqual(len(resp), 239,
                    "response len should be 239, got {}, {}".format(len(resp), resp))
            for ans in resp[117+offset:]:
                self.assertIn(ans, code_list, "each question should be coded")
            for index, ans in enumerate(resp[offset:offset+117]):
                # if not ans:
                if iql[index].parent_question_scale == "M":
                    if not ans:
                        self.assertEqual(resp[index + offset + 117], "E222E",
                                "blanks in M-type questions should be 222")
                elif iql[index].parent_question_scale == "L":
                    if not ans and "other" in iql[index].name:
                        self.assertEqual(resp[index + offset + 117], "E222E",
                                "blank response for other SQ of L-type Q should be 222")
                    elif not ans:
                        self.assertEqual(resp[index + offset + 117], "E999E",
                                "missing answers should be marked 999")
                    else:
                        self.assertEqual(resp[index + offset + 117], "E111E",
                                "answered Qs should be marked 111")
                elif iql[index].parent_question_scale == ";":
                    if not ans:
                        self.assertEqual(resp[index + offset + 117], "E999E",
                                "missing ans for ;-type should be 999")
                    if ans.upper() in bad_response_key:
                        self.assertEqual(resp[index + offset + 117], "E111E",
                               """variations on 'n/a' should be coded as 111
                                for ;-type questions (LoT 1.1)""")
                elif iql[index].parent_question_logic:
                    if not ans:
                        self.assertEqual(resp[index + offset + 117], "E777E",
                                "unanswered Qs w skip logic should be 777")
                else:
                    if not ans:
                        self.assertEqual(resp[index + offset + 117], "E999E",
                                """
                                missing answers should be marked 999. offending
                                result: {}:{}>{}
                                """
                                .format(iql[index],ans,resp[index + offset + 117]))
                    else:
                        self.assertEqual(resp[index + offset + 117], "E111E",
                               """answered questions should be marked 111""")

class TestSS(unittest.TestCase):

    def setUp(self):
        self.ss = SurveyStructure('limesurvey_survey_471745.txt')

    def tearDown(self):
        self.ss = None

    def test_ss_init(self):
        self.assertNotEqual(self.ss.lol[0][0], "class", "should drop header")
        self.assertEqual(len(self.ss.q_groups), 6,
                "should be six question groups")
        self.assertEqual(len(self.ss.q_groups[0].questions), 2)
        self.assertEqual(len(self.ss.q_groups[1].questions), 5)
        self.assertEqual(len(self.ss.q_groups[2].questions), 7)
        self.assertEqual(len(self.ss.q_groups[3].questions), 3)
        self.assertEqual(len(self.ss.q_groups[4].questions), 2)
        self.assertEqual(len(self.ss.q_groups[5].questions), 5)
        self.assertEqual(len(self.ss.indexed_question_list), 117,
                "wrong number of questions")

    def test_semicolon_sq_generation(self):
        self.assertEqual(len(self.ss.q_groups[1].questions[0].subquestions), 24)
        self.assertListEqual(self.ss.q_groups[1].questions[0].answers, [])
        for sq in self.ss.q_groups[1].questions[0].subquestions:
            self.assertEqual(sq.scale, "SQ", "sq scale incorrect")
            self.assertEqual(sq.parent_question_scale, ";",
                    "parent scale wrong")
            self.assertEqual(sq.parent_question_logic, False,
                    "parent logic wrong")

    def test_L_w_other_scale_question_handling(self):
        self.assertIn("other",
                self.ss.q_groups[1].questions[3].subquestions[0].name)
        self.assertIsNotNone(self.ss.q_groups[1].questions[3].answers)
        self.assertIn("ClinOwnrshpType_other",
                [q.name for q in self.ss.indexed_question_list])

    def test_M_scale_question_handling(self):
        q = self.ss.q_groups[1].questions[4]
        self.assertEqual(len(q.subquestions), 13, "M type has subquestions")
        self.assertListEqual(q.answers, [], "M type has no answers")
        self.assertEqual(q.subquestions[-1].name, "TypesOnTeam_other",
                "should have other")

    def test_question_with_simple_skip_logic(self):
        q = self.ss.q_groups[2].questions[4] # EHRInfo
        self.assertTrue(q.has_skip_logic, "question should have skip logic")

    def test_yn_no_logic(self):
        # simple y/n question, no skip logic
        q = Question("Y", "YNQuestion", "", "a test y/n question")
        self.assertEqual(q.scale, "Y", "scale should be Y")
        self.assertEqual(q.name, "YNQuestion", "name should be YNQuestion")
        self.assertEqual(q.has_skip_logic, False, "shouldnt have skip logic")
        self.assertEqual(q.text, "a test y/n question", "text is wrong")
        self.assertListEqual(q.subquestions, [], "should have no subquestions")
        self.assertListEqual(q.answers, [], "should have no answers")

class CommandLineTestCase(unittest.TestCase):
    def test_with_empty_arguments(self):
        """should start the input prompt routine"""
        out = StringIO()
        main.main([], out)
        output = out.getvalue().strip()
        self.assertNotEqual(output, "","{}".format(output))


class TestAnswer(unittest.TestCase):

    def test_init(self):
        ans = Answer("","","")
        self.assertEqual(ans.name, "")
        self.assertEqual(ans.text, "")
        self.assertEqual(ans.scale, "")

if __name__ == "__main__":
    unittest.main(buffer=True)
