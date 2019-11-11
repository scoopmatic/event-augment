import re

for filename in ["output/manual_eval.html","output/manual_eval_oov.html"]:
    game_nr = 1
    with open(filename,'w') as out_file:
        with open(filename.replace('.html','_strip.txt'),'w') as txt_out_file:
            sents = []
            out_file.write('<pre>')
            for line in open(filename.replace('.html','.txt')):
                if line[0] == '<':
                    line = 'E: '+line
                    if '<type>result' in line:
                        line = ('--- %d.' % game_nr)+(' %s - %s ---\n\n' % re.findall("<home> (.+) </home> <guest> (.+) </guest>",line)[0]) +line
                        game_nr += 1
                    line = re.sub("<length>\w+</length>", "", line)
                    line = line.replace('>','&gt;').replace('<','&lt;')
                    line = re.sub(r" ?&lt;(\w+)&gt; ?", r"</b> \1:<b>", line)
                    line = re.sub(r"(&lt;/\w+&gt;)",r"", line)
                    line = "<b>"+line+"</b>"
                    out_file.write(line)#+'\n')
                    txt_out_file.write(re.sub("</?b>","",line))
                elif line == '\n':

                    for i, (score, sent) in enumerate(sents):
                        mark = ['S', 'M', 'L'][i]
                        sent = sent.strip().split('\t')[1]
                        if score == max([x[0] for x in sents]):
                            #out_file.write('\t%s: %s &#09;<b>%s</b>\n' % (mark, score, sent))
                            out_file.write('%s\n' % sent)
                            txt_out_file.write('%s\n' % sent)
                        else:
                            #out_file.write('%s: %s &#09;%s\n' % (mark, score, sent))
                            pass
                    print('', file=out_file)
                    print('', file=txt_out_file)
                    sents = []
                else:
                    score, sent = line.split('\t')
                    score = float(score.strip())
                    sents.append((score, line))
            out_file.write('</pre>')
