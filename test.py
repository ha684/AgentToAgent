import json


with open("./ncc_data/all_data.json", "r",encoding="utf8") as f:
    data = json.load(f)
    
print(data[0]["content"])