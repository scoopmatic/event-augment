#!/bin/bash

## Train with data augmentation and sentence pieces

data="data"
model="model"
inmax=80
outmax=100
BS=128

mkdir $model

mkdir $data
#rm $data/prep*

#cat $data/train.all | cut -f 1 > $data/train.input
#cat $data/train.all | cut -f 2 > $data/train.output

#cat $data/devel.all | cut -f 1 > $data/devel.input
#cat $data/devel.all | cut -f 2 > $data/devel.output

#cat $data/test.all | cut -f 1 > $data/test.input
#cat $data/test.all | cut -f 2 > $data/test.output

#python name_expansion.py
#cp -v event-augment/data/*aug $data/

#for v in {100..5000..500} ; do
v=2500 # Vocab size
cd sentpiece
##python train.py ../sentpiece_corpus.txt $v
cd ..
#python data2pieces.py ../game-report-generator/event2text/data/ ""
##python data2pieces.py data/ ""
##python data2pieces.py data/ .aug
#cp -v event-augment/data/*pcs $data/

##rm $data/prep_fwd*
#python OpenNMT-py/preprocess.py -train_src $data/train.input.pcs -train_tgt $data/train.output.pcs -valid_src $data/devel.input.pcs -valid_tgt $data/devel.output.pcs -save_data $data/prep -src_words_min_frequency 1 -tgt_words_min_frequency 1 -dynamic_dict --src_seq_length $inmax --tgt_seq_length $outmax
##python OpenNMT-py/preprocess.py -train_src $data/train.input.aug.pcs -train_tgt $data/train.output.aug.pcs -valid_src $data/devel.input.aug.pcs -valid_tgt $data/devel.output.aug.pcs -save_data $data/prep_fwd -src_words_min_frequency 1 -tgt_words_min_frequency 1 -dynamic_dict --src_seq_length $inmax --tgt_seq_length $outmax

##rm $model/*
##python OpenNMT-py/train.py -seed 9001 -data $data/prep_fwd -save_model $model/model -encoder_type brnn -train_steps 12000 -valid_steps 500 -save_checkpoint_steps 500 -log_file training.log -early_stopping 3 -gpu_ranks 0 -optim adam -learning_rate 0.000125 -layers 2 -batch_size $BS -copy_attn -reuse_copy_attn -coverage_attn -copy_loss_by_seqlength

# Evaluate
rm tmp/eval.txt
# Simple detokenization of game scores to deflate BLEU scores

cat $data/devel.output | sed "s/ – /–/g" |sed "s/ - /-/g" | sed "s/ — /—/g" | sed "s/( /(/g" | sed "s/ )/)/g" > $data/devel.output.detok
for i in {1000..12000..500} ;
do
echo "Evaluating step $i"
python OpenNMT-py/translate.py -seed 10101 -gpu 0 -model $model/model_step_$i.pt -src $data/devel.input.pcs -output tmp/pred.txt.pcs -replace_unk -max_length 50 -batch_size $BS
python sentpiece/p2s.py tmp/pred.txt.pcs sentpiece/m.model > tmp/pred.txt
cat tmp/pred.txt | sed "s/ – /–/g" |sed "s/ - /-/g" | sed "s/ — /—/g" | sed "s/( /(/g" | sed "s/ )/)/g" > tmp/pred.txt.detok
BLEU=$(perl OpenNMT-py/tools/multi-bleu.perl $data/devel.output.detok < tmp/pred.txt.detok)
echo $BLEU $i >> tmp/eval.txt
echo $BLEU
done

BEST="$model/model_step_$(cat tmp/eval.txt | cut -d" " -f3,9|sort -n|tail -1|cut -d" " -f2).pt"
echo "Best model: $BEST"
cp -v $BEST trained_model.pt

