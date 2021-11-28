import json
import os


def getJson(name, directory="json/"):
    files = os.listdir(directory)
    for file in files:
        if name + ".json" in file:
            with open(os.path.join(directory, file)) as jsonFile:
                data = json.load(jsonFile)
            return data
    return []


def applyJsonConfig(obj, name, directory="json/"):
    res = []
    for k, v in getJson(name, directory=directory).items():
        setattr(obj, k, v)
        res.append(k)
    return res
