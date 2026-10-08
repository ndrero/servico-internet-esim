import json

def json_write(json_data, file_name):
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(json_data, file, indent=4, ensure_ascii=False)

def json_read(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data
