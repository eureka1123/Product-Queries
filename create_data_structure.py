from nltk.tag.stanford import StanfordPOSTagger
import nltk

_path_to_model = "/home/abishkarchhetri/Product-Queries/stanford_tagger_files/stanford-postagger-2017-06-09/models/english-bidirectional-distsim.tagger" 
_path_to_jar = "/home/abishkarchhetri/Product-Queries/stanford_tagger_files/stanford-postagger-2017-06-09/stanford-postagger.jar"

st = StanfordPOSTagger(model_filename=_path_to_model, path_to_jar=_path_to_jar)

text = nltk.word_tokenize("Forever Is The best") 

a = st.tag(text)
print(a)
