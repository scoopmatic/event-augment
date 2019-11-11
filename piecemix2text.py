import re
import sys

for row in sys.stdin:
    parts = row.split()
    out = []
    in_text_tag = False
    for part in parts:
        if re.search("(<\w+>\w+</\w+>)", part):
            out.append(part)
            in_text_tag = False
        elif re.search("<\w+>", part):
            if part != '<goaltype>':
                in_text_tag = True
            out.append(part)
            text = []
        elif re.search("</\w+>", part):
            in_text_tag = False
            if text:
                out.append(''.join(text).replace('▁',' ').strip())
            out.append(part)
        else:
            if in_text_tag:
                text.append(part)
            else:
                out.append(part)
    print(' '.join(out))
