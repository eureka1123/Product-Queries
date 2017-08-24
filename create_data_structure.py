from os import popen
from nltk.tag.stanford import StanfordPOSTagger
from nltk import word_tokenize
import nltk
import re
import requests
import json
import nlpnet

client = "shoppersstop.com"
url = "http://pcsync-01/" + client + "/pcf_catalog.json"
file_request = requests.get(url, stream = True)

username = "xiaoluguo"
root1 = "/mnt/data/pos_" + client + "/"
root = "/home/" + username + "/Product-Queries/"
_path_to_model = root +  "stanford_tagger_files/stanford-postagger-2017-06-09/models/english-bidirectional-distsim.tagger" 
_path_to_jar = root + "stanford_tagger_files/stanford-postagger-2017-06-09/stanford-postagger.jar"
tpdb_file_pre = root1 + client + "_tpdb_pre.txt"
tpdb_file_filter = root1 + client + "_tpdb_filter.txt"
tpdb_file = root1 + client + "_tpdb.txt"
dict_file  = root1 + client + "_dict.txt"
tag_list = ["JJ","JJR","JJS","NN","NNS","NNP","NNPS","VB","VBD","VBG","VBN","VBP","VBZ"]

try:
    popen('mkdir ' + root1)
except:
    pass
def lazy_json_read_line(line):
    try:
        line_json = json.loads(line[line.index("{"):-1])
        line_description = line_json["description"]
        return line_description
    except:
        return "error"

f = open(tpdb_file_pre, "w").close()
f = open(tpdb_file_pre, "a")

for line in file_request.iter_lines():
    try:
        f.write(lazy_json_read_line(line).replace("\n",""))
        f.write("\n")
    except:
        pass

f.close()

f = open(tpdb_file_pre, "r")
set_input = set(f.read().split("\n"))
f.close()

f1 = open(tpdb_file_filter, "w")
f1.write('\n'.join(set_input))
f1.close()

def check_not_all_capitalized(tokenized):
    count = 0.0
    for word in tokenized:
        if word.islower():
            count +=1
    if (count/float(len(tokenized))>.3):
	return True
    return False

def check_has_verb(tagged):
    for word in tagged:
        if word[1] in ["VB","VBD","VBG","VBN","VBP","VBZ"]:
            return True
    return False

counter = 0
main_data_structure = {}
sentences_with_tag = []

f = open(tpdb_file, "w").close()
f = open(tpdb_file, "a")
t = open("temp_sentences.txt", "w").close()
t = open("temp_sentences.txt", "a")

def create_data_structure(long_string):
    global counter
    global main_data_structure 
    global sentences_with_tag
    st = StanfordPOSTagger(model_filename=_path_to_model, path_to_jar=_path_to_jar)
    tagger = nlpnet.POSTagger("/mnt/static/nlpnet-en", language ="en")
    sentences = re.split("\. |\n", long_string)
    for sentence_index in range(len(sentences)):
        print(sentence_index*100.0/float(len(sentences)))
        tokenized = word_tokenize(sentences[sentence_index])
        if len(tokenized)!=0 and check_not_all_capitalized(tokenized):
            tagged = tagger.tag(sentences[sentence_index])[0]
            if check_has_verb(tagged):
                t.write(sentences[sentence_index])
                t.write("\n")
                sentences_with_tag.append(tagged)
                f.write(str(tagged).strip('[]'))
                f.write("\n")
		for word_index in range(len(tagged)):
		    word = tagged[word_index][0].lower()
		    word_in_dict = main_data_structure.setdefault(word, {})
		    word_index_list = word_in_dict.setdefault(counter, [])
		    word_index_list.append(word_index)
                counter+=1 
        if sentence_index%10000==0:
            p = open(dict_file, "w")
	    p.write(str(main_data_structure))
            p.close()
    return (main_data_structure, sentences_with_tag)

with open(tpdb_file_filter) as myfile:
    corpus = myfile.read()

sample_string = "Some things never change. Do they? never"
main_data_structure, sentences_with_tag = create_data_structure(corpus)
p = open(dict_file, "w")
p.write(str(main_data_structure))
p.close()
f.close()
t.close()
