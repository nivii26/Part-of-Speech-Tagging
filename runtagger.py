# python3.8 runtagger.py <test_file_absolute_path> <model_file_absolute_path> <output_file_absolute_path>

import os
import math
import sys
import datetime


# Function to initialise path probability matrix for backtracking in viterbi algorithm
# Matrix is of dimensions (no. of words in sentence, total tags) and
# each entry in matrix has form {'backtrack_pointer' : None, 'prob': 0}
def intialise_matrix_backtrack(words_list, tag_list, matrix):
    for index, word in enumerate(words_list):
            matrix[index] = {}
            for tag in tag_list:
                matrix[index][tag] = {'backtrack_pointer' : None, 'prob': 0}

# Function to calulate next step probability (next tag in seq)
def next_tag_prob(index, tag, tag_list, matrix, trans_prob):
    next_tag_prob = {} 
    for prev_tag in tag_list:
        next_tag_prob[prev_tag] = trans_prob[prev_tag][tag] + matrix[index-1][prev_tag]['prob'] #(best)
    return next_tag_prob
    

def tag_sentence(test_file, model_file, out_file):
    # write your code here. You can add functions as well.

    # read the test file 
    test_file_open = open(test_file, 'r')
    test_file_data = test_file_open.readlines()
    
    # read model_file with results from buildtagger
    model_file_open = open(model_file, 'r')
    model_file_data = model_file_open.read()
    model_file_dict = eval(model_file_data)
    
    tag_count_dict = model_file_dict['tag_count_dict']
    transition_prob = model_file_dict['transition_prob']
    emission_prob = model_file_dict['emission_prob']

    # List of all the unique available tags
    list_of_tags = []
    for tag in tag_count_dict.keys():
        list_of_tags.append(tag)

    # To store the final word\tag sequence of sentences 
    final_output = []

    start = '<s>'
    end = '<end>'
    
    for sentence in test_file_data:
        words_in_sent = sentence.split()
        
        # Matrix implemeneted as a dictionary to store v(t) in viterbi algorithm 
        path_Matrix = {}
        intialise_matrix_backtrack(words_in_sent, list_of_tags, path_Matrix)
         
            
        for index, word in enumerate(words_in_sent):
            
            # For the first word in sentence
            if index == 0:
                for tag in list_of_tags:
                    
                    # First tag in the path would be <s>
                    path_Matrix[index][tag]['backtrack_pointer'] = start
                    
                    if word in emission_prob.keys():
                        # adding log probabilities is same as multiplying individual probabilities 
                        path_Matrix[index][tag]['prob'] = emission_prob[word][tag] + transition_prob[start][tag]
                        
                    else:
                        path_Matrix[index][tag]['prob'] = emission_prob['unknown'][tag] + transition_prob[start][tag]

            # For rest of the words in the sentence
            else:
                for tag in list_of_tags:

                    # For last word in the sentence
                    if index == len(sentence)-1:
                        path_Matrix[index][tag]['prob'] = transition_prob[tag][end] + path_Matrix[index][tag]['prob'] 
                    
                    else:
                        # Dictionary with the probabilities to pick next tag in the seq
                        next_tag_probs = next_tag_prob(index, tag, list_of_tags, path_Matrix, transition_prob)
                        
                        # Pick the tag with highest probability as the backpointer from 
                        best_tag_so_far = max(next_tag_probs, key = next_tag_probs.get)
                        path_Matrix[index][tag]['backtrack_pointer'] = best_tag_so_far

                        if word in emission_prob.keys():
                            path_Matrix[index][tag]['prob'] = next_tag_probs[best_tag_so_far] + emission_prob[word][tag]
                            
                        else:
                            path_Matrix[index][tag]['prob'] = next_tag_probs[best_tag_so_far] + emission_prob['unknown'][tag]
                        
        # Final probabilities and tag sequence
        final_tag_probs = [] 
        for tag in list_of_tags:
            final_tag_probs.append(path_Matrix[len(words_in_sent)-1][tag]['prob'])
            
        tag_with_max_prob = max(final_tag_probs) # tag of last word in sentence
        final_tag = list_of_tags[final_tag_probs.index(tag_with_max_prob)]

        best_seq = []
        
        # final sequence of tags - fill from last to first word of sentence
        for i in range(len(words_in_sent)-1, -1, -1):
            # add current final tag to the best_seq list
            best_seq.append(final_tag)
            
            # update last tag pointer to previous max (backtrack)
            final_tag = path_Matrix[i][final_tag]['backtrack_pointer']

        best_seq.reverse()
        
        # Output sentence of format word/tag 
        output_tagged_sentence = ""
        
        for tag_no,word in enumerate(sentence.split(' ')):
            output_tagged_sentence = output_tagged_sentence + word.rstrip() + '/' + best_seq[tag_no] + ' '
        
        
        final_output.append(output_tagged_sentence)
        
    
    # Write the final_output to a file
    output_file = open(out_file, "w")
    for sentence in final_output:
            output_file.write(sentence + '\n')
    output_file.close()
            
    print('Finished...')
    
    

if __name__ == "__main__":
    # make no changes here
    test_file = sys.argv[1]
    model_file = sys.argv[2]
    out_file = sys.argv[3]
    start_time = datetime.datetime.now()
    tag_sentence(test_file, model_file, out_file)
    end_time = datetime.datetime.now()
    print('Time:', end_time - start_time)
