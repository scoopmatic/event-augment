BS=128
ALPHA=1.8

# Manual test original entities
for i in 1 2 3; do
  length=$(echo "long medium short"|cut -d" " -f$i)
  min_length=$(echo "25 15 0"|cut -d" " -f$i)
  python OpenNMT-py/translate.py -seed 10101 -gpu 0 -model trained_model.pt -src data/test_manual_$length.input.pcs -output tmp/test_pred_$length.txt.pcs -replace_unk -max_length 100 -batch_size $BS -min_length $min_length -length_penalty wu -alpha $ALPHA -verbose |grep "PRED SCORE"|cut -d":" -f2 > tmp/test_scores_$length.txt
  python sentpiece/p2s.py tmp/test_pred_$length.txt.pcs sentpiece/m.model > tmp/test_pred_$length.txt
  #cat tmp/test_pred_$length.txt | sed "s/ – /–/g" |sed "s/ - /-/g" | sed "s/ — /—/g" | sed "s/( /(/g" | sed "s/ )/)/g" > tmp/test_pred_$length.txt.detok
  #paste test_scores_$length.txt test_pred_$length.txt > tmp/test_scored_pred_$length.txt
done
#paste -d "\n" data/test_manual_long.input tmp/test_scored_pred_short.txt.detok tmp/test_scored_pred_medium.txt.detok tmp/test_scored_pred_long.txt.detok /dev/null |python postprocessing.py > output/manual_eval.txt

## Prepare input for back-translation
paste -d "\n" tmp/test_pred_short.txt tmp/test_pred_medium.txt tmp/test_pred_long.txt > tmp/manual_eval_fc-in.txt
## Prepare gold output for back-translation
paste -d "\n" data/test_manual_short.input data/test_manual_medium.input data/test_manual_long.input > tmp/manual_eval_fc-out.txt

#python OpenNMT-py/translate.py -seed 10101 -gpu 0 -model trained_model.pt -src data/test_manual_$length.input.pcs -output tmp/test_pred_$length.txt.pcs -replace_unk -max_length 100 -batch_size $BS -min_length 25 -length_penalty wu -alpha $ALPHA -verbose |grep "PRED SCORE"|cut -d":" -f2 > tmp/test_scores_$length.txt
python OpenNMT-py/translate.py -seed 10101 -gpu 0 -model trained_rev_model.pt -src tmp/manual_eval_fc-in.txt -tgt tmp/manual_eval_fc-out.txt -output tmp/manual_eval_fc.pred -replace_unk -max_length 80 -batch_size 128 -verbose > tmp/manual_eval_fc.log

# Fwd pred scores
paste -d "\n" tmp/test_scores_short.txt  tmp/test_scores_medium.txt  tmp/test_scores_long.txt > tmp/manual_eval_fc_fwd.scores


grep "GOLD SCORE" tmp/manual_eval_fc.log | cut -d" " -f3 > tmp/manual_eval_fc_gold.scores
grep "PRED SCORE" tmp/manual_eval_fc.log | cut -d" " -f3 > tmp/manual_eval_fc_pred.scores
paste tmp/manual_eval_fc_fwd.scores tmp/manual_eval_fc_gold.scores tmp/manual_eval_fc_pred.scores tmp/manual_eval_fc-in.txt tmp/manual_eval_fc-out.txt

# Fwd pred scores
#paste -d "\n" tmp/test_scores_short.txt  tmp/test_scores_medium.txt  tmp/test_scores_long.txt
