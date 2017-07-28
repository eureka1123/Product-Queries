
from nltk.tag.stanford import StanfordPOSTagger
from nltk import word_tokenize
import re

username = "abishkarchhetri"
_path_to_model = "/home/" + username+ "/Product-Queries/stanford_tagger_files/stanford-postagger-2017-06-09/models/english-bidirectional-distsim.tagger"
_path_to_jar = "/home/" + username+ "/Product-Queries/stanford_tagger_files/stanford-postagger-2017-06-09/stanford-postagger.jar"

#_path_to_model = "/Users/abishkarchhetri/Downloads/stanford-postagger-2017-06-09/models/english-bidirectional-distsim.tagger"
#_path_to_jar = "/Users/abishkarchhetri/Downloads/stanford-postagger-2017-06-09/stanford-postagger.jar"

def create_data_structure(long_string):
    st = StanfordPOSTagger(model_filename=_path_to_model, path_to_jar=_path_to_jar)
    main_data_structure = {}
    sentences_with_tag = []
    sentences = re.split("\. |\n", long_string)
    #print("sentences",sentences)
    for sentence_index in range(len(sentences)):
        tokenized = word_tokenize(sentences[sentence_index])
        tagged = st.tag(tokenized)
        sentences_with_tag.append(tagged)

        for word_index in range(len(tagged)):
            word = tagged[word_index][0]

            if word not in main_data_structure:
                main_data_structure[word] = {}
                if sentence_index not in main_data_structure[word]:
                    main_data_structure[word][sentence_index] =  [word_index]
                else:
                    main_data_structure[word][sentence_index].append(word_index)
            else:
                #main_data_structure[word].append((sentence_index, word_index))
                if sentence_index not in main_data_structure[word]:
                    main_data_structure[word][sentence_index] =  [word_index]
                else:
                    main_data_structure[word][sentence_index].append(word_index)

    return (main_data_structure, sentences_with_tag)

sample_corpus = "Epitome of orange and trend, this t-shirt is a must-have. the orange color The all over graphical print the orange and trend takes it a notch higher on the orange scale. the orange color it comes with short side-slits and dolman sleeves for an added allure.\nHow To Use: Apply directly onto the lips from the tube or use the Retractable Lip Brush for a more precise application.\nCarry your essentials in style by using this sling bag from Hidesign. It comes with a long strap, which will help you to carry it with ease. It also features one main compartment that will provide you adequate space to keep your stuff in place. Moreover, it has been made of premium quality leather that makes it easy to maintain."

data, tagged_sentences = create_data_structure(sample_corpus)

data_file = open("data.txt", "w")
data_file.write(str(data))

#data_file = open("tagged_sentences.txt", "w")
#data_file.write(str(tagged_sentences))

#data = open("data.txt", "r")
#data = eval(data.read())

#tagged_sentences = open("tagged_sentences.txt", "r")
#tagged_sentences = eval(tagged_sentences.read())

# print("tagged",tagged_sentences)
# print("data",data)


def all_pairs(lst):
    if len(lst) == 1:
        return lst
    return_list = []
    for i in range(len(lst)-1):
        return_list.append((lst[i], lst[i+1]))
    return return_list

def find_words(word, main_data_structure):
    if word in main_data_structure:
        return main_data_structure[word]
    else:
        return None

def query_words(list_of_words, main_data_structure):
    result_by_word = {}
    for word in list_of_words:
        if word not in result_by_word:
            result_by_word[word] = find_words(word, main_data_structure)
    return result_by_word

def count(TPP_list):
    TPP_to_freq = {}
    for TPP in TPP_list:
        if TPP not in TPP_to_freq:
            TPP_to_freq[TPP] = 1
        else:
            TPP_to_freq[TPP] += 1
    return TPP_to_freq
    
def get_TPP(word_1_query,word_2_query, tagged_sentences): #queries: {'a': {0: [9], 1: [7], 3: [19], 5: [3]}, 'style': {0: [2], 1: [12], 4: [4]}, 'sleeves': {2: [7]}}
    
    word_1_index_list = word_1_query.keys()
    word_2_index_list = word_2_query.keys()

    word_POS_pairs = []
    common_sentences = set(word_1_index_list) & set(word_2_index_list)

    for sentence_index in common_sentences:
        #print(sentence_index)
        for word_index in word_1_query[sentence_index]:
            #print("word_index", word_index)
            #print("here", word_1_query[sentence_index])
            if word_index+1 in word_2_query[sentence_index]:
                to_add = (tagged_sentences[sentence_index][word_index], tagged_sentences[sentence_index][word_index+1])
                word_POS_pairs.append(to_add)

    return word_POS_pairs

