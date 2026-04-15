from JsonParser.ParsedJson import loadJson
from TreeStructure.CreateTree import JsonTree

def quickJedi(t1: JsonTree, t2: JsonTree):
    subproblem = 0 
    numSkips = 0
    numMatchings = 0 
    numEditSkips = 0 
    numEdits = 0

        

def main():
    js1 = loadJson("./QuickJedi/testFile1.txt")
    js2 = loadJson("./QuickJedi/testFile2.txt")

    t1 = JsonTree(js1)
    t2 = JsonTree(js2)

    print(t2.height, t2.size, t2.degree)


if __name__ == "__main__":
    main()