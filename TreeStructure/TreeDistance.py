from TreeStructure.CreateTree import JsonTree

class JediDistance:

    def __init__(self, t1, t2):
        self.t1 = t1
        self.t2 = t2

    def jedi_baseline(self):
        t1_traversal_list = self.postorder(self.t1.root)
        t2_traversal_list = self.postorder(self.t2.root)

        n1 = len(t1_traversal_list)
        n2 = len(t2_traversal_list)

        dt, df = self.init_data_structures(n1, n2)

        print(f"Tree 1 size: {n1}")
        print(f"Tree 2 size: {n2}")

        #I'm going to refer the index of a node by the order of its post order iteration
        for v in range(1, n1 + 1):
            sum = 0

            for c in t1_traversal_list[v].children:
                sum += dt[c][0]

            df[v][0] = sum
            dt[v][0] = df[v][0] + self.delete_cost()


        for w in range(1, n2 + 1):
            sum = 0

            for c in t2_traversal_list[w].children:
                sum += dt[0][c]

            df[0][w] = sum
            dt[0][w] = df[0][w] + self.insert_cost()


        
            






    def init_data_structures(self, n1, n2):
        dt = [[0 for _ in  range(n2 + 1)] for _ in  range(n1 + 1)]
        df = [[0 for _ in  range(n2 + 1)] for _ in  range(n1 + 1)]

        return dt, df
    

    def position_to_index(i):
        return i - 1    

    def SED(v, w):
        pass

    def BPM(v, w):
        pass

    def postorder(self, root):
        out = []

        def dfs(node):
            for child in node.children:
                dfs(child)
            out.append(node)

        dfs(root)
        return out

    def delete_cost(v):
        return 1

    def insert_cost(w):
        return 1

    def rename_cost(v, w):
        if v.type != w.type:
            return 2   # delete v + insert w
        
        return 0 if v.label == w.label else 1
