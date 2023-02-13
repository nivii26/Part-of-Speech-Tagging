# Part-of-Speech-Tagging-
POS bigram tagger based on the hidden Markov model, using Viterbi Algorithm

The command for training the POS tagger on a train file is:
```
    python3.8 buildtagger.py sents.train model-file
```

The file model-file is the output of the training process and contains the statistics gathered from training, which include the POS tag transition probabilities and the word emission probabilities.

The command to test on a test file and generate an output file sents.out is:
```
    python3.8 runtagger.py sents.test model-file sents.out
```
