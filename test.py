import json

file_path = "nakup.json"
with open(file_path, "r", encoding="utf-8") as json_file:
    print(json.load(json_file)["data"])
