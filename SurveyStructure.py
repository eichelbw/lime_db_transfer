import csv
from itertools import count

class SurveyStructure:

    def __init__(self, structure_csv):
        self.structure_csv = structure_csv
        self.lol = self.read_structure_csv()
        self.q_groups = self.generate_question_groups()
        self.check_question_completeness()
        self.indexed_question_list = self.generate_i_q_list()

    def read_structure_csv(self):
        with open(self.structure_csv, "rb") as inp:
            lol = list(csv.reader(inp, delimiter="\t"))[1:]
        return lol

    def generate_question_groups(self):
        q_groups = []
        marks = []
        for index, line in enumerate(self.lol):
            if line[0] == "G":
                marks.append(index)
        for i in range(len(marks) - 1):
            # gets slices between the marks [...)
            q_groups.append(QuestionGroup(self.lol[marks[i]:marks[i + 1]]))
        q_groups.append(QuestionGroup(self.lol[marks[-1]:]))
        # gets last slice [...]
        return q_groups

    def check_question_completeness(self):
        for qg in self.q_groups:
            for q in qg.questions:
                q.check_scale()
        return True

    def generate_i_q_list(self):
        i_q_list = []
        for g in self.q_groups:
            for q in g.questions:
                if not q.has_subquestions():
                    i_q_list.append(q)
                elif q.scale == "L": # radio w second text 'other' column
                    i_q_list.append(q)
                    for sq in q.subquestions:
                        i_q_list.append(sq)
                else:
                    for sq in q.subquestions:
                        i_q_list.append(sq)
        return i_q_list

class QuestionGroup:

    def __init__(self, slice_of_survey_lol):
        self.slice_of_survey_lol = slice_of_survey_lol
        self.scale = slice_of_survey_lol[0][1]
        self.name = slice_of_survey_lol[0][2]
        self.text = slice_of_survey_lol[0][4]
        self.questions = self.populate_questions()

    def __repr__(self):
        return self.name

    def populate_questions(self):
        """
        first pass at getting questions set up. doesn't generate sq array for
        ;-type questions or pass question type to sq in general. those're done
        in SurveyStructure#check_question_completeness
        """
        questions = []
        for row in self.slice_of_survey_lol[1:]:
            if row[0] == "Q":
                params = row[1:5]
                q = Question(*params)
                if q.has_subquestions():
                    questions.append(q)
                else:
                    questions.append(q)
            elif row[0] == "SQ":
                params = [row[1], row[2], row[4], questions[-1]]
                questions[-1].subquestions.append(Subquestion(*params))
            elif row[0] == "A":
                params = [row[1], row[2], row[4]]
                questions[-1].answers.append(Answer(*params))
            else:
                print "found an unexpected row scale: {}".format(row[0])
        return questions

class Question:

    def __init__(self, scale, name, logic, text):
        self.scale = scale
        self.name = name
        self.logic = logic
        self.has_skip_logic = self.determine_logic(self.logic)
        self.text = text
        self.subquestions = []
        self.answers = []
        # the following attributes arn't DRY, but simplify tests and coding due
        # to iql structure
        self.parent_question_scale = scale
        self.parent_question_logic = self.has_skip_logic

    def __repr__(self):
        return self.name

    def determine_logic(self, logic_col):
        # true if this question isn't shown depending on previous answers
        if logic_col == "1" or not logic_col:
            return False
        else:
            return True

    def has_subquestions(self):
        if not self.subquestions:
            return False
        else:
            return True

    def check_scale(self):
        if self.scale == ";":
            self.semicolon_array_logic()
        else:
            self.finalize_sq_generation()
        return True

    def finalize_sq_generation(self):
        for sq in self.subquestions:
            new_name = "{0}_{1}".format(self.name, sq.name)
            sq.name = new_name
            sq.parent_question_type = self.scale
        return True

    def semicolon_array_logic(self):
        """ wow this is hacky.
        generates correct subquestions for ;-type LS questions. for some reason,
        the LS survey structure doesn't include all combinations for this
        question type, so we have to generate them.
        """
        sq0 = []
        sq1 = []
        new_subquestions = []
        for sq in self.subquestions:
            if sq.scale == "0":
                sq0.append(sq)
            elif sq.scale == "1":
                sq1.append(sq)
            else:
                print "unexpected subquesion scale: {}".format(sq.scale)
        for i in sq0:
            for j in sq1:
                new_name = "{0}_{1}_{2}".format(self.name, i.name, j.name)
                params = ["SQ", new_name, "", self]
                new_subquestions.append(Subquestion(*params))
        self.subquestions = new_subquestions
        return self.subquestions

class Subquestion:

    def __init__(self, scale, name, text, parent_question):
        self.scale = scale
        self.name = name
        self.text = text
        self.parent_question_scale = parent_question.scale
        self.parent_question_logic = parent_question.has_skip_logic

    def __repr__(self):
        return self.name

class Answer:

    def __init__(self, scale, name, text):
        self.scale = scale
        self.name = name
        self.text = text

if __name__ == "__main__":
    ss = SurveyStructure('limesurvey_survey_471745.txt')
    print ss.indexed_question_list
