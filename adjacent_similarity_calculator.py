import os
import pandas as pd

if os.path.exists('output'):
    files = os.listdir('./output/')
    which_file = ['similarity_matrix.csv' in file for file in files]
    for ind, f in enumerate(files):
        if which_file[ind]:
            sim_mat = pd.read_csv(f'./output/{f}', index_col=0)
            break
else:
    print('create similarity matrix first')



def similar(c1, c2):
    '''
    give two consonants, find the similarity value from the similarity matrix
    :param c1: str.
    :param c2: str.
    :return: float. similarity value
    '''
    return sim_mat.loc[c1, c2]

def calc(root_list):
    '''
    calculate average adjacent similarity for each word
    :param root_list:
    :return:
    '''
    with open(root_list, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    res = []
    for root in lines:
        word_sim = []
        c = root.split()
        for i in range(1, len(c)):
            try:
                word_sim.append(similar(c[i-1], c[i]))
            except KeyError:
                word_sim.append(0)
        word_sim = [i for i in word_sim if i != 0]
        try:
            word_avg = sum(word_sim) / len(word_sim)
        except ZeroDivisionError:
            word_avg = 0
        res.append(word_avg)
    return res

if __name__ == '__main__':
    file = './Type A.txt'
    calc(file)


