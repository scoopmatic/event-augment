import re
import sys
import sentencepiece as spm

sp = spm.SentencePieceProcessor()
if len(sys.argv) > 2:
        sp.Load(sys.argv[2])
else:
        sp.Load("sentpiece/m.model")


for dataset in ['train', 'devel', 'test']:
    with open("../game-report-generator/event2text/data/%s.input.pcs" % dataset, 'w') as out:
        for line in open("../game-report-generator/event2text/data/%s.input" % dataset):
            done = []
            ignore = False
            for part in line.split(' '):
                if part in ['<abbrevs>', '<goaltype>']:
                    ignore = True
                    done.append(part)
                    continue
                if part.startswith('<'):
                    if ignore:
                        ignore = False
                    done.append(part)
                elif ignore:
                    done.append(part)
                else:
                    done += sp.EncodeAsPieces(part)
            print(' '.join(done).strip(), file=out)


for dataset in ['train', 'devel', 'test']:
    with open("../game-report-generator/event2text/data/%s.output.pcs" % dataset, 'w') as out:
        for line in open("../game-report-generator/event2text/data/%s.output" % dataset):
            print(' '.join(sp.EncodeAsPieces(line.strip())).strip(), file=out)
