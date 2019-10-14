import re
import sys
from detokenizer import detokenize

out = open("sentpiece_corpus.txt", 'w')
for dataset in ['train', 'devel', 'test']:
    for line in open("../game-report-generator/event2text/data/%s.input" % dataset):
        done = ""
        ignore = False
        for part in line.split(' '):
            if part in ['<abbrevs>', '<goaltype>']:
                ignore = True
                continue
            if part.startswith('<'):
                if ignore:
                    ignore = False
                pass
            elif ignore:
                pass
            else:
                done += part + ' '
        print(done.strip(), file=out)


for dataset in ['train', 'devel', 'test']:
    for line in open("../game-report-generator/event2text/data/%s.output" % dataset):
        print(detokenize(line.strip()), file=out)
