import re
import sys
import sentencepiece as spm

sp = spm.SentencePieceProcessor()
if len(sys.argv) > 3:
        sp.Load(sys.argv[3])
else:
        sp.Load("sentpiece/m.model")

path = sys.argv[1] # ../game-report-generator/event2text/data/
suffix = sys.argv[2] # "" / ".aug"

for dataset in ['train', 'devel', 'test']:
    with open("%s%s.input%s.pcs" % (path,dataset,suffix), 'w') as out:
        for line in open("%s%s.input%s" % (path,dataset,suffix)):
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
    with open("%s%s.output%s.pcs" % (path,dataset,suffix), 'w') as out:
        for line in open("%s%s.output%s" % (path,dataset,suffix)):
            print(' '.join(sp.EncodeAsPieces(line.strip())).strip(), file=out)
