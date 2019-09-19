'''load pickle data to plot
'''
import os
from datetime import datetime
import json
import argparse
import random
import pdb

import matplotlib.pyplot as plt
color_list = ['red', 'green', 'blue', 'green']
marker_list = ['o', '+', 'x', 'o']
linestyle_list = ['-','-', '-', '--']
method_translate = {'pdt_r': 'Kolmogorov', 'dt': 'Narayanan', 'psp_i': 'ours', 'pdt': 'ours'}

def plot_gaussian_demo_data():
    color_list = ['#3FF711', 'r', 'g', 'm','y','k','c','#00FF00']
    marker_list = ['o', 'v', 's', '*', '+', 'x', 'D', '1']
    part_center = [[3,3],[3,-3],[-3,-3],[-3,3]]
    for i in range(4):
        xx = []
        yy = []
        for j in range(25):
            xx.append(part_center[i][0] + random.gauss(0,1))
            yy.append(part_center[i][1] + random.gauss(0,1))            
        plt.scatter(xx, yy, c=color_list[i], marker=marker_list[i])
    plt.title('Four Gaussian Blobs Dataset', fontsize=18)
    plt.savefig(os.path.join('build', 'gaussian-blob-dataset.eps'))

def plot_time(filename, plot_name, format, omit_list):
    '''combine different algorithms
    '''
    f = open(os.path.join('build', filename), 'r')
    data = json.loads(f.read())
    x_data = [int(i) for i in data.keys()]
    one_key = str(x_data[0])
    alg_data = {}
    for i in data[one_key].keys():
        alg_data[i] = []
    for i in data.values():
        for k,v in i.items():
            alg_data[k].append(v)
    index = 0
    for k,v in alg_data.items():
        if(k == 'num_edge' or omit_list.count(k) > 0):
            continue
        plt.plot(x_data, v, label=method_translate[k], linewidth=3, color=color_list[index],
            marker=marker_list[index], markersize=12, linestyle=linestyle_list[index])
        index += 1
    plt.ylabel('Time(s)', fontsize=18)
    plt.xlabel('N(nodes)', fontsize=18)
    if plot_name == 'gaussian':
        plot_title = 'Time complexity comparison'
        plt.yscale('log')
    else:
        plot_title = 'Two level graph clustering'
    plt.title(plot_title, fontsize=18)
    plt.legend(fontsize='x-large')
    plt.savefig(os.path.join('build', filename.replace('json', format)), bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    current_time_str = datetime.now().strftime('%Y-%m-%d')    
    parser.add_argument('--date', help='which date to load', default=current_time_str)
    parser.add_argument('--type', default='gaussian', choices=['gaussian', 'two_level'])
    parser.add_argument('--format', default='eps', choices=['eps', 'png'])
    parser.add_argument('--plot_demo', default=False, type=bool, nargs='?', const=True, help='whether to plot the gaussian demo data')    
    parser.add_argument('--debug', default=False, type=bool, nargs='?', const=True, help='whether to enter debug mode') 
    parser.add_argument('--omit', default=None, nargs='+', choices=['pdt', 'psp_i', 'dt', 'pdt_r'])
    args = parser.parse_args()
    if(args.debug):
        pdb.set_trace()
    if args.omit is None:
        omit_list = []
    else:
        omit_list = args.omit
    if(args.plot_demo):
        plot_gaussian_demo_data()
    else:
        plot_time(args.date + '-' + args.type + '.json', args.type, args.format, omit_list)    
