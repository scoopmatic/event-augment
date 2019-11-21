# Usage: python ./OpenNMT-py/translate.py -model model.pt -src devel.input -output pred.txt -replace_unk -verbose --max_length 50 -attn_debug > debug.txt
#        python attention_visualization.py --input debug.txt

import sys
import argparse
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import re


def read_data(args):

    with open(args.input, "rt", encoding="utf-8") as f:

        preline = ""
        attn_block = False
        data = []

        for line in f:
            line = line.strip()
            if not line:
                preline = ""
                attn_block = False
                continue

            if line.startswith('SENT '):
                if len(data) > 0:
                    #data[-1][0] = source
                    for i in range(1, len(data[-1])):
                        try:
                            data[-1][i][0] = target[i-1]
                        except IndexError:
                            data[-1][i][0] = '</s>'

                    data[-1][0] = source
                data.append([])
                source = eval(line[line.index(':')+2:])
            if re.search("^PRED \d+", line):
                target = line[line.index(':')+2:].split()
            if preline.startswith("PRED SCORE:"):
                attn_block = True
            if line.startswith("PRED AVG SCORE:"):
                attn_block = False
            if attn_block:
                data[-1].append(line.split())
            preline = line

    return data

def process_data(data):

    processed_data = []

    for sentence in data:
        source, rest = sentence[0], sentence[1:]
        target = [ w[0] for w in rest ]
        weights = [ w[1:] for w in rest ]
        weights = [[float(j.replace("*", "")) for j in i] for i in weights]

        processed_data.append( (source, target, weights) )

    return processed_data



def longest_cont(array):

    longest = [[array[0]]]
    for val in array[1:]:
        if val == longest[-1][-1]+1:
            longest[-1].append(val)
        else:
            longest.append([val])

    return longest


def prune_empty_regions(source, target, weights):

    # dummy solution to remove zero value regions from the heatmap
    # should be rewritten with numpy magic

    weight_array = np.array(weights)

    empty_columns = [] # indices of colums where all rows are close to zero

    for i in range(len(source)): # i is a column index
        is_empty = True
        for j in range(len(target)): # j is a row index
            if weights[j][i] >= 0.05:
                is_empty = False
                break
        if is_empty:
            empty_columns.append(i)
    """for i,x in enumerate(weight_array):
        for j,_ in enumerate(x):
            if weight_array[i][j] < 0.5:
                weight_array[i][j] = 0"""

    cont_empty_subseq = longest_cont(empty_columns)

    keep_columns = [i for i in range(len(source)) if i not in empty_columns] # all non empty columns

    for subseq in cont_empty_subseq: # add small empty regions

        if False and len(subseq) > 10: # prune!!!
            for i in subseq[:3]+subseq[-3:]:
                keep_columns.append(i)
            source[subseq[2]] = source[subseq[2]]+"..."
            source[subseq[-3]] = "..."+source[subseq[-3]]
        else: # keep!!!
            for i in subseq:
                keep_columns.append(i)

    keep_columns.sort()


    a = weight_array[:, keep_columns]
    source_ = [word for i, word in enumerate(source) if i in keep_columns ]


    return source_, target, a


