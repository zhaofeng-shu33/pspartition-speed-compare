import argparse
import networkx as nx
from sklearn import datasets
from sklearn.metrics.pairwise import pairwise_kernels

TOLERANCE = 1e-10

def generate_gaussian(num_node):
    '''
        returns: networkx.DiGraph
    '''
    pos_list, _ = datasets.make_blobs(n_samples = args.size, centers=[[3,3],[-3,-3],[3,-3],[-3,3]], cluster_std=1)
    affinity_matrix = pairwise_kernels(pos_list, metric='rbf', gamma = args.gamma)
    ms = affinity_matrix.shape[0]
    digraph = nx.DiGraph()
    for i in range(ms):
        for j in range(i+1, ms):
            w = affinity_matrix[i,j]
            if(w > TOLERANCE):
                digraph.add_edge(i,j,weight=w)
    return digraph
    
    