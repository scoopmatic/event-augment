import re
import random
import string

ORIGINAL_REPEAT = 4
EXPANSION_RATE = 40

firstnames = {'Aatu', 'Annukka', 'Balazs', 'Eero', 'Hannu', 'Ilari', 'Jani', 'Janne', 'Jarkko', 'Jason', 'Joonas', 'Juha', 'Jukka', 'Jussi', 'Kai', 'Lennart', 'Maija', 'Matt', 'Miikka', 'Mikko', 'Niclas', 'Niko', 'Patrick', 'Philip', 'Rico', 'Saku', 'Sami', 'Samuli', 'Semir', 'Stefan', 'Steve', 'Thomas', 'Tony', 'Tuulia', 'Ville'}
cities = ['edmonton', 'espoon', 'helsingin', 'helsinki', 'hämeenlinna', 'joensuu', 'jyväskylä', 'kajaani', 'kirkkonumm', 'kuopio', 'kuopion', 'lahden', 'lahti', 'lappeenran', 'malmö', 'mikkeli', 'oulu', 'pori', 'rauma', 'tampere', 'tikkurila', 'vaasa']

for dataset in ['train','devel','test']:
    print("Preparing %s set..." % dataset)
    aug_input = open("data/%s.input.aug" % dataset,'w')
    aug_output = open("data/%s.output.aug" % dataset,'w')

    prevs = set()
    for input, output in zip(open("data/%s.input" % dataset), open("data/%s.output" % dataset)):
        names = []

        if '<type>result' in input:
            home = re.findall("<home> ([\w \-]+) </home>", input)[0]
            guest = re.findall("<guest> ([\w \-]+) </guest>", input)[0]
        elif '<type>goal' in input:
            opponent = [home]
            if guest:
                opponent.append(guest)
            try:
                opponent.remove(re.findall("<team> ([\w \-]+) \*\*", input)[0])
            except ValueError:
                #print(opponent, input)
                home = re.findall("<team> ([\w \-]+) \*\*", input)[0]
                guest = None
                opponent = []
            if not opponent:
                opponent = ["Unknown"]
            input = input.strip() + " <opponent> %s </opponent>\n" % opponent[0]
            names.append(opponent[0])

        # Teams
        names += re.findall("<team> ([\w \-]+) \*\*", input)
        names += re.findall("<home> ([\w \-]+) </home>", input)
        names += re.findall("<guest> ([\w \-]+) </guest>", input)
        # Players
        names += re.findall("<player> ([\w \-]+) </player>", input)
        names += re.findall("<assist> ([\w \-]+) </assist>", input)
        names += [x for xx in re.findall("<assist> ([\w \-]+) , ([\w \-]+) </assist>", input) for x in xx] # flatten list of tuples

        #print()
        # Add last names only
        names += [n.split()[-1] for n in names if ' ' in n]
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
        # Add original data
        for o in range(ORIGINAL_REPEAT):
            print(input.strip(), file=aug_input)
            print(output.strip(), file=aug_output)

        # Check city references in output
        refs = [word for word in output.split() if re.search(r"\w+(ais(joukkue|ryhmä|et|ten))|(seura)\w*", word)]
        if refs:
            """for e in range(EXPANSION_RATE//4):
                print(input.strip(), file=aug_input)
                print(output.strip(), file=aug_output)"""
            continue
        refs = [word for word in output.split() if any([word.lower().startswith(city) for city in cities])]
        all_handled = True
        for ref in refs:
            handled = False
            for name in names:
                if name[:3] == output[output.index(ref):].split(' ')[1][:3] and len(name) > 2:
                    output = output.replace(ref+' ','')
                    handled = True
                    break
            if not handled:
                all_handled = False

        if not all_handled:
            for e in range(EXPANSION_RATE//4):
                print(input.strip(), file=aug_input)
                print(output.strip(), file=aug_output)
            continue

        if 'Kärpät' in output and 'Kärpät' not in names:
            print("ODD:", output, input)


        # Add augmented data
        SUBST_RATES = [0.4, 0.2, 0.2]
        for e in range(EXPANSION_RATE):
            spoofed_input = input
            spoofed_output = output
            for orig, subst in input_subst:
                chrs = []
                for i, ch in enumerate(subst):
                    if random.random() < SUBST_RATES[max(len(SUBST_RATES)*-1,i-len(subst))]:
                        if ch.isupper():
                            chrs.append(random.sample(string.ascii_uppercase, 1)[0])
                        elif ch.islower():
                            chrs.append(random.sample(string.ascii_lowercase, 1)[0])
                        else:
                            chrs.append(ch)
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
