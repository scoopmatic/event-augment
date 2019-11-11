import sys

# Penalize word repeats
for line in sys.stdin:
    if line.strip().startswith('-'):
        score, text = line.split('\t')
        words = text.strip().replace('-',' - ').split()
        for i, word in enumerate(words):
            for j, word2 in enumerate(words):
                if i==j or len(word.replace('–','')) <= 2:
                    continue
                if word2.startswith(word):
                    score = float(score.strip())-0.25
                    print(" %.4f\t%s" % (score, text), end="")
                    break
            if type(score) is float:
                break
        else:
            print(line, end="")
    else:
        print(line, end="")
