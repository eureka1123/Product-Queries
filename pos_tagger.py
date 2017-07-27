from nltk.tag.stanford import StanfordPOSTagger
from nltk import word_tokenize
import re

username = "abishkarchhetri"
_path_to_model = "/home/" + username+ "/Product-Queries/stanford_tagger_files/stanford-postagger-2017-06-09/models/english-bidirectional-distsim.tagger"
_path_to_jar = "/home/" + username+ "/Product-Queries/stanford_tagger_files/stanford-postagger-2017-06-09/stanford-postagger.jar"

# _path_to_model = "/Users/abishkarchhetri/Downloads/stanford-postagger-2017-06-09/models/english-bidirectional-distsim.tagger"
# _path_to_jar = "/Users/abishkarchhetri/Downloads/stanford-postagger-2017-06-09/stanford-postagger.jar"

st = StanfordPOSTagger(model_filename=_path_to_model, path_to_jar=_path_to_jar)

def create_data_structure(list_string):
    #st = StanfordPOSTagger(model_filename=_path_to_model, path_to_jar=_path_to_jar)
    main_data_structure = {}
    sentences_with_tag = []
    sentences = []
    for par in list_string:
        sentences.extend(re.split("\. |\n", par))
    #print("sentences",sentences)
    for sentence_index in range(len(sentences)):
        tokenized = word_tokenize(sentences[sentence_index])
        tagged = st.tag(tokenized)
        sentences_with_tag.append(tagged)

        for word_index in range(len(tagged)):
            word = str(tagged[word_index][0]).lower()

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

sample_corpus = ["Epitome of style and trend, this t-shirt is a must-have. The all over graphical print takes it a notch higher on the style scale. It comes with short side-slits and dolman sleeves for an added allure.\nHow To Use: Apply directly onto the lips from the tube or use the Retractable Lip Brush for a more precise application.\nCarry your essentials in style by using this sling bag from Hidesign. It comes with a long strap, which will help you to carry it with ease. It also features one main compartment that will provide you adequate space to keep your stuff in place. Moreover, it has been made of premium quality leather that makes it easy to maintain."]


with open("shoppersstop.com_tpdb.txt") as myfile:
    sample_corpus_2 = []
    for i in range(5):
	sample_corpus_2.append(myfile.readline().strip("\n")) 

#print(sample_corpus_2)

data, tagged_sentences = create_data_structure(sample_corpus_2)


#print(tagged_sentences)

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

def get_freq_dict(words_index_in_dict, tagged_sentences):
    word_to_tag = {}
    for word in words_index_in_dict:
        if word not in word_to_tag:
            word_to_tag[word] = {}
        for sentence_index in words_index_in_dict[word]:
            word_index = words_index_in_dict[word][sentence_index][0] #only considering one word from the sentence
            tag = tagged_sentences[sentence_index][word_index][1]
            if tag in word_to_tag[word]:
                word_to_tag[word][tag] += 1
            else:
                word_to_tag[word][tag] = 1

    return word_to_tag

def get_tags(freq_dict):
    word_to_tag_final = []
    for word in freq_dict:
        max_tag = ""
        max_freq = 0
        for tag in freq_dict[word]:
            if freq_dict[word][tag] > max_freq:
                max_freq = freq_dict[word][tag]
                max_tag = tag
        word_to_tag_final.append((word, tag))

    return word_to_tag_final

words = raw_input("Type your query separated with space: ")
words = words.split(" ")
#words = ["red", "dress"]
words_index_in_dict = query_words(words, data)
#print(words_index_in_dict)
freq_dict = get_freq_dict(words_index_in_dict, tagged_sentences)
#print(freq_dict)
final_tag = get_tags(freq_dict)
print(final_tag)

