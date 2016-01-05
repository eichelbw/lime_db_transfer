import os
import sys
import getopt
import csv
from copy import deepcopy

from SurveyStructure import *

class MedEdNetToEDNATranslator:

    def __init__(self, structure_csv=None, response_csv=None, out=sys.stdout):
        if not structure_csv or not response_csv:
            self.prompt_user()
        else:
            self.survey_structure = SurveyStructure(structure_csv)
            self.responses = self.read_response_csv(response_csv)
        self.out = out
        self.conduct_checks()

    def prompt_user(self):
        ss_opts = [i for i in os.listdir(".") if i.startswith("limesurvey_survey")]
        r_opts = [i for i in os.listdir(".") if i.startswith("vvexport")]
        self.out.write("Survey Structure file? Here are some possibilities I found:")
        self.out.write("--> " + ", ".join(ss_opts))
        ss = raw_input("? >")
        self.out.write("Responses file? Here are some possibilities I found:")
        self.out.write("--> " + ", ".join(r_opts))
        resp = raw_input("? >")
        if not ss or not resp:
            raise UserWarning("You gotta give me some files, bro")
        else:
            MedEdNetToEDNATranslator(ss, resp)

    def read_response_csv(self, response_csv):
        with open(response_csv, 'rb') as inp:
            return list(csv.reader(inp, delimiter='\t'))

    def conduct_checks(self):
        # first, some preliminary checks
        headers = self.responses[:2]
        responses = self.responses[2:]
        for header in headers:
            try:
                header.remove("") # gets rid of pesky empty field
            except ValueError:
                continue
        for h in headers[1]:
            if len(h) > 22:
                self.out.write("""The question name '{}' is too long (>22
                characters) and may run into collision issues in LimeSurvey!
                Please choose a shorter question name and have another go."""
                .format(h))
                raise KeyboardInterrupt
        # headers/responses should all be the same length
        # unanswered question at end of response caused unevenness, hence this
        # check
        if len(headers[0]) != len(headers[1]):
            self.out.write("""Headers must be equal lengths. If this is not the
            case, something is likely fundementally wrong with the response
            export.""")
            raise ValueError
        for index, response in enumerate(responses):
            while len(response) < len(headers[0]):
                self.out.write("""Response at index {0} is shorter than expected
                ({1} < {2}). The script will pad this response with placeholders
                until length is correct, but you should likely look in to why
                this could be happening-- especially if you're seeing this
                message many times.""".format(index, len(response),
                        len(headers[0])))
                response.append("")

    def massage_header(self, headers):

        header_ignore = ["id", "token", "submitdate", "lastpage",
        "startlanguage", "startdate", "datestamp", "ipaddr", ""]

        new_headers = deepcopy(headers)
        offset = 0 # number of LS info columns (id, token, etc) to ignore
        for entry in headers[1]:
            if entry.strip() not in header_ignore:
                new_headers[0].append("")
                new_headers[1].append("responseStatus_{0}"
                    .format(entry.replace("_", "")))
            else:
                if not entry == "":
                    offset += 1
                continue
        return new_headers, offset

    def code_responses(self, responses, headers, offset):

        iql = self.survey_structure.indexed_question_list
        bad_response_key = ["NA", "N/A", "NOT AVAILABLE", "NONE", "?"]

        outp = []
        for response in responses:
            outl = deepcopy(response)
            for index, entry in enumerate(response[offset:]):
                # enumerate to check surveystructure for column specific actions
                if iql[index].parent_question_scale == "M":
                    if entry == "{question_not_shown}" or not entry:
                        outl.append("E222E")
                    elif entry =="Y":
                        outl.append("E111E")
                    else:
                        outl.append("E999E")
                elif iql[index].parent_question_scale == "L":
                    if not entry and "other" in iql[index].name:
                        outl.append("E222E")
                    elif not entry:
                        outl.append("E999E")
                    else:
                        outl.append("E111E")
                elif iql[index].parent_question_scale == ";":
                    if not entry:
                        outl.append("E999E")
                    else:
                        outl.append("E111E")
                elif iql[index].parent_question_logic:
                    if not entry:
                        outl.append("E777E")
                    else:
                        outl.append("E111E")
                elif entry.upper() in bad_response_key:
                    outl.append("E999E")
                elif not entry:
                    outl.append("E999E")
                elif isinstance(entry, basestring):
                    outl.append("E111E")
                else:
                    outl.append("E999E")
                    out.write(entry)
            outp.append(outl)
        return outp

    def write_responses(self):
        p1, offset = self.massage_header(self.responses[:2])
        p2 = self.code_responses(self.responses[2:], p1, offset)
        target = "translated_EDNA_" + self.survey_structure.sid + ".txt"
        with open(target, "wb") as f:
            w = csv.writer(f, delimiter='\t')
            w.writerows(p1 + p2)

    def console_repr(self):
        """utility function to show coded example response in the console"""
        p1, offset = self.massage_header(self.responses[:2])
        p2 = self.code_responses(self.responses[2:], p1, offset)
        # question.name:response>code
        for index, entry in enumerate(p2[0][offset:117+offset]):
            self.out.write(p1[1][index+offset]+":"+entry+">"+p2[0][offset+index+117])
