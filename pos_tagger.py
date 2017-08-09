from nltk.tag.stanford import StanfordPOSTagger
from nltk import word_tokenize
import re
from timer import Timer
import ast

username = "abishkarchhetri"
client = "shoppersstop.com"
_path_to_model = "/home/" + username+ "/Product-Queries/stanford_tagger_files/stanford-postagger-2017-06-09/models/english-bidirectional-distsim.tagger"
_path_to_jar = "/home/" + username+ "/Product-Queries/stanford_tagger_files/stanford-postagger-2017-06-09/stanford-postagger.jar"
root = "/home/" + username + "/Product-Queries/"
tpdb_file = root + client + "_tpdb.txt"
dict_file  = root + client + "_dict.txt"
st = StanfordPOSTagger(model_filename=_path_to_model, path_to_jar=_path_to_jar)

data_read = open(dict_file, "r")
data = ast.literal_eval(data_read.read())
data_read.close()

tagged_sentences_read = open(tpdb_file, "r")
tagged_sentences_temp = tagged_sentences_read.read().split("\n")
del tagged_sentences_temp[len(tagged_sentences_temp)-1]
tagged_sentences = []
for i in range(len(tagged_sentences_temp)):
    tagged_sentences.append([x for x in ast.literal_eval(tagged_sentences_temp[i])])
tagged_sentences_read.close()

def count(TPP_list):
    TPP_to_freq = {}
    TPP_without_distance = map(lambda x : (x[0], x[1]), TPP_list)
    for TPP in TPP_without_distance:
        if TPP not in TPP_to_freq:
            TPP_to_freq[TPP] = 1
        else:
            TPP_to_freq[TPP] += 1
    return TPP_to_freq

def get_max_from_TPP_dict(TPDict):
    max_freq_TPP = None
    current_max = 0
    for entry in TPDict:
        if TPDict[entry] > current_max:
            current_max = TPDict[entry]
            max_freq_TPP = entry
    return (current_max, max_freq_TPP)

def score_function_single( word_query, tagged_sentences):
    word_POS_pairs = []
    for sentence_index in word_query:
        for word_index in word_query[sentence_index]:
            to_add = tagged_sentences[sentence_index][word_index]
            word_POS_pairs.append(to_add)

    TPPDict = count(word_POS_pairs)
    return get_max_from_TPP_dict(TPPDict)[1]

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
    return None

def query_words(list_of_words, main_data_structure):
    result_by_word = {}
    for word in list_of_words:
        if word not in result_by_word:
            result_by_word[word] = find_words(word, main_data_structure)
    return result_by_word

def get_TPP_and_freq(word_1_query,word_2_query, tagged_sentences, word_list): #queries: {'a': {0: [9], 1: [7], 3: [19], 5: [3]}, 'style': {0: [2], 1: [12], 4: [4]}, 'sleeves': {2: [7]}}
    word_1_index_list = word_1_query.keys()
    word_2_index_list = word_2_query.keys()
    word_POS_pairs = []
    common_sentences = set(word_1_index_list) & set(word_2_index_list)
    print("common_sentences", common_sentences)
    
    if len(word_1_index_list) != 0 and len(word_2_index_list) != 0 and len(common_sentences) == 0:
	tag_1 = score_function_single(word_1_query, tagged_sentences)
	tag_2 = score_function_single( word_2_query, tagged_sentences)
	print(tag_1, tag_2)
	return {(tag_1, tag_2):1}

    for sentence_index in common_sentences:
        for word_index in word_1_query[sentence_index]:
            for word_2_index in word_2_query[sentence_index]:
                distance = abs(word_index- word_2_index)
                to_add = ((tagged_sentences[sentence_index][word_index][0].lower(),tagged_sentences[sentence_index][word_index][1]), (tagged_sentences[sentence_index][word_2_index][0].lower(),tagged_sentences[sentence_index][word_2_index][1]), distance)
                word_POS_pairs.append(to_add)
    # with Timer() as t:
    #     freq_dict = count(TPP_list)
    # print("=> elasped fre_dict: {} s".format(t.secs))
    freq_dict = count(word_POS_pairs) #like freq dictionary returns {(t_1, POS_1): 1, (t_2, POS_2) : 3, ...}
    return freq_dict

def get_max_norm_freq_from_TPP_dict(TPDict):
    total = float(sum(TPDict.values()))
    max_freq_TPP = None
    current_max = 0
    for entry in TPDict:
        if (TPDict[entry]/total) > current_max:
            current_max = TPDict[entry]/total
            max_freq_TPP = entry
    return (current_max, max_freq_TPP)

