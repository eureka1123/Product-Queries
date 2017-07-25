import requests
import json
import nltk

url = "http://pcsync-01/shoppersstop.com/pcf_catalog.json"
file_request = requests.get(url, stream = True)

def lazy_json_read_line(line):
    try:
        line_json = json.loads(line[line.index("{"):len(line)-1])
        line_description = line_json["description"]
        return line_description
    except:
        return "error"


for line in file_request.iter_lines():
    print(lazy_json_read_line(line))
