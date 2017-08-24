from nltk.tag.stanford import StanfordPOSTagger
from nltk import word_tokenize
import re
import ast

username = "xiaoluguo"
client = "ebay.in"
_path_to_model = "/home/" + username+ "/Product-Queries/stanford_tagger_files/stanford-postagger-2017-06-09/models/english-bidirectional-distsim.tagger"
_path_to_jar = "/home/" + username+ "/Product-Queries/stanford_tagger_files/stanford-postagger-2017-06-09/stanford-postagger.jar"
root = "/mnt/data/pos_" + client + "/"
tpdb_file = root + client + "_tpdb.txt"
dict_file  = root + client + "_dict.txt"
st = StanfordPOSTagger(model_filename=_path_to_model, path_to_jar=_path_to_jar)

data_read = open(dict_file, "r")
data = ast.literal_eval(data_read.read())
data_read.close()

tagged_sentences_read = open(tpdb_file, "r")
tagged_sentences_temp = tagged_sentences_read.read().split("\n")
del tagged_sentences_temp[-1]
tagged_sentences = []
for i in range(len(tagged_sentences_temp)):
    tagged_sentences.append([x for x in ast.literal_eval(tagged_sentences_temp[i])])
tagged_sentences_read.close()

def count(TPP_list):
    TPP_to_freq = {}
    TPP_without_distance = map(lambda x : (x[0], x[1]), TPP_list)
    for TPP in TPP_without_distance:
        TPP_to_freq.setdefault(TPP, 0)
        TPP_to_freq[TPP] += 1
    return TPP_to_freq

def score_function_single( word_query, tagged_sentences):
    word_POS_pairs = []
    for sentence_index in word_query:
        for word_index in word_query[sentence_index]:
            to_add = (tagged_sentences[sentence_index][word_index][0].lower(),tagged_sentences[sentence_index][word_index][1])
            word_POS_pairs.append(to_add)

    TPPDict = count(word_POS_pairs)
    return max(TPPDict, key=lambda key: TPPDict[key])

def all_pairs(lst):
    if len(lst) == 1:
        return lst
    return_list = []
    for i in range(len(lst)-1):
        return_list.append((lst[i], lst[i+1]))
    return return_list

def query_words(list_of_words, main_data_structure):
    result_by_word = {}
    for word in list_of_words:
        if word not in result_by_word:
            result_by_word[word] = main_data_structure.get(word)
    return result_by_word

def get_TPP_and_freq(word_1_query,word_2_query, tagged_sentences, word_list): #queries: {'a': {0: [9], 1: [7], 3: [19], 5: [3]}, 'style': {0: [2], 1: [12], 4: [4]}, 'sleeves': {2: [7]}}
    word_1_index_list = word_1_query.keys()
    word_2_index_list = word_2_query.keys()
    word_POS_pairs = []
    common_sentences = set(word_1_index_list) & set(word_2_index_list)
    print("common_sentences", common_sentences)
    
    if len(word_1_index_list) != 0 and len(word_2_index_list) != 0 and len(common_sentences) == 0:
	tag_1 = score_function_single(word_1_query, tagged_sentences)
	tag_2 = score_function_single(word_2_query, tagged_sentences)
	return [(tag_1, tag_2,2)]

    for sentence_index in common_sentences:
        for word_index in word_1_query[sentence_index]:
            for word_2_index in word_2_query[sentence_index]:
                distance = abs(word_index- word_2_index)
                to_add = ((tagged_sentences[sentence_index][word_index][0].lower(),tagged_sentences[sentence_index][word_index][1]), (tagged_sentences[sentence_index][word_2_index][0].lower(),tagged_sentences[sentence_index][word_2_index][1]), distance)
                word_POS_pairs.append(to_add)
    print("word_POS_pairs", word_POS_pairs) 
    return(word_POS_pairs) 
    #freq_dict = count(word_POS_pairs) #like freq dictionary returns {(t_1, POS_1): 1, (t_2, POS_2) : 3, ...}
    #return freq_dict

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

    query = query_words(search_words, data) #returns a big dictionary of all positions of the words in the corpus {'long': {0: [2], 1: [12], 4: [4]}, 'sleeves': {2: [7]}}
    list_of_freq_dict, list_of_freq_dict_A, list_of_freq_dict_B = [],[],[]

    search_words_temp = search_words[:]
    search_words = [x for x in search_words if query[x] is not None]
    other_words = [x for x in search_words_temp if query[x] is None] 
    
    result =[]
    if len(other_words)!=0:
        result.extend(st.tag(other_words))
    
    if len(search_words) == 1:
        if query[search_words[0]] == None:
            result.extend(st.tag([search_words[0]]))
            return result 

        result.append(score_function_single( query[search_words[0]], tagged_sentences))
        return result

    word_pairs = all_pairs(search_words)

    for word_1, word_2 in word_pairs:
        word_POS_pairs_A, word_POS_pairs_B = [],[]
	word_POS_pairs = get_TPP_and_freq(query[word_1],query[word_2], tagged_sentences,[word_1,word_2]) #only gets consecutive pairs and their tag [(t_1, POS_1), (t_2, POS_2), ...]
        if len(word_pairs) ==1:
            freq_dict = count(word_POS_pairs)
	    if len(freq_dict) == 0:
		st_tag = st.tag([word_1, word_2])
		list_of_freq_dict.append({st_tag[0]:.5})
		continue
            list_of_freq_dict.append(freq_dict)

	    term_POS_pairs = scoring_function_most_likelihood(word_pairs, list_of_freq_dict) #returns the tag of word pairs
	    result.extend(term_POS_pairs)
	    continue
        for x in word_POS_pairs:
            if x[2]==1:
                word_POS_pairs_A.append(x)
            else: 
                word_POS_pairs_B.append(x)
        freq_dict_A = count(word_POS_pairs_A)
        freq_dict_B = count(word_POS_pairs_B)
        if len(freq_dict_B) == 0 and len(freq_dict_A) == 0:
            st_tag = st.tag([word_1, word_2])
            list_of_freq_dict_B.append({st_tag[0]:.5})
        if len(freq_dict_A)!=0:
            list_of_freq_dict_A.append(freq_dict_A)
        if len(freq_dict_B)!=0:
            list_of_freq_dict_B.append(freq_dict_B)      
        
    term_POS_pairs_A = []
    term_POS_pairs_A_first = []
    if len(list_of_freq_dict_A)!= 0:
	term_POS_pairs_A = scoring_function_most_likelihood(word_pairs, list_of_freq_dict_A) #returns the tag of word pairs
	result.extend(term_POS_pairs_A)
    results_first = [x[0] for x in result]
    term_POS_pairs_A_first = [x[0] for x in term_POS_pairs_A if x[0] not in results_first]
    term_POS_pairs_B = scoring_function_most_likelihood(word_pairs, list_of_freq_dict_B)
    result.extend([x for x in term_POS_pairs_B if x[0] not in term_POS_pairs_A_first and x[0] not in results_first])
    return result

while True:
    word = raw_input("Enter your search term: ---> ")
    if word == "":
        continue
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




