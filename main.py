import sys
from MedEdNetToEDNATranslator import *

def main(argv, out=sys.stdout):
    ss_txt = ""
    vvexport_txt = ""
    try:
        opts, args = getopt.getopt(argv, "hs:v:", ["ss_txt=", "vvexport_txt="])
    except getopt.GetoptError:
        pass
    for opt, arg in opts:
        if opt == "-h":
            out.write("""usage: MedEdNetToEDNATranslator.py
            -s <survey_structure>
            -v <vvexport>""")
            sys.exit()
        elif opt in ("-s", "--ss_txt"):
            ss_txt = arg
        elif opt in ("-v", "--vvexport_txt"):
            vvexport_txt = arg
    if ss_txt and vvexport_txt:
        sys.write("survey structure txt is {}".format(ss_txt))
        sys.write("response vvexport txt is {}".format(vvexport_txt))
        trans = MedEdNetToEDNATranslator(ss_txt, vvexport_txt, out)
        sys.write("you'll find the result in {}"
                .format(trans.survey_structure.sid))

if __name__ == "__main__":
    main(sys.argv[1:])
