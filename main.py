import sys
from MedEdNetToEDNATranslator import *

def user_command_line_prompt():
    """Allows user interaction with the script while maintaining testing"""
    return raw_input("? >")

def prompt_user(input_func, out):
    """Prompts user for LS files if not present in at instantiation.

    creates a new instance of the translator if correct files are specified
    """
    ss_opts = [i for i in os.listdir(".") if i.startswith("limesurvey_survey")]
    r_opts = [i for i in os.listdir(".") if i.startswith("vvexport")]
    out.write("Survey Structure file? Here are some possibilities I found:")
    out.write("--> " + ", ".join(ss_opts) + "\n")
    ss = input_func()
    out.write("Responses file? Here are some possibilities I found:")
    out.write("--> " + ", ".join(r_opts) + "\n")
    resp = input_func()
    if not ss or not resp:
        raise UserWarning("You gotta give me some files, bro")
    else:
        return MedEdNetToEDNATranslator(input_func, ss, resp, out)

def main(argv, input_func=user_command_line_prompt, out=sys.stdout):
    """Handles interaction on the command line, runs trans based on input.

    args:
    argv -- list of command line arguments/options.
            expected:
                --ss_txt/-s: limesurvey_survey_(sid).txt
                --vvexport_txt/-v: vvexport_(sid).txt
                --help/-h
    out -- testing utility (default system stdout)
    """
    ss_txt = ""
    vvexport_txt = ""
    try:
        opts, args = getopt.getopt(argv, "hs:v:", ["ss_txt=", "vvexport_txt="])
    except getopt.GetoptError:
        pass
    if opts:
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                out.write("""usage: MedEdNetToEDNATranslator.py
                -s <survey_structure>
                -v <vvexport>""")
                sys.exit()
            elif opt in ("-s", "--ss_txt"):
                ss_txt = arg
            elif opt in ("-v", "--vvexport_txt"):
                vvexport_txt = arg
    if ss_txt or vvexport_txt:
        if ss_txt:
            out.write("survey structure txt is {}".format(ss_txt))
        if  vvexport_txt:
            out.write("response vvexport txt is {}".format(vvexport_txt))
    else:
        prompt_user(input_func, out)
        return True
    trans = MedEdNetToEDNATranslator(input_func(), ss_txt, vvexport_txt, out)
    out.write("you'll find the result in {}".format(trans.survey_structure.sid))
    return True

if __name__ == "__main__":
    main(sys.argv[1:])
