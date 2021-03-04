This program is an implementation of Viterbi HMM Algorithm, with OOV handling, collaborated by Xinyu Xie and Jessica Liu. 

====================================================================================
How to run this system

To run this program on self-selected files, execute 
`python3 xx708_HW3.py training_file testing_file output_file` in terminal

To run this program on DEFAULT files, execute `python3 xx708_HW3.py` in terminal: 
training_corpus.pos is the training set, WSJ_23.words is the testing file, 
and result is to be written to submission.pos file. 

====================================================================================
Work distribution: 

Jessica: created tables of likelihood and transition. 
Xinyu Xie: implemented a transducer dict to get best pos of words. 
Jessica: did an error analysis based on OOV words, and decided what to fix in the next step. 
Xinyu Xie: wrote a manual rule based system, dealing with the OOVs. 


====================================================================================
What we did to handle OOV items

OOV (Out-of-Vocabulary) tokens are handled by the following steps:
1. For each token in the training corpus that only occurs once, 
   We created a dictionary to store them. 

2. Assume this unique tokens' tags follow a normal distribution, 
   We will use it to estimate the probability of any new incoming OOV token 
   from testing corpus being classified to a certain tag. 

For example: 
    Suppose, in training corpus, we have nouns of "cat" occurring 30 times, 
    "fish" occurring 50 times, and "dog" occurring 18 times. 
    Additionally, we have some unique noun tokens: "unicorn" and "dragon". 

    Collectively, there are 100 nouns, and the unique words are 2 out of 100. 
    So, we consider any new incoming OOV token has 2% probability to be a noun. 

====================================================================================