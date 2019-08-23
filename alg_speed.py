import time
import argparse
import networkx as nx
from sklearn import datasets
from sklearn.metrics.pairwise import pairwise_kernels

from info_cluster import InfoCluster
TOLERANCE = 1e-10

def generate_gaussian(num_node):
    '''
        returns: networkx.DiGraph
    '''
    pos_list, _ = datasets.make_blobs(n_samples = num_node, centers=[[3,3],[-3,-3],[3,-3],[-3,3]], cluster_std=1)
    affinity_matrix = pairwise_kernels(pos_list, metric='rbf', gamma = 0.6)
    ms = affinity_matrix.shape[0]
    digraph = nx.DiGraph()
    for i in range(ms):
        for j in range(i+1, ms):
            w = affinity_matrix[i,j]
            if(w > TOLERANCE):
                digraph.add_edge(i,j,weight=w)
    return digraph

def algorithm_runner(method_name, digraph):
    '''
        return the time used 
    '''
    ic = InfoCluster(affinity='precomputed')
        
    
    if(method_name == 'dt'):
        start_time = time.time()    
        ic.fit(digraph)
    elif(method_name == 'pdt'):
        start_time = time.time()        
        ic.fit(digraph, use_pdt=True)
    elif(method_name == 'pdt_r'):
        start_time = time.time()        
        ic.fit(digraph, use_pdt_r=True)
    else:
        start_time = time.time()        
        ic.fit(digraph, use_psp_i=True)
        
    end_time = time.time()
    return end_time - start_time
    
if __name__ == '__main__':
    method_list = ['all', 'dt', 'pdt', 'psp_i', 'pdt_r']
    parser = argparse.ArgumentParser()
    parser.add_argument('--node_size', type=int, default=100)
    parser.add_argument('--method', default='all', choices=method_list, nargs='+')
    args = parser.parse_args()
    if(args.node_size < 4):
        print('size should be at least 4')
        exit(0)
    dg = generate_gaussian(args.node_size)
    if(args.method.count('all') >= 0):
        method_inner_list = ['dt', 'pdt', 'psp_i', 'pdt_r']
    elif(type(args.method) is list):
        method_inner_list = args.method
    else:
        method_inner_list = [args.method]
    print('num of edge', len(dg.edges))
    for method in method_inner_list:
        time_used = algorithm_runner(method, dg)
        print(method, time_used)
        