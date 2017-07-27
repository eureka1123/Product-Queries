from nltk.tag.stanford import StanfordPOSTagger
import nltk
import re
import requests
import json
from multiprocessing.pool import ThreadPool as Pool

client = "shoppersstop.com"
url = "http://pcsync-01/" + client + "/pcf_catalog.json"
file_request = requests.get(url, stream = True)

username = "xiaoluguo"
root = "/home/" + username + "/Product-Queries/"
_path_to_model = root +  "stanford_tagger_files/stanford-postagger-2017-06-09/models/english-bidirectional-distsim.tagger" 
_path_to_jar = root + "stanford_tagger_files/stanford-postagger-2017-06-09/stanford-postagger.jar"
tpdb_file_pre = root + client + "_tpdb_pre.txt"
tpdb_file = root + client + "_tpdb.txt"

pool = Pool(4)

def lazy_json_read_line(line):
    try:
        line_json = json.loads(line[line.index("{"):len(line)-1])
        line_description = line_json["description"]
        return line_description
    except:
        return "error"

f = open(tpdb_file_pre, "w").close()
f = open(tpdb_file_pre, "a")

for line in file_request.iter_lines():
    f.write(lazy_json_read_line(line))
    f.write("\n")

f.close()

def check_not_all_capitalized(tokenized):
    for word in tokenized:
        if word.islower():
            return True
    return False

main_data_structure = {}
sentences_with_tag = []

f = open(tpdb_file, "w").close()
f = open(tpdb_file, "a")

def create_data_structure(long_string):
    st = StanfordPOSTagger(model_filename=_path_to_model, path_to_jar=_path_to_jar)
    sentences = re.split("\. |\n", long_string)
    # print("sentences",sentences)
    for sentence_index in range(len(sentences)):
        tokenized = nltk.word_tokenize(sentences[sentence_index])
        if check_not_all_capitalized(tokenized):
            tagged = st.tag(tokenized)
            sentences_with_tag.append(tagged)
            print(tagged)
            f.write(str(tagged).strip('[]'))
            f.write("\n")

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

with open(tpdb_file_pre) as myfile:
    corpus = myfile.read()

sample_string = "Some things never change. Do they? never"

T = pool.map(create_data_structure(corpus))
f.close()

print(data)
print(sentences)