def get_max_from_TPP_dict(TPDict):
    max_freq_TPP = None
    current_max = 0
    for entry in TPDict:
        if TPDict[entry] > current_max:
            current_max = TPDict[entry]
            max_freq_TPP = entry
    return (current_max, max_freq_TPP)

def get_max_norm_freq_from_TPP_dict(TPDict):
    total = float(sum(TPDict.values()))
    max_freq_TPP = None
    current_max = 0
    for entry in TPDict:
        if (TPDict[entry]/total) > current_max:
            current_max = TPDict[entry]
            max_freq_TPP = entry
    return (current_max, max_freq_TPP)


def scoring_function_max_freq(word_pairs, list_freq_dict): #make it more efficient
    word_to_POS = {} #{word: {pos: <tag>, max_freq: <number>}}
    result = []

    for TPDict in list_freq_dict:
        score, max_freq_TPP = get_max_from_TPP_dict(TPDict)

        for (word, tag) in max_freq_TPP:
            if word not in word_to_POS:
                word_to_POS[word] = {}
                word_to_POS[word]["POS"] = tag
                word_to_POS[word]["max_freq"] = score
            else:
                if score > word_to_POS[word]["max_freq"]:
                    word_to_POS[word]["POS"] = tag
                    word_to_POS[word]["max_freq"] = score

    for word in word_to_POS:
        result.append((word, word_to_POS[word]["POS"]))
    return result

def scoring_function_most_likelihood(word_pairs, list_freq_dict): #make it more efficient
    word_to_POS = {} #{word: {pos: <tag>, max_freq: <number>}}
    result = []

    for TPDict in list_freq_dict:
        norm_freq, max_freq_TPP = get_max_norm_freq_from_TPP_dict(TPDict)

        for (word, tag) in max_freq_TPP:
            if word not in word_to_POS:
                word_to_POS[word] = {}
                word_to_POS[word]["POS"] = tag
                word_to_POS[word]["max_freq"] = norm_freq
            else:
                if norm_freq > word_to_POS[word]["max_freq"]:
                    word_to_POS[word]["POS"] = tag
                    word_to_POS[word]["max_freq"] = norm_freq

    for word in word_to_POS:
        result.append((word, word_to_POS[word]["POS"]))
    return result

def scoring_function_all_combi(word_pairs, list_freq_dict): #make it more efficient
    word_to_POS = {} #{word: {pos: <tag>, max_freq: <number>}}
    result = []

    for TPDict in list_freq_dict:
        #norm_freq, max_freq_TPP = get_max_norm_freq_from_TPP_dict(TPDict)
        for TPPtuple in TPDict:
            norm_freq = TPDict[TPPtuple]
            for (word, tag) in TPPtuple:
                if word not in word_to_POS:
                    word_to_POS[word] = {}
                    word_to_POS[word]["POS"] = tag
                    word_to_POS[word]["norm_freq"] = norm_freq
                else:
                    if norm_freq > word_to_POS[word]["norm_freq"]:
                        word_to_POS[word]["POS"] = tag
                        word_to_POS[word]["norm_freq"] = norm_freq

    for word in word_to_POS:
        result.append((word, word_to_POS[word]["POS"]))
    return result

def get_tag_complete(search_words):
    query = query_words(search_words, data) #returns a big dictionary of all positions of the words in the corpus {style': {0: [2], 1: [12], 4: [4]}, 'sleeves': {2: [7]}}
    list_of_freq_dict = []
    
    word_pairs = all_pairs(search_words)
    #print(word_pairs)
    #print(query)

    for word_1, word_2 in word_pairs:
        TPP_list = get_TPP(query[word_1],query[word_2], tagged_sentences) #only gets consecutive pairs and their tag [(t_1, POS_1), (t_2, POS_2), ...]
            
        #print("TPP_list",TPP_list)
        freq_dict = count(TPP_list) #like freq dictionary returns {(t_1, POS_1): 1, (t_2, POS_2) : 3, ...}

        #print(freq_dict)
        list_of_freq_dict.append(freq_dict)

    print(list_of_freq_dict)
    word_POS_pairs = scoring_function_all_combi(word_pairs, list_of_freq_dict) #returns the tag of word pairs

    print(word_POS_pairs)
    return word_POS_pairs


get_tag_complete(["the", "orange", "and", "trend"])



