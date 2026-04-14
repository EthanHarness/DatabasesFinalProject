from JsonParser.JsonParser import loadJson
from TreeStructure.CreateTree import JsonTree

def main():
    path = "./TreeStructure/testJson.txt"
    data = loadJson(path)
    tree = JsonTree(data)


if __name__ == "__main__":
    main()