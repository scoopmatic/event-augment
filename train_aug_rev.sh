#!/bin/bash

## Train with data augmentation and sentence pieces

data="data"
model="model"
inmax=100
outmax=80
BS=128

mkdir $model

mkdir $data
rm $data/prep_rev*

#cat $data/train.all | cut -f 1 > $data/train.input
#cat $data/train.all | cut -f 2 > $data/train.output

#cat $data/devel.all | cut -f 1 > $data/devel.input
#cat $data/devel.all | cut -f 2 > $data/devel.output

#cat $data/test.all | cut -f 1 > $data/test.input
#cat $data/test.all | cut -f 2 > $data/test.output

#for v in {100..5000..500} ; do
v=2500 # Vocab size
cd sentpiece
##python train.py ../sentpiece_corpus.txt $v
cd ..
#python data2pieces.py ../game-report-generator/event2text/data/ ""
python data2pieces.py data/ ""
python data2pieces.py data/ .aug

rm $data/prep_rev*
#python OpenNMT-py/preprocess.py -train_src $data/train.input.pcs -train_tgt $data/train.output.pcs -valid_src $data/devel.input.pcs -valid_tgt $data/devel.output.pcs -save_data $data/prep -src_words_min_frequency 1 -tgt_words_min_frequency 1 -dynamic_dict --src_seq_length $inmax --tgt_seq_length $outmax
#python OpenNMT-py/preprocess.py -train_src $data/train.input.aug.pcs -train_tgt $data/train.output.aug.pcs -valid_src $data/devel.input.aug.pcs -valid_tgt $data/devel.output.aug.pcs -save_data $data/prep -src_words_min_frequency 1 -tgt_words_min_frequency 1 -dynamic_dict --src_seq_length $inmax --tgt_seq_length $outmax
python OpenNMT-py/preprocess.py -train_tgt $data/train.input.aug.pcs -train_src $data/train.output.aug.pcs -valid_tgt $data/devel.input.aug.pcs -valid_src $data/devel.output.aug.pcs -save_data $data/prep_rev -src_words_min_frequency 1 -tgt_words_min_frequency 1 -dynamic_dict --src_seq_length $outmax --tgt_seq_length $inmax

rm $model/rev_*
python OpenNMT-py/train.py -seed 9001 -data $data/prep_rev -save_model $model/rev_model -encoder_type brnn -train_steps 12000 -valid_steps 500 -save_checkpoint_steps 500 -log_file training.log -early_stopping 3 -gpu_ranks 0 -optim adam -learning_rate 0.000125 -layers 2 -batch_size $BS -copy_attn -reuse_copy_attn -coverage_attn -copy_loss_by_seqlength

# Evaluate
rm tmp/rev_eval.txt
# Simple detokenization of game scores to deflate BLEU scores

#cat $data/devel.output | sed "s/ – /–/g" |sed "s/ - /-/g" | sed "s/ — /—/g" | sed "s/( /(/g" | sed "s/ )/)/g" > $data/devel.output.detok
for i in {1000..12000..500} ;
do
echo "Evaluating step $i"
python OpenNMT-py/translate.py -seed 10101 -gpu 0 -model $model/rev_model_step_$i.pt -src $data/devel.output.pcs -output tmp/rev_test_pred.txt.pcs -replace_unk -max_length 80 -batch_size $BS
#python event-augment/sentpiece/p2s.py pred.txt.pcs event-augment/sentpiece/m.model > pred.txt
cat tmp/rev_test_pred.txt.pcs | python piecemix2text.py > tmp/rev_test_pred.txt
#cat pred.txt | sed "s/ – /–/g" |sed "s/ - /-/g" | sed "s/ — /—/g" | sed "s/( /(/g" | sed "s/ )/)/g" > pred.txt.detok
BLEU=$(perl OpenNMT-py/tools/multi-bleu.perl $data/devel.input.aug < tmp/rev_test_pred.txt)
echo $BLEU $i >> rev_eval.txt
echo $BLEU
done

BEST="$model/rev_model_step_$(cat rev_eval.txt | cut -d" " -f3,9|sort -n|tail -1|cut -d" " -f2).pt"
echo "Best model: $BEST"
cp -v $BEST trained_rev_model.pt

echo "Vocab size: $v"

### Test on unaugmented test data
#cat $data/test.output | sed "s/ – /–/g" |sed "s/ - /-/g" | sed "s/ — /—/g" | sed "s/( /(/g" | sed "s/ )/)/g" > $data/test.output.detok
python OpenNMT-py/translate.py -seed 10101 -gpu 0 -model $BEST -src $data/test.output.pcs -output tmp/rev_test_pred.txt.pcs -replace_unk -max_length 80 -batch_size $BS
#python event-augment/sentpiece/p2s.py test_pred.txt.pcs event-augment/sentpiece/m.model > test_pred.txt
cat tmp/rev_test_pred.txt.pcs | python piecemix2text.py > tmp/rev_test_pred.txt
#cat test_pred.txt | sed "s/ – /–/g" |sed "s/ - /-/g" | sed "s/ — /—/g" | sed "s/( /(/g" | sed "s/ )/)/g" > test_pred.txt.detok
BLEU_PCS=$(perl OpenNMT-py/tools/multi-bleu.perl $data/test.input.pcs < tmp/rev_test_pred.txt.pcs)
echo "Performance on test set, sentence pieces: $BLEU_PCS"
BLEU_WORD=$(perl OpenNMT-py/tools/multi-bleu.perl $data/test.input < tmp/rev_test_pred.txt)
echo "Performance on test set, words: $BLEU_WORD"
#BLEU_DETOK=$(perl OpenNMT-py/tools/multi-bleu.perl $data/test.output.detok < test_pred.txt.detok)
#echo "Performance on test set, detokenized: $BLEU_DETOK"

#echo -e "orig\t$v\t$BLEU_DETOK\t$BLEU_WORD\t$BLEU_PCS\t$BEST" >> rev_opt.log
#cp test_pred.txt.detok $data/test_pred.txt.detok__sp$v

#done
