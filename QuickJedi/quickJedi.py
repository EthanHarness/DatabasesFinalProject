from JsonParser.ParsedJson import loadJson
from TreeStructure.CreateTree import JsonTree
import math

class QuickJedi:
    def __init__(self):
        e_row_minima = []
        e_col_minima = []

    def quickJedi(self, t1: JsonTree, t2: JsonTree):
        subproblemCounter = 0 
        numSkips = 0
        numMatchings = 0 
        numEditSkips = 0 
        numEdits = 0

        t1InputSize = t1.size
        t2InputSize = t2.size
        largerSize = max(t1InputSize, t2InputSize)

        dt = [[math.inf]*(t2InputSize+1) for _ in range(t1InputSize+1)]
        df = [[math.inf]*(t2InputSize+1) for _ in range(t1InputSize+1)]
        e = [[math.inf]*(t2InputSize+1) for _ in range(t1InputSize+1)]

        hungarianCM = [[0.0]*(2*largerSize) for _ in range(2*largerSize)]

        self.e_row_minima = [0.0]*(2*largerSize)
        self.e_col_minima = [0.0]*(2*largerSize)

        dt[0][0] = 0.0
        df[0][0] = 0.0

        #TODO: Fix this
        for i in range(1, t1InputSize+1):
            df[i][0] = 0.0
            prevIChild = JsonTree.findIthChild(i-1, t1.root)
            for k in range(1, len(prevIChild.children)+1):

                df[i][0] += dt[prevIChild.offset][prevIChild.children[k-1] + 1] = 0


        

def main():
    js1 = loadJson("./QuickJedi/testFile1.txt")
    js2 = loadJson("./QuickJedi/testFile2.txt")

    t1 = JsonTree(js1)
    t2 = JsonTree(js2)

    quickJedi(t1, t2)


if __name__ == "__main__":
    main()