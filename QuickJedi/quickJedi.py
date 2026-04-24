import numpy as np
from JsonParser.ParsedJson import loadJson
from TreeStructure.CreateTree import JsonTree, NodeType
import math

"""    def compare(self, tree1: JsonTree, tree2: JsonTree):
        t1 = tree1.jedi_data
        t2 = tree2.jedi_data

        print("TREE 1")
        for key,value in tree1.jedi_data.items():
            print(f"{key}:{value}")
        print("\nTREE 2")
        for key,value in tree2.jedi_data.items():
            print(f"{key}:{value}")
        print("\n")

        n, m = t1["size"], t2["size"]
        
        dt = np.full((n + 1, m + 1), float('inf'))
        df = np.full((n + 1, m + 1), float('inf'))
        
        dt[0, 0] = 0.0
        df[0, 0] = 0.0

        # Init: Deletion costs
        for i in range(1, n + 1):
            df[i, 0] = sum(dt[c + 1, 0] for c in t1["children"][i-1])
            dt[i, 0] = df[i, 0] + self.cost_del

        # Init: Insertion costs
        for j in range(1, m + 1):
            df[0, j] = sum(dt[0, c + 1] for c in t2["children"][j-1])
            dt[0, j] = df[0, j] + self.cost_ins

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                # 1. Forest Distances (The children matching)
                type1, type2 = t1["types"][i-1], t2["types"][j-1]
                
                # Forest deletion/insertion
                min_for_del = min([df[i, c_idx+1] - df[0, c_idx+1] for c_idx in t2["children"][j-1]] + [float('inf')])
                min_for_del += df[0, j]

                min_for_ins = min([df[c_idx+1, j] - df[c_idx+1, 0] for c_idx in t1["children"][i-1]] + [float('inf')])
                min_for_ins += df[i, 0]

                # Forest Rename (Structural Match)
                ub = min(min_for_del, min_for_ins)
                
                # JEDI Core: Match children based on node type
                if not t1["children"][i-1] and not t2["children"][j-1]:
                    min_for_ren = 0.0
                elif type1 == NodeType.KEY and type2 == NodeType.KEY:
                    # KEY nodes always have exactly one child in your structure
                    min_for_ren = dt[t1["children"][i-1][0] + 1, t2["children"][j-1][0] + 1]
                elif type1 == NodeType.ARRAY and type2 == NodeType.ARRAY:
                    min_for_ren = self._sed_array(t1, t2, i-1, j-1, dt)
                elif type1 == NodeType.OBJECT and type2 == NodeType.OBJECT:
                    min_for_ren = self._greedy_matching(t1, t2, i-1, j-1, dt)
                else:
                    min_for_ren = ub

                df[i, j] = min(ub, min_for_ren)

                # 2. Tree Distance (Node Rename + Forest Match)
                # Labels match if both are None or both are equal strings
                label_match = (t1["labels"][i-1] == t2["labels"][j-1])
                cost_ren = 0.0 if (type1 == type2 and label_match) else 1.0
                
                min_tree_ren = df[i, j] + cost_ren
                
                # Tree deletion/insertion
                min_tree_del = min([dt[i, c_idx+1] - dt[0, c_idx+1] for c_idx in t2["children"][j-1]] + [float('inf')])
                min_tree_del += dt[0, j]

                min_tree_ins = min([dt[c_idx+1, j] - dt[c_idx+1, 0] for c_idx in t1["children"][i-1]] + [float('inf')])
                min_tree_ins += dt[i, 0]

                dt[i, j] = min(min_tree_del, min_tree_ins, min_tree_ren)

        print("DT Printout")
        for index, row in enumerate(dt):
            print(f"{index}: {row}")
        
        print("\n")
        print(df)

        return dt[n, m]"""

import numpy as np

