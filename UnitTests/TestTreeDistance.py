from JsonParser.ParsedJson import loadJson
from TreeStructure.CreateTree import JsonTree
from TreeStructure.TreeDistance import JediDistance

def main():
    path1 = "./UnitTests/TreeStructurePackageTestFile.txt"
    data1 = loadJson(path1)
    tree1 = JsonTree(data1)

    path2 = "./UnitTests/JsonParserPackageTestFile.txt"
    data2 = loadJson(path2)
    tree2 = JsonTree(data2)

    tree1.printTreeBFS()
    tree2.printTreeBFS()

    dist_computer = JediDistance(tree1, tree2)

    dist_computer.jedi_baseline()




if __name__ == "__main__":
    main()