def scoring_function_most_likelihood(word_pairs, list_freq_dict): #make it more efficient
    word_to_POS = {} #{word: {pos: <tag>, max_freq: <number>}}
    result = []
    print("list_freq_dict",list_freq_dict)
    for TPDict in list_freq_dict: #TPDict = {(w1, t1): 3, ....}
        norm_freq, max_freq_TPP = get_max_norm_freq_from_TPP_dict(TPDict)
        for (word, tag) in max_freq_TPP:
            if word not in word_to_POS:
                word_to_POS[word] = {}
                word_to_POS[word]["POS"] = tag
                word_to_POS[word]["max_freq"] = norm_freq
            elif norm_freq > word_to_POS[word]["max_freq"]:
                word_to_POS[word]["POS"] = tag
                word_to_POS[word]["max_freq"] = norm_freq

    for word in word_to_POS:
        result.append((word, word_to_POS[word]["POS"]))
    return result

def get_tag_complete(search_words): #need to fix for single word search

    # with Timer() as t:
    #     query = query_words(search_words, data) #returns a big dictionary of all positions of the words in the corpus {'long': {0: [2], 1: [12], 4: [4]}, 'sleeves': {2: [7]}}
    # print("=> elasped query: {} s".format(t.secs))
    query = query_words(search_words, data) #returns a big dictionary of all positions of the words in the corpus {'long': {0: [2], 1: [12], 4: [4]}, 'sleeves': {2: [7]}}
    list_of_freq_dict = []

    #print(query)
    # with Timer() as t:
    #     word_pairs = all_pairs(search_words)
    # print("=> elasped word_pairs: {} s".format(t.secs))
    search_words_temp = search_words
    search_words = [x for x in search_words if query[x] is not None]
    other_words = [x for x in search_words_temp if query[x] is None] 
    
    print("other_words", other_words) 
    result =[]
    if len(other_words)!=0:
        result.append(st.tag(other_words))
    
    if len(search_words) == 1:
        if query[search_words[0]] == None:
            result.append(st.tag([search_words[0]]))
            return result 
        print("result", result)

        result.append(score_function_single( query[search_words[0]], tagged_sentences))
        return result

    word_pairs = all_pairs(search_words)
    
    for word_1, word_2 in word_pairs:
        
	# with Timer() as t:
	#     TPP_list = get_TPP(query[word_1],query[word_2], tagged_sentences) #only gets consecutive pairs and their tag [(t_1, POS_1), (t_2, POS_2), ...]
	# print("=> elasped TPP_list: {} s".format(t.secs))
	freq_dict = get_TPP_and_freq(query[word_1],query[word_2], tagged_sentences,[word_1,word_2]) #only gets consecutive pairs and their tag [(t_1, POS_1), (t_2, POS_2), ...]
	if len(freq_dict) == 0:
	    result.append(st.tag(search_words))
            return result

	# with Timer() as t:
	#     list_of_freq_dict.append(freq_dict)
	# print("=> elasped list_of_freq_dict: {} s".format(t.secs))

	list_of_freq_dict.append(freq_dict)

    with Timer() as t:
	term_POS_pairs = scoring_function_most_likelihood(word_pairs, list_of_freq_dict)
    print("=> elasped term_POS_pairs: {} s".format(t.secs))
    #term_POS_pairs = scoring_function_most_likelihood(word_pairs, list_of_freq_dict) #returns the tag of word pairs
    result.append(term_POS_pairs)
    return result

while True:
    word = raw_input("Enter your search term: ---> ")
    word = [item.lower() for item in word.split(" ")]

    print(get_tag_complete(word))



#test

# def get_data_from_label(sentence_label):
#     data = {}
#     for sentence_index in range(len(sentence_label)):
#         for word_index in range(len(sentence_label[sentence_index])):
#             word = sentence_label[sentence_index][word_index][0]
#             if word not in data:
#                 data[word] = {}
#                 data[word][sentence_index] = [word_index]
#             else:
#                 if sentence_index in data[word]:
#                     data[word][sentence_index].append(word_index)
#                 else:
#                     data[word][sentence_index] = [word_index]

#     return data


# tagged_sentences = [[("t_A", "p_1"), ("t_C", "p_2"), ("t_D", "p_4")]*5,
#                   [("t_A", "p_1"), ("t_C", "p_3")]*4,
#                   [("t_A", "p_2"), ("t_C", "p_4")]*7,

#                   [("t_A", "p_1"), ("t_C", "p_2")]*3,
#                   [("t_A", "p_3"), ("t_C", "p_3")]*6,

#                   [("t_B", "p_1"), ("t_C", "p_2"), ("t_D", "p_6")]*4,
#                   [("t_B", "p_2"), ("t_C", "p_2")]*5]
# with Timer() as t:
#     data = get_data_from_label(tagged_sentences)
# print("=> elasped generate_data_dict: {} s".format(t.secs))


# print("result ",get_tag_complete(["t_K"]))