class QuickJEDI:
    def __init__(self, cost_del=1.0, cost_ins=1.0, cost_ren=1.0):
        self.c_del = cost_del
        self.c_ins = cost_ins
        self.c_ren = cost_ren

    def compare(self, tree1, tree2):
        t1, t2 = tree1.jedi_data, tree2.jedi_data
        n, m = t1["size"], t2["size"]

        print("TREE 1")
        for key,value in tree1.jedi_data.items():
            print(f"{key}:{value}")
        print("\nTREE 2")
        for key,value in tree2.jedi_data.items():
            print(f"{key}:{value}")
        print("\n")

        
        # dt[i, j] stores the distance between subtree i (Tree 1) and subtree j (Tree 2)
        dt = np.zeros((n + 1, m + 1))

        # 1. Initialize Deletion and Insertion costs for full subtrees
        for i in range(1, n + 1):
            dt[i, 0] = self.c_del + sum(dt[c + 1, 0] for c in t1["children"][i-1])
        for j in range(1, m + 1):
            dt[0, j] = self.c_ins + sum(dt[0, c + 1] for c in t2["children"][j-1])

        # 2. Fill DP Table
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                type1, type2 = t1["types"][i-1], t2["types"][j-1]
                label1, label2 = t1["labels"][i-1], t2["labels"][j-1]

                # --- Path A: Direct Match / Rename ---
                # Per your requirement: Mismatched types = Delete + Insert
                if type1 != type2:
                    node_op_cost = self.c_del + self.c_ins
                elif label1 != label2:
                    node_op_cost = self.c_ren
                else:
                    node_op_cost = 0.0

                # Forest distance (matching the children)
                if type1 == NodeType.ARRAY and type2 == NodeType.ARRAY:
                    f_dist = self._sed_array(t1, t2, i-1, j-1, dt)
                else:
                    f_dist = self._min_weight_matching(t1["children"][i-1], t2["children"][j-1], dt)
                
                res_match = node_op_cost + f_dist

                # --- Path B: Delete current T1 node, match children to T2 subtree ---
                res_del = self.c_del + self._match_single_to_forest(j-1, t1["children"][i-1], dt, single_is_t1=False)
                
                # --- Path C: Insert current T2 node, match T1 subtree to children ---
                res_ins = self.c_ins + self._match_single_to_forest(i-1, t2["children"][j-1], dt, single_is_t1=True)

                dt[i, j] = min(res_match, res_del, res_ins)

        print("DT Printout")
        for index, row in enumerate(dt):
            print(f"{index}: {row}")
            
        return dt[n, m]

    def _match_single_to_forest(self, s_idx, f_indices, dt, single_is_t1):
        """
        Matches a single subtree (s_idx) against a forest (f_indices).
        Logic: Pick the best child to match the subtree, and delete/insert the rest.
        """
        if not f_indices:
            return dt[s_idx + 1, 0] if single_is_t1 else dt[0, s_idx + 1]
        
        # Cost to delete/insert the entire forest
        if single_is_t1: # Forest is in Tree 2 (Insertion)
            total_f_cost = sum(dt[0, idx + 1] for idx in f_indices)
        else: # Forest is in Tree 1 (Deletion)
            total_f_cost = sum(dt[idx + 1, 0] for idx in f_indices)
        
        best_cost = float('inf')
        for f_idx in f_indices:
            if single_is_t1:
                # Match T1(s_idx) to T2(f_idx), insert other T2 children
                current = dt[s_idx + 1, f_idx + 1] + (total_f_cost - dt[0, f_idx + 1])
            else:
                # Match T1(f_idx) to T2(s_idx), delete other T1 children
                current = dt[f_idx + 1, s_idx + 1] + (total_f_cost - dt[f_idx + 1, 0])
            best_cost = min(best_cost, current)
            
        return best_cost

    def _min_weight_matching(self, c1, c2, dt):
        if not c1: return sum(dt[0, idx + 1] for idx in c2)
        if not c2: return sum(dt[idx + 1, 0] for idx in c1)

        costs = np.array([[dt[idx1 + 1, idx2 + 1] for idx2 in c2] for idx1 in c1])
        matched_cost = 0.0
        used_r, used_c = set(), set()
        flat_indices = np.argsort(costs, axis=None)
        
        for idx in flat_indices:
            r, c = divmod(idx, costs.shape[1])
            if r not in used_r and c not in used_c:
                matched_cost += costs[r, c]
                used_r.add(r)
                used_c.add(c)
        
        for r in range(len(c1)):
            if r not in used_r: matched_cost += dt[c1[r] + 1, 0]
        for c in range(len(c2)):
            if c not in used_c: matched_cost += dt[0, c2[c] + 1]
            
        return matched_cost

    def _sed_array(self, t1, t2, i, j, dt):
        c1, c2 = t1["children"][i], t2["children"][j]
        n, m = len(c1), len(c2)
        dp = np.zeros((n + 1, m + 1))
        for s in range(1, n+1): dp[s, 0] = dp[s-1, 0] + dt[c1[s-1]+1, 0]
        for t in range(1, m+1): dp[0, t] = dp[0, t-1] + dt[0, c2[t-1]+1]
        for s in range(1, n+1):
            for t in range(1, m+1):
                dp[s, t] = min(dp[s-1, t] + dt[c1[s-1]+1, 0],
                               dp[s, t-1] + dt[0, c2[t-1]+1],
                               dp[s-1, t-1] + dt[c1[s-1]+1, c2[t-1]+1])
        return dp[n, m]
        
def main():
    js1 = loadJson("./QuickJedi/testFile1.txt")
    js2 = loadJson("./QuickJedi/testFile2.txt")

    t1 = JsonTree(js1)
    t2 = JsonTree(js2)

    qj = QuickJEDI()

    editDistance = qj.compare(t1, t2)
    print(editDistance)


if __name__ == "__main__":
    main()