import re

def detokenize(string):
    """ Simple detokenizer for hockey news """
    string = re.sub(r"(\d) - (\d)", r"\1-\2", string)
    string = re.sub(r"(\d) – (\d)", r"\1–\2", string)
    string = re.sub(r"(\d) — (\d)", r"\1—\2", string)
    string = re.sub(r"(.) (\.)", r"\1\2", string)
    string = re.sub(r"(.) (,)", r"\1\2", string)
    string = re.sub(r"(.) (:)", r"\1\2", string)
    string = re.sub(r"(:) (\w)", r"\1\2", string)
    string = re.sub(r"(.) (\?)", r"\1\2", string)
    string = re.sub(r"(.) (\!)", r"\1\2", string)
    string = re.sub(r"(.) (\))", r"\1\2", string)
    string = re.sub(r"(\() (.)", r"\1\2", string)
    string = re.sub(r"(.) - (.)", r"\1-\2", string)
    string = re.sub(r"-ja ", r"- ja ", string)
    return string
