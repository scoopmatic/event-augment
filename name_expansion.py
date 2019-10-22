import re
import random
import string

EXPANSION_RATE = 20

firstnames = {'Aatu', 'Annukka', 'Balazs', 'Eero', 'Hannu', 'Ilari', 'Jani', 'Janne', 'Jarkko', 'Jason', 'Joonas', 'Juha', 'Jukka', 'Jussi', 'Kai', 'Lennart', 'Maija', 'Matt', 'Miikka', 'Mikko', 'Niclas', 'Niko', 'Patrick', 'Philip', 'Rico', 'Saku', 'Sami', 'Samuli', 'Semir', 'Stefan', 'Steve', 'Thomas', 'Tony', 'Tuulia', 'Ville'}

for dataset in ['train','devel','test']:
    print("Preparing %s set..." % dataset)
    aug_input = open("data/%s.input.aug" % dataset,'w')
    aug_output = open("data/%s.output.aug" % dataset,'w')

    prevs = set()
    for input, output in zip(open("data/%s.input" % dataset), open("data/%s.output" % dataset)):
        names = []
        # Teams
        names += re.findall("<team> ([\w \-]+) \*\*", input)
        names += re.findall("<home> ([\w \-]+) </home>", input)
        names += re.findall("<guest> ([\w \-]+) </guest>", input)
        names += re.findall("<player> ([\w \-]+) </player>", input)
        names += re.findall("<assist> ([\w \-]+) </assist>", input)
        names += [x for xx in re.findall("<assist> ([\w \-]+) , ([\w \-]+) </assist>", input) for x in xx] # flatten list of tuples

        #print()
        #print(names)
        output = output.strip()
        input_subst = []
        for name in names:
            if name == 'None':
                continue
            for cutoff in range(0, len(name)*-1, -1):
                if cutoff == 0 or len(name) <= 3:
                    cutoff = None
                if len(name[:cutoff]) <= 2:
                    input_subst.append((name, name)) # Not in output
                    break

                # Collect first name candidates
                """try:
                    match = re.search(r"(%s)"%name[:cutoff], output)
                    prev = output[:match.span()[0]].split()[-1]
                    if prev[0].isupper() and prev[1:].islower() and prev not in names:
                        prevs.add(prev)
                except:
                    pass"""

                if re.search(r"(%s)"%name[:cutoff], output):
                    input_subst.append((name, name[:cutoff]))
                    break
            else:
                input_subst.append((name, name)) # Not in output

        #print(input_subst)
        print(input.strip(), file=aug_input)
        print(output.strip(), file=aug_output)
        for e in range(EXPANSION_RATE):
            spoofed_input = input
            spoofed_output = output
            for orig, subst in input_subst:
                chrs = []
                for ch in subst:
                    if ch.isupper():
                        chrs.append(random.sample(string.ascii_uppercase, 1)[0])
                    elif ch.islower():
                        chrs.append(random.sample(string.ascii_lowercase, 1)[0])
                    else:
                        chrs.append(ch)
                spoofed_subst = ''.join(chrs)

                try:
                    match = re.search(r"(%s)"%subst, spoofed_output)
                    prev = spoofed_output[:match.span()[0]].split()[-1]
                    if prev in firstnames:
                        spoofed_output = spoofed_output.replace(prev+' ', '')
                except:
                    pass
                spoofed_output = re.sub(subst, spoofed_subst, spoofed_output)
                spoofed_input = re.sub(subst, spoofed_subst, spoofed_input)

            print(spoofed_input.strip(), file=aug_input)
            print(spoofed_output.strip(), file=aug_output)

    #print(prevs)