echo "Vocab size: $v"
### Test
## Without data augmentation
cat $data/test.output | sed "s/ – /–/g" |sed "s/ - /-/g" | sed "s/ — /—/g" | sed "s/( /(/g" | sed "s/ )/)/g" > $data/test.output.detok
python OpenNMT-py/translate.py -seed 10101 -gpu 0 -model $BEST -src $data/test.input.pcs -output tmp/test_pred.txt.pcs -replace_unk -max_length 80 -batch_size $BS
python sentpiece/p2s.py tmp/test_pred.txt.pcs sentpiece/m.model > tmp/test_pred.txt
cat tmp/test_pred.txt | sed "s/ – /–/g" |sed "s/ - /-/g" | sed "s/ — /—/g" | sed "s/( /(/g" | sed "s/ )/)/g" > tmp/test_pred.txt.detok
BLEU_PCS=$(perl OpenNMT-py/tools/multi-bleu.perl $data/test.output.pcs < tmp/test_pred.txt.pcs)
echo "Performance on test set, sentence pieces: $BLEU_PCS"
BLEU_WORD=$(perl OpenNMT-py/tools/multi-bleu.perl $data/test.output < tmp/test_pred.txt)
echo "Performance on test set, words: $BLEU_WORD"
BLEU_DETOK=$(perl OpenNMT-py/tools/multi-bleu.perl $data/test.output.detok < tmp/test_pred.txt.detok)
echo "Performance on test set, detokenized: $BLEU_DETOK"

echo -e "orig\t$v\t$BLEU_DETOK\t$BLEU_WORD\t$BLEU_PCS\t$BEST" >> opt.log
#cp test_pred.txt.detok $data/test_pred.txt.detok__sp$v

## With data augmentation
cat $data/test.output.aug | sed "s/ – /–/g" |sed "s/ - /-/g" | sed "s/ — /—/g" | sed "s/( /(/g" | sed "s/ )/)/g" > $data/test.output.aug.detok
python OpenNMT-py/translate.py -seed 10101 -gpu 0 -model $BEST -src $data/test.input.aug.pcs -output tmp/test_pred_aug.txt.pcs -replace_unk -max_length 80 -batch_size $BS
python sentpiece/p2s.py tmp/test_pred_aug.txt.pcs sentpiece/m.model > tmp/test_pred_aug.txt
cat tmp/test_pred_aug.txt | sed "s/ – /–/g" |sed "s/ - /-/g" | sed "s/ — /—/g" | sed "s/( /(/g" | sed "s/ )/)/g" > tmp/test_pred_aug.txt.detok
BLEU_PCS=$(perl OpenNMT-py/tools/multi-bleu.perl $data/test.output.aug.pcs < tmp/test_pred_aug.txt.pcs)
echo "Performance on aug. test set, sentence pieces: $BLEU_PCS"
BLEU_WORD=$(perl OpenNMT-py/tools/multi-bleu.perl $data/test.output.aug < tmp/test_pred_aug.txt)
echo "Performance on aug. test set, words: $BLEU_WORD"
BLEU_DETOK=$(perl OpenNMT-py/tools/multi-bleu.perl $data/test.output.aug.detok < tmp/test_pred_aug.txt.detok)
echo "Performance on aug. test set, detokenized: $BLEU_DETOK"

echo -e "aug\t$v\t$BLEU_DETOK\t$BLEU_WORD\t$BLEU_PCS\t$BEST" >> opt.log
#cp test_pred_aug.txt.detok $data/test_pred_aug.txt.detok__sp$v
#done

ALPHA=1.8

### Evaluation on aligned test set
#cat test.input.pcs |sed "s/<length>short<\/length>/<length>long<\/length>/g"|sed "s/<length>medium<\/length>/<length>long<\/length>/g">test_long.input.pcs
#cat test.input.pcs |sed "s/<length>short<\/length>/<length>medium<\/length>/g"|sed "s/<length>long<\/length>/<length>medium<\/length>/g">test_medium.input.pcs
#cat test.input.pcs |sed "s/<length>long<\/length>/<length>short<\/length>/g"|sed "s/<length>medium<\/length>/<length>short<\/length>/g">test_short.input.pcs

