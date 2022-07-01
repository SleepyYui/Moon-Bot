import json
with open(f"test.json",'r') as f:
    content = json.load(f)
print(str(content) + "\n" + str(content["12345"]["2038769824"]))