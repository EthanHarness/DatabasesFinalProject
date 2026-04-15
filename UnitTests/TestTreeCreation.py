from JsonParser.ParsedJson import loadJson
from TreeStructure.CreateTree import JsonTree

def main():
    path = "./UnitTests/TreeStructurePackageTestFile.txt"
    data = loadJson(path)
    tree = JsonTree(data)

    tree.printTreeBFS()

if __name__ == "__main__":
    main()