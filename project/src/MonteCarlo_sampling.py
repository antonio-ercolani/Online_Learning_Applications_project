import numpy as np

# Class that implements the MonteCarlo sampling estimation techiques that estimates the Item-Item influence graph through random walks
# prob_matrix : influence graph to be estimated by MC
class MC_sampling:
    
    def __init__(self, prob_matrix):
        self.prob_matrix = prob_matrix
        self.node_dim = prob_matrix.shape[0]
        self.Z = np.zeros(((self.node_dim), (self.node_dim)))
    
    # Method that returns a matrix containing activation probs of nodes given the seed (seed on rows, node on columns)
    # n_iter : number of iterations (walks) perfomed to obtain graph estimation
    def estimate_activ_prob(self, n_iter):
        seeds = np.arange(self.node_dim)
        #perform multiple iterations of MC
        for seed in seeds:
            for t in range(n_iter):
                #Random walk generating the live-edge graph according to prob_matrix
                live_edge_mask = np.zeros(shape=[self.node_dim, self.node_dim])
                already_actives = []
                last_actives = [seed]
                while last_actives:
                    for node in last_actives:
                        if node not in already_actives:
                            already_actives.append(node)
                    origin = int(last_actives.pop())
                    for dest in range(self.node_dim):
                        edge_activation = np.random.choice([0, 1], p=[1-self.prob_matrix[origin, dest], self.prob_matrix[origin, dest]])
                        if edge_activation > 0 and (dest not in already_actives):
                            live_edge_mask[origin, dest] = edge_activation
                            last_actives.append(dest)

                #get all active nodes of the previously generated live-edge graph
                active_nodes = self.depth_first_tree_search(live_edge_mask, seed, visited = set())
                for i in active_nodes:
                    self.Z[seed, i] +=1

        return self.Z / n_iter

    # Utility method
    def depth_first_tree_search(self, live_edge_graph, start, visited = set()):
        visited.add(start)
        activated = np.where(live_edge_graph[start] == 1)[0]
        for node in activated:
            if node not in visited:
                self.depth_first_tree_search(live_edge_graph, node, visited)

        return visited
