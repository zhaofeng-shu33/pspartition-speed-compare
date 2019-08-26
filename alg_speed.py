# for time comparison experiment, it can not be reproduced exactly because of different computing machines
# but we hope the general tendency can be reproduced.
import os
import time
from datetime import datetime
import argparse
import random
import json
import logging
import networkx as nx
from sklearn import datasets
from sklearn.metrics.pairwise import pairwise_kernels

from info_cluster import InfoCluster
TOLERANCE = 1e-10
GAUSSIAN_NODE_LIST = [100, 200, 300, 400, 500]
METHOD_LIST = ['dt', 'pdt', 'psp_i', 'pdt_r']
time_str = datetime.now().strftime('%Y-%m-%d-')
LOGGING_FILE = time_str + 'speed.log'
logging.basicConfig(filename=os.path.join('build', LOGGING_FILE), level=logging.INFO, format='%(asctime)s %(message)s')

def construct(scale = 4):
    n = scale * scale
    k1 = scale # inner
    k2 = scale # outer
    z_in_1 = n - 2
    z_in_2 = k1 - 1
    z_out = 1
    p_1 = z_in_1/(n-1)    
    p_2 = z_in_2/(n*(k1-1))
    p_o = z_out/(n*k1*(k2-1))
    G = nx.Graph()
    cnt = 0
    for t in range(k2):
        for i in range(k1):
            for j in range(n):
                G.add_node(cnt, macro=t, micro=i)
                cnt += 1
    for i in G.nodes(data=True):
        for j in G.nodes(data=True):
            if(j[0] <= i[0]):
                continue
            if(i[1]['macro'] != j[1]['macro']):
                if(random.random()<=p_o):
                    G.add_edge(i[0], j[0])
            else:
                if(i[1]['micro'] == j[1]['micro']):
                    if(random.random() <= p_1):
                        G.add_edge(i[0], j[0])
                else:
                    if(random.random() <= p_2):
                        G.add_edge(i[0], j[0])
    return G 
    
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

def generate_and_run_gaussian(num_times):
    gaussian_dic = {}
    for i in GAUSSIAN_NODE_LIST:
        dg = generate_gaussian(i)
        prop = {'num_edge': len(dg.edges)}
        for method in METHOD_LIST:
            prop[method] = algorithm_runner(method, dg, num_times)
        gaussian_dic[i] = prop
    write_json(gaussian_dic, 'gaussian')

def write_json(python_dic, filename_prefix):    
    file_name_path = os.path.join('build', time_str + filename_prefix + '.json')
    with open(file_name_path, 'w') as f:
        st = json.dumps(python_dic, indent=4) # human readable
        f.write(st)
        
def algorithm_runner(method_name, digraph, average_times = 1):
    '''
        return the time used 
    '''
    ic = InfoCluster(affinity='precomputed')
        
    total_times = 0
    for i in range(average_times):
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
        running_time = end_time - start_time
        logging.info('%s, %d/%d, running time: %f'.format(method_name, i, average_times, running_time))        
        total_times += running_time
        
    return total_times/average_times    
    
if __name__ == '__main__':
    method_list = ['all'] + METHOD_LIST
    task_list = ['try', 'gaussian']
    parser = argparse.ArgumentParser()
    parser.add_argument('--node_size', type=int, default=100)
    parser.add_argument('--method', default='all', choices=method_list, nargs='+')
    parser.add_argument('--task', default='try', choices=task_list)
    parser.add_argument('--num_times', type=int, default=1)
    args = parser.parse_args()
    if(args.node_size < 4):
        print('size should be at least 4')
        exit(0)
    if(args.task == 'try'):
        dg = generate_gaussian(args.node_size)
        if(args.method.count('all') >= 0):
            method_inner_list = METHOD_LIST
        elif(type(args.method) is list):
            method_inner_list = args.method
        else:
            method_inner_list = [args.method]
        print('num of edge', len(dg.edges))
        for method in method_inner_list:
            time_used = algorithm_runner(method, dg, args.num_times)
            print(method, time_used)
    elif(args.task == 'gaussian'):
        generate_and_run_gaussian(args.num_times)
       
        