#CUDA_VISIBLE_DEVICES=2 python OpenNMT-py/translate.py -seed 10101 -gpu 0 -model $BEST -src $data/test_long.input.pcs -output test_pred_long.txt.pcs -replace_unk -max_length 100 -batch_size $BS -min_length 25 -length_penalty wu -alpha $ALPHA -verbose |grep "PRED SCORE"|cut -d":" -f2 > test_scores_long.txt
#python event-augment/sentpiece/p2s.py test_pred_long.txt.pcs event-augment/sentpiece/m.model > test_pred_long.txt
#cat test_pred_long.txt | sed "s/ – /–/g" |sed "s/ - /-/g" | sed "s/ — /—/g" | sed "s/( /(/g" | sed "s/ )/)/g" > test_pred_long.txt.detok

#CUDA_VISIBLE_DEVICES=2 python OpenNMT-py/translate.py -seed 10101 -gpu 0 -model $BEST -src $data/test_medium.input.pcs -output test_pred_medium.txt.pcs -replace_unk -max_length 100 -batch_size $BS -min_length 15 -length_penalty wu -alpha $ALPHA -verbose |grep "PRED SCORE"|cut -d":" -f2 > test_scores_medium.txt
#python event-augment/sentpiece/p2s.py test_pred_medium.txt.pcs event-augment/sentpiece/m.model > test_pred_medium.txt
#cat test_pred_medium.txt | sed "s/ – /–/g" |sed "s/ - /-/g" | sed "s/ — /—/g" | sed "s/( /(/g" | sed "s/ )/)/g" > test_pred_medium.txt.detok

#CUDA_VISIBLE_DEVICES=2 python OpenNMT-py/translate.py -seed 10101 -gpu 0 -model $BEST -src $data/test_short.input.pcs -output test_pred_short.txt.pcs -replace_unk -max_length 100 -batch_size $BS -length_penalty wu -alpha $ALPHA -verbose |grep "PRED SCORE"|cut -d":" -f2 > test_scores_short.txt
#python event-augment/sentpiece/p2s.py test_pred_short.txt.pcs event-augment/sentpiece/m.model > test_pred_short.txt
#cat test_pred_short.txt | sed "s/ – /–/g" |sed "s/ - /-/g" | sed "s/ — /—/g" | sed "s/( /(/g" | sed "s/ )/)/g" > test_pred_short.txt.detok

#paste test_scores_long.txt test_pred_long.txt.detok > test_scored_pred_long.txt.detok
#paste test_scores_medium.txt test_pred_medium.txt.detok > test_scored_pred_medium.txt.detok
#paste test_scores_short.txt test_pred_short.txt.detok > test_scored_pred_short.txt.detok
#paste -d "\n" data/test.input test_scored_pred_short.txt.detok test_scored_pred_medium.txt.detok test_scored_pred_long.txt.detok /dev/null

#### Prepare manual evaluation set on setion of unaligned test set
python filter_test_games.py
python data2pieces_single.py data/test_manual_long.input # --> *.pcs
python data2pieces_single.py data/test_manual_medium.input
python data2pieces_single.py data/test_manual_short.input
python data2pieces_single.py data/test_manual_long_oov.input
python data2pieces_single.py data/test_manual_medium_oov.input
python data2pieces_single.py data/test_manual_short_oov.input


