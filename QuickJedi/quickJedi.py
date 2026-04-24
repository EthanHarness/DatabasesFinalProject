import numpy as np
from JsonParser.ParsedJson import loadJson
from TreeStructure.CreateTree import JsonTree, NodeType


class QuickJEDI:
    def __init__(self, cost_del=1.0, cost_ins=1.0, cost_ren=1.0):
        self.c_del = cost_del
        self.c_ins = cost_ins
        self.c_ren = cost_ren

    def compare(self, tree1, tree2):
        t1, t2 = tree1.jedi_data, tree2.jedi_data
        n, m = t1["size"], t2["size"]

        size1 = t1["subtree_sizes"]
        size2 = t2["subtree_sizes"]

        dt = np.zeros((n + 1, m + 1))

        # --- Aggregate initialization ---
        for i in range(1, n + 1):
            dt[i, 0] = self.c_del * size1[i - 1]

        for j in range(1, m + 1):
            dt[0, j] = self.c_ins * size2[j - 1]

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                type1, type2 = t1["types"][i - 1], t2["types"][j - 1]
                label1, label2 = t1["labels"][i - 1], t2["labels"][j - 1]

                # --- LOWER BOUND ---
                lb_size = abs(size1[i - 1] - size2[j - 1]) * min(self.c_del, self.c_ins)
                lb_type = 0 if type1 == type2 else (self.c_del + self.c_ins)
                lower_bound = lb_size + lb_type

                best = float("inf")

                # --- PATH A: MATCH / RENAME ---
                if lower_bound < best:
                    if type1 != type2:
                        node_op_cost = self.c_del + self.c_ins
                    elif label1 != label2:
                        node_op_cost = self.c_ren
                    else:
                        node_op_cost = 0.0

                    if type1 == NodeType.ARRAY and type2 == NodeType.ARRAY:
                        f_dist = self._sed_array(t1, t2, i - 1, j - 1, dt, size1, size2)
                    else:
                        f_dist = self._min_weight_matching(
                            t1["children"][i - 1],
                            t2["children"][j - 1],
                            dt,
                            size1,
                            size2,
                        )

                    best = node_op_cost + f_dist

                # --- PATH B: DELETE ---
                lb_del = self.c_del + lb_size  # cheap refinement
                if lb_del < best:
                    res_del = self.c_del + self._match_single_to_forest(
                        j - 1,
                        t1["children"][i - 1],
                        dt,
                        single_is_t1=False,
                        size1=size1,
                        size2=size2,
                    )
                    best = min(best, res_del)

                # --- PATH C: INSERT ---
                lb_ins = self.c_ins + lb_size
                if lb_ins < best:
                    res_ins = self.c_ins + self._match_single_to_forest(
                        i - 1,
                        t2["children"][j - 1],
                        dt,
                        single_is_t1=True,
                        size1=size1,
                        size2=size2,
                    )
                    best = min(best, res_ins)

                dt[i, j] = best

        return dt[n, m]

    def _match_single_to_forest(self, s_idx, f_indices, dt, single_is_t1, size1, size2):
        if not f_indices:
            return dt[s_idx + 1, 0] if single_is_t1 else dt[0, s_idx + 1]

        if single_is_t1:
            total_f_cost = sum(self.c_ins * size2[idx] for idx in f_indices)
        else:
            total_f_cost = sum(self.c_del * size1[idx] for idx in f_indices)

        best_cost = float("inf")

        for f_idx in f_indices:
            if single_is_t1:
                current = (
                    dt[s_idx + 1, f_idx + 1]
                    + (total_f_cost - self.c_ins * size2[f_idx])
                )
            else:
                current = (
                    dt[f_idx + 1, s_idx + 1]
                    + (total_f_cost - self.c_del * size1[f_idx])
                )

            best_cost = min(best_cost, current)

        return best_cost

    def _min_weight_matching(self, c1, c2, dt, size1, size2):
        if not c1:
            return sum(self.c_ins * size2[idx] for idx in c2)

        if not c2:
            return sum(self.c_del * size1[idx] for idx in c1)

        costs = np.array(
            [[dt[idx1 + 1, idx2 + 1] for idx2 in c2] for idx1 in c1]
        )

        matched_cost = 0.0
        used_r, used_c = set(), set()

        flat_indices = np.argsort(costs, axis=None)

        for idx in flat_indices:
            r, c = divmod(idx, costs.shape[1])
            if r not in used_r and c not in used_c:
                matched_cost += costs[r, c]
                used_r.add(r)
                used_c.add(c)

        # unmatched → aggregate delete/insert
        for r in range(len(c1)):
            if r not in used_r:
                matched_cost += self.c_del * size1[c1[r]]

        for c in range(len(c2)):
            if c not in used_c:
                matched_cost += self.c_ins * size2[c2[c]]

        return matched_cost

    def _sed_array(self, t1, t2, i, j, dt, size1, size2):
        c1, c2 = t1["children"][i], t2["children"][j]
        n, m = len(c1), len(c2)

        dp = np.zeros((n + 1, m + 1))

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
    import time
    start = time.perf_counter()
    main()
    end = time.perf_counter()
    print(end - start)