# python3.8 buildtagger.py <train_file_absolute_path> <model_file_absolute_path>

import os
import math
import sys
import datetime

# Function that takes a sentence as input and adds start <s> and end <end> tags
def sentence_start_end_tokenizer(sentence):
    sentence_tokened = sentence.split()
    sentence_tokened.insert(0, '<s>/<s>')
    sentence_tokened.append('<end>/<end>')

    return sentence_tokened

# Function that updates a dictionary of counts each item
# item could be a 'word' or a 'tag'
def update_count_dict(item, item_dict):
    if item in item_dict.keys():
        item_dict[item] = item_dict[item] + 1
    else:
        item_dict[item] = 1
        
#Function that updates nested dictionary of form word:tag/ tag:tag
def updated_nested_dict(item1, item2, item_dict):
    if item1 in item_dict.keys():
        if item2 in item_dict[item1].keys():
            item_dict[item1][item2] = item_dict[item1][item2] + 1
        else:
            item_dict[item1][item2] = 1
    else:
        item_dict[item1] = {}
        item_dict[item1][item2] = 1
    
def train_model(train_file, model_file):
    # write your code here. You can add functions as well.

    # Reading tagged text from the train file
    train_file_open = open(train_file, 'r')
    sentences = train_file_open.readlines()

    # Stores a list of lists of sentences with <s>, <end> tokens
    sentences_list = []
    
    # Add start of sentence <s>, and end of sentence <\s> tokens
    for sentence in sentences:
        curr_sentence_tokened = sentence_start_end_tokenizer(sentence)
        sentences_list.append(curr_sentence_tokened)
        
    word_count_dict = {} 
    tag_count_dict = {} 
    word_tag_dict = {}
    tag_tag_dict = {}
    
    for sentence in sentences_list:
        for i in range(0, len(sentence)-1): # -1 bcz otherwise tag2 will give key error
            word_tag_pair = sentence[i].split('/')
                                             
            word = '/'.join(word_tag_pair[:-1])
            tag = word_tag_pair[-1]

            # Store count of each word in dictionary of form {word:count}
            update_count_dict(word,word_count_dict)
            
            # Store count of each tag in dictionary of form {tag:count}
            update_count_dict(tag,tag_count_dict)
            
            # Store count of each <word,tag> occurences
            # nested dict of form {word1:{tag1:.., tag2:..}, word2:{tag1:.., tag2:..}}
            updated_nested_dict(word, tag, word_tag_dict)
            
            # Store count of each tag(i)|tag(i-1) occurences
            # Dictionary of form {tag: tag1}
            tag2 = sentence[i+1].split('/')[1]
            updated_nested_dict(tag, tag2, tag_tag_dict)
            

    # for end of sentence <end> tag
    # As the number of end tags = start tags
    number_sentences = tag_count_dict['<s>']
    tag_count_dict['<end>'] = number_sentences
    word_count_dict['<end>'] = number_sentences
    word_tag_dict['<end>'] = {}
    word_tag_dict['<end>']['<end>'] = number_sentences
    
    # Computing the transition and emission probabilities
    
    # Transistion probability dictionary with values log(P(tag(i)|tag(i-1))
    transition_prob = {}

    # Emission probability dictionary with values log(P(word|tag)
    emission_prob = {} 
    
    total_words = len(word_count_dict.keys()) 
    total_tags = len(tag_count_dict.keys()) 

    # WITH 'K-ADD SMOOTHING' - as test data might have many new unknown words
    # We take log probabilities to avoid numerical underflow
    
    # Calculate Emission probabilities P(word|tag) 
    for word in word_tag_dict.keys():
        emission_prob[word] = {}
        for tag in tag_count_dict.keys():
            if tag in word_tag_dict[word]:
                emission_prob[word][tag] =  math.log10((word_tag_dict[word][tag] + 1*0.15)/ (tag_count_dict[tag] + total_words*0.15))
            else:
                emission_prob[word][tag] = -999999999
                
    # Calculate Transition probabilities P(tag(i)|tag(i-1))/ P(curr_tag|prev_tag)
    for prev_tag in tag_tag_dict.keys():
        transition_prob[prev_tag] = {}
        for curr_tag in tag_tag_dict[prev_tag]:
            transition_prob[prev_tag][curr_tag] = math.log10((tag_tag_dict[prev_tag][curr_tag] + 1*0.15) / (tag_count_dict[prev_tag] + total_tags*0.15))

    # DEALING WITH UNKNOWN WORDS AND NEW TAG SEQUENCES
    
    # for a new unknown word that may appear in the test dataset
    emission_prob['unknown'] = {}
    for tag in tag_count_dict.keys():
        emission_prob['unknown'][tag] = math.log10(1*0.15 / (tag_count_dict[tag] + total_words*0.15))

    # for a new tag sequence that may appear in the test dataset
    for prev_tag in tag_count_dict.keys():
        if prev_tag not in transition_prob.keys():
            transition_prob[prev_tag] = {}
        for curr_tag in tag_count_dict.keys():
            if curr_tag not in transition_prob[prev_tag]:
                transition_prob[prev_tag][curr_tag] = math.log10(1*0.15 / (tag_count_dict[prev_tag] + total_tags*0.15))
    
    '''
    The file model-file is the output of the training process and contains
    the statistics gathered from training, which include the
    POS tag transition probabilities and the word emission probabilities - that we need for runtagger.py
    '''

    model_train_stats = {'tag_count_dict':tag_count_dict,'transition_prob': transition_prob, 'emission_prob': emission_prob}
    

    model_file = open(model_file, 'w') 
    model_file.write(str(model_train_stats))
    model_file.close()
    
    print('Finished...')


if __name__ == "__main__":
    # make no changes here
    train_file = sys.argv[1]
    model_file = sys.argv[2]
    start_time = datetime.datetime.now()
    train_model(train_file, model_file)
    end_time = datetime.datetime.now()
    print('Time:', end_time - start_time)