# Manual test original entities
for i in 1 2 3; do
  length=$(echo "long medium short"|cut -d" " -f$i)
  min_length=$(echo "25 15 0"|cut -d" " -f$i)
  python OpenNMT-py/translate.py -seed 10101 -gpu 0 -model $BEST -src data/test_manual_$length.input.pcs -output tmp/test_pred_$length.txt.pcs -replace_unk -max_length 100 -batch_size $BS -min_length $min_length -length_penalty wu -alpha $ALPHA -verbose |grep "PRED SCORE"|cut -d":" -f2 > tmp/test_scores_$length.txt
  python sentpiece/p2s.py tmp/test_pred_$length.txt.pcs sentpiece/m.model > tmp/test_pred_$length.txt
  cat tmp/test_pred_$length.txt | sed "s/ – /–/g" |sed "s/ - /-/g" | sed "s/ — /—/g" | sed "s/( /(/g" | sed "s/ )/)/g" > tmp/test_pred_$length.txt.detok
  paste test_scores_$length.txt test_pred_$length.txt.detok > tmp/test_scored_pred_$length.txt.detok
done
paste -d "\n" data/test_manual_long.input tmp/test_scored_pred_short.txt.detok tmp/test_scored_pred_medium.txt.detok tmp/test_scored_pred_long.txt.detok /dev/null |python postprocessing.py > output/manual_eval.txt

# Manual test original entities with varying seed
#for i in 1 2 3; do
#  length=$(echo "long medium short"|cut -d" " -f$i)
#  min_length=$(echo "25 15 0"|cut -d" " -f$i)
#  for s in 1 2 3 4 5; do
#    seed=$(echo "10101 20202 30303 939 123091"|cut -d" " -f$s)
#    python OpenNMT-py/translate.py -seed $seed -gpu 0 -model $BEST -src data/test_manual_$length.input.pcs -output tmp/test_pred_$length.$s.txt.pcs -replace_unk -max_length 100 -batch_size $BS -min_length $min_length -length_penalty wu -alpha $ALPHA -verbose |grep "PRED SCORE"|cut -d":" -f2 > tmp/test_scores_$length.$s.txt
#    python sentpiece/p2s.py tmp/test_pred_$length.$s.txt.pcs sentpiece/m.model > tmp/test_pred_$length.$s.txt
#  done
#  paste -d "\n" tmp/test_pred_$length.?.txt | sed "s/ – /–/g" |sed "s/ - /-/g" | sed "s/ — /—/g" | sed "s/( /(/g" | sed "s/ )/)/g" > tmp/test_pred_$length.txt.detok
#  paste -d "\n" tmp/test_scores_$length.?.txt > test_scores_$length.txt
#  paste test_scores_$length.txt test_pred_$length.txt.detok > tmp/test_scored_pred_$length.txt.detok
#done

# Manual test OOV entities
for i in 1 2 3; do
  length=$(echo "long medium short"|cut -d" " -f$i)
  min_length=$(echo "25 15 0"|cut -d" " -f$i)
  python OpenNMT-py/translate.py -seed 10101 -gpu 0 -model $BEST -src data/test_manual_$length.oov.input.pcs -output tmp/test_pred_$length.oov.txt.pcs -replace_unk -max_length 100 -batch_size $BS -min_length $min_length -length_penalty wu -alpha $ALPHA -verbose |grep "PRED SCORE"|cut -d":" -f2 > tmp/test_scores_$length.txt
  python sentpiece/p2s.py tmp/test_pred_$length.oov.txt.pcs sentpiece/m.model > tmp/test_pred_$length.oov.txt
  cat tmp/test_pred_$length.oov.txt | sed "s/ – /–/g" |sed "s/ - /-/g" | sed "s/ — /—/g" | sed "s/( /(/g" | sed "s/ )/)/g" > tmp/test_pred_$length.oov.txt.detok
  paste test_scores_$length.oov.txt test_pred_$length.oov.txt.detok > tmp/test_scored_pred_$length.oov.txt.detok
done
paste -d "\n" data/test_manual_long.oov.input tmp/test_scored_pred_short.oov.txt.detok tmp/test_scored_pred_medium.oov.txt.detok tmp/test_scored_pred_long.oov.txt.detok /dev/null |python postprocessing.py > output/manual_eval_oov.txt
