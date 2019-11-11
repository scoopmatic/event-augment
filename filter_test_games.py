import re

games_in_eval = []
events_in_eval = []
# Manual eval game IDs
for line in open("../game-report-generator/event2text/data/manual_eval.txt"):
    if 'Lopputulos' in line:
        teams, score = re.findall("Lopputulos (.+–.+) \d+–\d+.+\((.+)\)", line)[0]
        teams = tuple(teams.split('–'))
        #score = tuple(score.split('–'))
        games_in_eval.append((teams, score))
        events_in_eval.append([])
        event_id = 0
        events_in_eval[-1].append(event_id)
    elif re.search("^\*?E\d", line):
        event_id += 1
        if line[0] == '*':
            events_in_eval[-1].append(event_id)

OOV_teams = "TuusKi,EJK,HCK Salamat,Kiekko-Oulu,Haukat,KoMu,Laser,Cowboys,Pyry,Tarmo,TuWe,VaKi,Viikingit,SuPS,KJT".split(',')

testset_games = []
game = []
teams, score = None, None
for line in open("../game-report-generator/event2text/data/test_with_null.all"):
    if "<type>result" in line:
        if game:
            if (teams, score) in games_in_eval:
                testset_games.append((games_in_eval.index((teams, score)), game))
            game = []

        teams = re.findall("<home> (.+) </home> <guest> (.+) </guest>", line)[0]
        score = re.findall("<periods> \((.+)\) </periods>", line)[0].strip().replace(' – ','–').replace(' ,',',')
        game.append(line)
    elif game:
        game.append(line)

if (teams, score) in games_in_eval:
    testset_games.append((games_in_eval.index((teams, score)), game))

print(len(testset_games))

for length in ['short','medium','long']:
    print("Preparing dataset", length)
    with open("data/test_manual_%s.input" % length,'w') as test_file:
        with open("data/test_manual_%s.oov.input" % length,'w') as oov_test_file:
            for i, game in sorted(testset_games):
                teams = re.findall("<home> (.+) </home> <guest> (.+) </guest>", game[0])[0]
                for j, row in enumerate(game):
                    if j in events_in_eval[i]:
                        print(re.sub("<length>(\w+)", "<length>%s" % length, row.split('\t')[0]), file=test_file)
                # Add events with OOV teams
                for j, row in enumerate(game):
                    if j in events_in_eval[i]:
                        str = re.sub("<length>(\w+)", "<length>%s" % length, row.split('\t')[0])
                        str = str.replace(teams[0], OOV_teams[i%len(OOV_teams)])
                        str = str.replace(teams[1], OOV_teams[(i+i//len(OOV_teams)+1)%len(OOV_teams)])
                        print(str, file=oov_test_file)
