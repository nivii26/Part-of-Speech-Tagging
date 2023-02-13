# Part-of-Speech-Tagging-
POS bigram tagger based on the hidden Markov model, using Viterbi Algorithm
The command for training the POS tagger is:
```
    python3.8 buildtagger.py sents.train model-file
```

The command to test on this test file and generate an output file sents.out is:
```
    python3.8 runtagger.py sents.test model-file sents.out
```
