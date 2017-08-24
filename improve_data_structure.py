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

counter = 1.0
for k in data.keys():
    print(counter/len(data))
    if len(data[k]) == 1:
       for s in data[k].keys():
           tagged_sentences[s] == ""
       del data[k]

d = open(dict_file+"1", "w")
d.write(str(data))

t = open(tpdb_file+"1", "w")
t.write(str(tagged_sentences))

