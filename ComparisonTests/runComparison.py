from JsonParser.ParsedJson import loadJson
from TreeStructure.CreateTree import JsonTree
from QuickJEDI.QuickJEDI import QuickJEDI
from QuickJEDI.JEDIBaseOld import JEDIBase
from QuickJEDI.JediModified import JediDistance
import time

def main():
    js1 = loadJson("./ComparisonTests/jsonFile1.txt")
    js2 = loadJson("./ComparisonTests/jsonFile2.txt")

    t1 = JsonTree(js1)
    t2 = JsonTree(js2)

    qj = QuickJEDI()
    bs = JEDIBase()
    bsNew = JediDistance(t1, t2)

    bsStart = time.perf_counter()
    bsDist = bsNew.jedi_baseline()
    bsEnd = time.perf_counter()

    qjStart = time.perf_counter()
    qjDist = qj.compare(t1, t2)
    qjEnd = time.perf_counter()

    print(f"JEDI Base Algorithm (runnint time, difference): ({bsEnd-bsStart}, {bsDist})")
    print(f"Quick JEDI Algorithm (runnint time, difference): ({qjEnd-qjStart}, {qjDist})")


if __name__ == "__main__":
    main()