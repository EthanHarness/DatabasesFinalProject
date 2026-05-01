import numpy as np
from TreeStructure.CreateTree import NodeType

class QuickJEDI:
    def __init__(self, cost_del=1, cost_ins=1, cost_ren=1):
        self.c_del = int(cost_del)
        self.c_ins = int(cost_ins)
        self.c_ren = int(cost_ren)
        self.min_unit_cost = min(self.c_del, self.c_ins)

    def compare(self, tree1, tree2):
        t1, t2 = tree1.jedi_data, tree2.jedi_data
        n, m = t1["size"], t2["size"]

        size1 = t1["subtree_sizes"]
        size2 = t2["subtree_sizes"]
        
        # Use a large integer for infinity
        INF = 10**9
        dt = np.zeros((n + 1, m + 1), dtype=int)

        # Base case initialization
        for i in range(1, n + 1):
            dt[i, 0] = self.c_del * size1[i - 1]
        for j in range(1, m + 1):
            dt[0, j] = self.c_ins * size2[j - 1]

        for i in range(1, n + 1):
            s1 = size1[i - 1]
            for j in range(1, m + 1):
                s2 = size2[j - 1]
                
                type1, type2 = t1["types"][i - 1], t2["types"][j - 1]
                label1, label2 = t1["labels"][i - 1], t2["labels"][j - 1]

                # --- Optimization: Global Lower Bound ---
                # The absolute minimum cost to transform T1 to T2 is the size difference
                lb_size = abs(s1 - s2) * self.min_unit_cost
                
                # We start with the cheapest 'skip' cases to set a competitive 'best'
                # usually it's faster to check these before Hungarian
                best = INF

                # 1. PATH B: DELETE (Delete T1 root, match its children to T2)
                # Quick check: can this path even theoretically beat INF?
                if self.c_del + lb_size < best:
                    res_del = self.c_del + self._match_single_to_forest(
                        j - 1, t1["children"][i - 1], dt, False, size1, size2
                    )
                    best = min(best, res_del)

                # 2. PATH C: INSERT (Insert T2 root, match T1 to its children)
                if self.c_ins + lb_size < best:
                    res_ins = self.c_ins + self._match_single_to_forest(
                        i - 1, t2["children"][j - 1], dt, True, size1, size2
                    )
                    best = min(best, res_ins)

                # 3. PATH A: MATCH / RENAME
                # Only run the expensive Forest Matching if the lower bound allows it
                lb_type = 0 if type1 == type2 else (self.c_del + self.c_ins)
                if lb_size + lb_type < best:
                    if type1 != type2:
                        node_op_cost = self.c_del + self.c_ins
                    else:
                        node_op_cost = self.c_ren if label1 != label2 else 0
                    
                    # Forest Matching
                    if type1 == NodeType.ARRAY and type2 == NodeType.ARRAY:
                        f_dist = self._sed_array(t1, t2, i - 1, j - 1, dt, size1, size2)
                    else:
                        # Before running Hungarian, check if node_op_cost alone 
                        # already breaks the bank.
                        if node_op_cost + lb_size < best:
                            f_dist = self._optimal_matching(
                                t1["children"][i - 1], t2["children"][j - 1],
                                dt, size1, size2, best - node_op_cost
                            )
                        else:
                            f_dist = INF
                    
                    best = min(best, node_op_cost + f_dist)

                dt[i, j] = best

        return int(dt[n, m])

    def _match_single_to_forest(self, s_idx, f_indices, dt, single_is_t1, size1, size2):
        if not f_indices:
            return dt[s_idx + 1, 0] if single_is_t1 else dt[0, s_idx + 1]

        # Optimization: Pre-calculate the cost of inserting/deleting the whole forest
        if single_is_t1:
            total_f_cost = sum(self.c_ins * size2[idx] for idx in f_indices)
        else:
            total_f_cost = sum(self.c_del * size1[idx] for idx in f_indices)

        best_cost = 10**9
        for f_idx in f_indices:
            if single_is_t1:
                current = dt[s_idx + 1, f_idx + 1] + (total_f_cost - self.c_ins * size2[f_idx])
            else:
                current = dt[f_idx + 1, s_idx + 1] + (total_f_cost - self.c_del * size1[f_idx])
            if current < best_cost:
                best_cost = current
        return best_cost

    def _optimal_matching(self, c1, c2, dt, size1, size2, limit):
        n, m = len(c1), len(c2)
        if n == 0: return sum(self.c_ins * size2[idx] for idx in c2)
        if m == 0: return sum(self.c_del * size1[idx] for idx in c1)

        # Forest-level Lower Bound: Sum of size differences of children
        # This is an extra optimization to avoid building the matrix
        # (Though simple, it can prune many obviously different objects)
        
        size = n + m
        matrix = [[0] * size for _ in range(size)]
        INF = 10**9

        for i in range(size):
            for j in range(size):
                if i < n and j < m:
                    matrix[i][j] = dt[c1[i] + 1, c2[j] + 1]
                elif i < n and j >= m:
                    matrix[i][j] = (self.c_del * size1[c1[i]]) if (j - m) == i else INF
                elif i >= n and j < m:
                    matrix[i][j] = (self.c_ins * size2[c2[j]]) if (i - n) == j else INF
                else:
                    matrix[i][j] = 0

        return self._hungarian(matrix)

    def _hungarian(self, matrix):
        # Implementation remains the same as previous (Optimal solver)
        n = len(matrix)
        u, v = [0] * (n + 1), [0] * (n + 1)
        p, way = [0] * (n + 1), [0] * (n + 1)
        for i in range(1, n + 1):
            p[0] = i
            j0 = 0
            minv = [10**9] * (n + 1)
            used = [False] * (n + 1)
            while True:
                used[j0] = True
                i0, j1, delta = p[j0], 0, 10**9
                for j in range(1, n + 1):
                    if not used[j]:
                        cur = matrix[i0 - 1][j - 1] - u[i0] - v[j]
                        if cur < minv[j]:
                            minv[j], way[j] = cur, j0
                        if minv[j] < delta:
                            delta, j1 = minv[j], j
                for j in range(n + 1):
                    if used[j]:
                        u[p[j]] += delta
                        v[j] -= delta
                    else:
                        minv[j] -= delta
                j0 = j1
                if p[j0] == 0: break
            while True:
                j1 = way[j0]
                p[j0] = p[j1]
                j0 = j1
                if j0 == 0: break
        return -v[0]

    def _sed_array(self, t1, t2, i, j, dt, size1, size2):
        c1, c2 = t1["children"][i], t2["children"][j]
        n, m = len(c1), len(c2)
        dp = np.zeros((n + 1, m + 1), dtype=int)
        for s in range(1, n + 1):
            dp[s, 0] = dp[s - 1, 0] + self.c_del * size1[c1[s - 1]]
        for t in range(1, m + 1):
            dp[0, t] = dp[0, t - 1] + self.c_ins * size2[c2[t - 1]]
        for s in range(1, n + 1):
            for t in range(1, m + 1):
                dp[s, t] = min(
                    dp[s - 1, t] + self.c_del * size1[c1[s - 1]],
                    dp[s, t - 1] + self.c_ins * size2[c2[t - 1]],
                    dp[s - 1, t - 1] + dt[c1[s - 1] + 1, c2[t - 1] + 1],
                )
        return int(dp[n, m])