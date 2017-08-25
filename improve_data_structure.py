import re
import ast

username = "xiaoluguo"
client = "ebay.in"
root = "/mnt/data/pos_" + client + "/"
tpdb_file = root + client + "_tpdb.txt"
dict_file  = root + client + "_dict.txt"

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

for k in data.keys():
    if len(data[k]) < 5:
       for s in data[k].keys():
           tagged_sentences[s] = ["IGNORE"]
       del data[k]

d = open(dict_file, "w")
d.write(str(data))

t = open(tpdb_file, "w").close()
t = open(tpdb_file, "a")

for i in range(len(tagged_sentences)):
    t.write(str(tagged_sentences[i]).strip('[]'))
    t.write("\n")

