from nltk.tag.stanford import StanfordPOSTagger
import nltk
import re

username = "abishkarchhetri"
_path_to_model = "/home/" + username+ "/Product-Queries/stanford_tagger_files/stanford-postagger-2017-06-09/models/english-bidirectional-distsim.tagger" 
_path_to_jar = "/home/" + username+ "/Product-Queries/stanford_tagger_files/stanford-postagger-2017-06-09/stanford-postagger.jar"



def create_data_structure(long_string):
    st = StanfordPOSTagger(model_filename=_path_to_model, path_to_jar=_path_to_jar)
    main_data_structure = {}    
    sentences_with_tag = []
    sentences = re.split("\. |\n", long_string)
    print("sentences",sentences)    
    for sentence_index in range(len(sentences)): 
        tocanized = nltk.word_tokenize(sentences[sentence_index])
    	tagged = st.tag(tocanized)
	sentences_with_tag.append(tagged)
	
	for (word, tag) in tagged:
	    if word not in main_data_structure:
		main_data_structure[word] = [sentence_index]
	    else:
		main_data_structure[word].append(sentence_index)

    return (main_data_structure, sentences_with_tag) 