def plot(data, n=5):

    out=open("plot_copy.html",'w')
    #print("<table>",file=out)
    for i, (source, target, weights) in enumerate(data):

        print("source:", source)
        print("prediction:", target)

        source, target, weights = prune_empty_regions(source, target, weights)

        if i >= n:
            break

        ## Calculate error scores
        copy_error_scores = []
        repeat_error_scores = []
        for j in range(len(source)):
            copy_error_scores.append(0.0)
            repeat_error_scores.append(0.0)
            """if re.search("</\w+>$", source[j]):
                in_tag = False
                print(np.mean(copy_error_scores),j)
                continue
            elif re.search("^<\w+>", source[j]):
                in_tag = True
                copy_error_scores = []
                continue"""
            for i,w in enumerate(weights[:,j]):
                if weights[i,j] > 0.01 and (target[i] != source[j] or re.search("</?\w+>", target[i])):
                    copy_error_scores[-1] += weights[i,j]
                    print("copy", weights[i,j],source[j],target[i])
                if weights[i,j] > 0.01 and weights[i,j] < max(weights[:,j]):
                    if target[i] == source[j] and source[j] not in list("–▁ .,-"):
                        repeat_error_scores[-1] += weights[i,j]
                        print("repeat", weights[i,j], target[i])

            repeat_error_scores[-1] /= source.count(source[j])

        print("Copy error:", np.sum(copy_error_scores))#,copy_error_scores)
        print("Repeat error:", np.sum(repeat_error_scores))#,copy_error_scores)

        fig, ax = plt.subplots(figsize=(16, 5))
        #import pdb; pdb.set_trace()
        #sns.heatmap(weights, vmin=0.0, vmax=1.0, linewidth=0.01, linecolor="black", yticklabels=target, cmap="Reds", ax=ax)


        ## Plot attention matrix
        weights_ = np.array([[w if w > 0 else 0 for w in r] for r in weights])
        sns.heatmap(weights_, vmin=0.0, vmax=1.0, linewidth=0.01, linecolor="black", yticklabels=target, cmap="Reds", ax=ax)
        ax.set_xticks(np.arange(len(source))+0.5)
        ax.axes.set_xticklabels(source, fontsize="x-small", rotation=45, ha="center", va="center")
        plt.show()


        ## Highlight text by copy attention activation

        scores = [np.mean([w for w in r if w > 0.05]) for r in weights]
        scores = [0 if np.isnan(s) else s for s in scores]

        cmap = sns.diverging_palette(220, 20, n=9)

        ##scores = np.array(scores).reshape((1,weights.shape[0]))
        ##sns.heatmap(scores, vmin=-1.0, vmax=1.0, linewidth=0.01, linecolor="black", xticklabels=target, cmap=sns.diverging_palette(220, 20, n=7))
        ##plt.show()
        for i in range(weights.shape[1]):
            for j in range(weights.shape[0]):
                weights[j,i] = max(0,weights[j,i])
            if sum(weights[:,i]) > 0.05:
                weights[:,i] /= sum(weights[:,i])

        src_scores = [np.mean([w for w in r if w > 0.05]) for r in weights.transpose()]
        src_scores = [0 if np.isnan(s) else s for s in src_scores]

        print("<p><font style=\"font-size: 0.8em\">Event:",file=out)
        for w,s in zip(source,src_scores):
            i = 4-int(s*4.9999)
            color = ''.join([hex(int(cmap[i][j]*256))[2:] for j in range(3)])
            w = re.sub("(<length>\w+</length>|<type>\w+</type>)","",w)
            print("<span style=\"background-color:#%s\">%s</span>" % (color, w.replace('▁',' ').replace('<','&lt;').replace('>','&gt;')), file=out, end="")
        print("</font></p><p>Text:<b>",file=out)

        for w,s in zip(target,scores):
            try:
                i = int(s*4.9999)+4
            except TypeError:
                print(s)
                raise
            color = ''.join([hex(int(cmap[i][j]*256))[2:] for j in range(3)])
            print("<span style=\"background-color:#%s\">%s</span>" % (color, w.replace('▁',' ')), file=out, end="")
        print("</b></p><hr style=\"border-top: 1px solid #aaa; border-bottom: 0px\">",file=out)
        print(scores)

        src_scores = np.array(src_scores).reshape((1,weights.shape[1]))

        ##sns.heatmap(src_scores, vmin=-1.0, vmax=1.0, linewidth=0.01, linecolor="black", xticklabels=source, cmap=sns.diverging_palette(220, 20, n=7))
        #sns.heatmap(weights, vmin=-1.0, vmax=1.0, linewidth=0.01, linecolor="black", xticklabels=target, cmap=sns.diverging_palette(220, 20, n=7), ax=ax)
        #ax.set_xticks(np.arange(len(source))+0.5)
        #ax.axes.set_xticklabels(source, fontsize="x-small", rotation=45, ha="center", va="center")
        ##plt.show()

def main(args):

    data = read_data(args)

    data = process_data(data)

    plot(data, n=100)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', type=str, default='debug.txt', help="")

    args = parser.parse_args()


    main(args)
