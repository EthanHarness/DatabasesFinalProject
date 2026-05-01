from JsonParser.ParsedJson import loadJson
from TreeStructure.CreateTree import JsonTree

from QuickJedi.jediBaseline import BaselineJEDI
from QuickJedi.quickJedi import QuickJEDI
import time

def main():
    js1 = loadJson("./ComparisonTests/jsonFile1.txt")
    js2 = loadJson("./ComparisonTests/jsonFile2.txt")

    t1 = JsonTree(js1)
    t2 = JsonTree(js2)

    bs = BaselineJEDI()
    qj = QuickJEDI()

    qjStart = time.perf_counter()
    qjDist = qj.compare(t1, t2)
    qjEnd = time.perf_counter()
    
    print(f"Quick JEDI Algorithm (runnint time, difference): ({qjEnd-qjStart}, {qjDist})")


    bsStart = time.perf_counter()
    bsDist = bs.compare(t1, t2)
    bsEnd = time.perf_counter()

    print(f"JEDI Base Algorithm (runnint time, difference): ({bsEnd-bsStart}, {bsDist})")


if __name__ == "__main__":
    main()