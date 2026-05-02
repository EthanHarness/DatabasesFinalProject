from TreeStructure.CreateTree import JsonTree
from TreeStructure.CreateTree import NodeType
import math

class BaselineJEDI:

    def compare(self, t1, t2):

        self.t1 = t1
        self.t2 = t2

        '''
        This is kind of wasteful to store the entire postorder traversal, it should store only what's
        nessary per iteration doing a nested DFS.

        I mainly did this because its simpler to get total number of nodes in the tree 
        without modifying the parser as well simplifies the algorithm implentation
        '''

        self.t1_traversal_list = self.postorder(self.t1.root)
        self.t2_traversal_list = self.postorder(self.t2.root)


        '''
        Storing the number of nodes isn't nessary anymore if I use a hashmap data structure
        '''
        self.n1 = len(self.t1_traversal_list)
        self.n2 = len(self.t2_traversal_list)

        ## Check for empty/malformed trees
        ## If either tree has no nodes dist is the cost to insert/delete all nodes from the other tree
        #if not self.t1_traversal_list and not self.t2_traversal_list:
        #    return 0
        #
        #if not self.t1_traversal_list:
        #    return sum(self.insert_cost(w) for w in self.t2_traversal_list)
        #
        #if not self.t2_traversal_list:
        #    return sum(self.delete_cost(v) for v in self.t1_traversal_list)
        
        #Creates two hashmaps that maps pair of verties to cost values 
        #Suppose to repserent two matrixs of dimension (n1 + 1) x (n2 + 1) with M[0][0] = 0
        dt, df = self.init_data_structures()

        #intilizes first row and first column of data structures (Empty tree cases)
        self.init_base_cases(df, dt)

        for i1,v in enumerate(self.t1_traversal_list):
            #print(f"{i1}/{len(self.t1_traversal_list)}")
            for w in self.t2_traversal_list:
                insF = self.compute_insF(df, v, w)
                insT = self.compute_insT(dt, v, w)

                delF = self.compute_delF(df, v, w)
                delT = self.compute_delT(dt, v, w)

                renF = 0
                if v.type == w.type == NodeType.ARRAY:
                    renF = self.SED(dt, v, w)
                else:
                    renF = self.BPM(dt, v, w)

                df[(v, w)] = min(insF, delF, renF)
                renT = df[(v, w)] + self.rename_cost(v, w)
                dt[(v, w)] = min(insT, delT, renT)

        return dt[(self.t1.root, self.t2.root)]


    '''
    I was intially going to use matrixes but if you only have a mapping from indexes to vertices
    aka an array, where the index referes to the DFS postion of some node, then it's
    hard to determine an aribtary node DFS postion (you need the DFS position a nodes children) 
    without scanning the list and checking the index and that's not ideal.
    '''
    def init_data_structures(self):
        dt = {(0, 0): 0}
        df = {(0, 0): 0}

        return dt, df
    
    def init_base_cases(self, df, dt):
        for v in self.t1_traversal_list:
            sum = 0

            for c in v.children:
                sum += dt[(c, 0)]

            df[(v, 0)] = sum
            dt[(v, 0)] = df[(v, 0)]+ self.delete_cost(v)

        for w in self.t2_traversal_list:
            sum = 0

            for c in w.children:
                sum += dt[(0, c)]

            df[(0, w)] = sum
            dt[(0, w)] = df[(0, w)] + self.insert_cost(w)

    def compute_insF(self, df, v, w):
        min = math.inf

        for c in w.children:
            temp = df[(v, c)] - df[(0, c)]

            if (temp < min):
                min = temp
        
        return df[(0, w)] + min

    def compute_insT(self, dt, v, w):
        min = math.inf

        for c in w.children:
            temp = dt[(v, c)] - dt[(0, c)]

            if (temp < min):
                min = temp
        
        return dt[(0, w)] + min

    def compute_delF(self, df, v, w):
        min = math.inf

        for c in v.children:
            temp = df[(c, w)] - df[(c, 0)]

            if (temp < min):
                min = temp
        
        return df[(v, 0)] + min

    def compute_delT(self, dt, v, w):
        min = math.inf

        for c in v.children:
            temp = dt[(c, w)] - dt[(c, 0)]

            if (temp < min):
                min = temp
        
        return dt[(v, 0)] + min
    
    def SED(self, dt, v, w):
        left = v.children
        right = w.children

        n = len(left)
        m = len(right)

        dp = [[0 for _ in range(m + 1)] for _ in range(n + 1)]

        # Delete remaining left child subtrees
        for i in range(1, n + 1):
            dp[i][0] = dp[i - 1][0] + dt[(left[i - 1], 0)]

        # Insert remaining right child subtrees
        for j in range(1, m + 1):
            dp[0][j] = dp[0][j - 1] + dt[(0, right[j - 1])]

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                delete_left = dp[i - 1][j] + dt[(left[i - 1], 0)]
                insert_right = dp[i][j - 1] + dt[(0, right[j - 1])]
                match_pair = dp[i - 1][j - 1] + dt[(left[i - 1], right[j - 1])]

                dp[i][j] = min(delete_left, insert_right, match_pair)

        return dp[n][m]

        ## My shot at SED, virtually the same idea, taken straignt from my code so the
        ## variables don't match up here but just added here for comparison
        ## SED for arrays (ordered children)
        #def SED(v, w, dt_matrix, node_to_idx):
        #    cv, cw = v.children, w.children # Get children
        #    m, n = len(cv), len(cw)
        #
        #    # Edit distance DP
        #    dp = [[0]*(n+1) for _ in range(m+1)]
        #
        #    for i in range(m+1):
        #        dp[i][0] = i   # Delete all
        #
        #    for j in range(n+1):
        #        dp[0][j] = j   # Insert all
        #
        #    for i in range(1, m+1):
        #        for j in range(1, n+1):
        #            vi = node_to_idx[id(cv[i-1])]
        #            wj = node_to_idx[id(cw[j-1])]
        #            dp[i][j] = min(
        #                    dp[i-1][j]+1,   # Delete
        #                    dp[i][j-1]+1,   # Insert
        #                    dp[i-1][j-1]+dt_matrix[(vi,wj)] # Match or substitute
        #                    )
        #    return dp[m][n]


    def BPM(self, dt, v, w):
        left_children = v.children
        right_children = w.children
        n, m = len(left_children), len(right_children)

        if n == 0: return sum(dt[(0, c)] for c in right_children)
        if m == 0: return sum(dt[(c, 0)] for c in left_children)

        # 1. Build the Cost Matrix (size (n+m) x (n+m))
        # Top-left: Match v_i with w_j
        # Top-right: Delete v_i (Diagonal = delete_cost, others = inf)
        # Bottom-left: Insert w_j (Diagonal = insert_cost, others = inf)
        # Bottom-right: Dummy zeros
        size = n + m
        inf = float('inf')
        matrix = [[0 for _ in range(size)] for _ in range(size)]

        for i in range(size):
            for j in range(size):
                if i < n and j < m:
                    matrix[i][j] = dt[(left_children[i], right_children[j])]
                elif i < n and j >= m:
                    matrix[i][j] = dt[(left_children[i], 0)] if (j - m) == i else inf
                elif i >= n and j < m:
                    matrix[i][j] = dt[(0, right_children[j])] if (i - n) == j else inf
                else:
                    matrix[i][j] = 0

        return self._min_cost_assignment(matrix)

    def _min_cost_assignment(self, matrix):
        """Pure Python Hungarian Algorithm (O(N^3))"""
        n = len(matrix)
        u, v = [0] * (n + 1), [0] * (n + 1)
        p, way = [0] * (n + 1), [0] * (n + 1)

        for i in range(1, n + 1):
            p[0] = i
            j0 = 0
            minv = [float('inf')] * (n + 1)
            used = [False] * (n + 1)
            
            while True:
                used[j0] = True
                i0, j1, delta = p[j0], 0, float('inf')
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

    def postorder(self, root):
        out = []

        def dfs(node):
            for child in node.children:
                dfs(child)
            
            out.append(node)

        dfs(root)
        return out

    def delete_cost(self, v):
        return 1

    def insert_cost(self, w):
        return 1

    def rename_cost(self, v, w):
        if v.type != w.type:
            return 2   # delete v + insert w
        
        return 0 if v.label == w.label else 1