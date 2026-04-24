from JsonParser.ParsedJson import loadJson
from TreeStructure.CreateTree import JsonTree

def main():
    path = "./UnitTests/TreeStructurePackageTestFile.txt"
    data = loadJson(path)
    tree = JsonTree(data)

    tree.printTreeBFS()
    node = tree.root

    print(node.children[0].label)

if __name__ == "__main__":
    main()