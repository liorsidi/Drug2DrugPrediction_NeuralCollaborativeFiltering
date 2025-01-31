import random
from collections import Counter
import re
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
# from keras.preprocessing import sequence
# from keras.utils import np_utils
from data_reader import read_as_network_x

use_new_version = 0
show_graph = 0
number_of_walks = 4
length_of_walks = 5
window_size = 2
num_of_iteration = 5
number_of_graphs = 1
number_of_nodes = 20
csv_path = "C:\Users\Dvir\Desktop\NNftw\words2.csv"



def Graph_row_to_dictionary(Original_graph):
    """
    This function inserts all of the row names of a graph into a dictionary as values and their index  as keys
    :param Original_graph: The graph which the row names are taken out of
    :return: All of the row names in a dictionary as values, and their index as a key
    """
    Gdict = dict()
    NeuronNames = list(Get_all_names_of_Neurons())
    st = NeuronNames
    for name in range((len(st))):
        Gdict[name] = NeuronNames[name]
    return Gdict

def get_neighbor(row_index, adj_mat):
    # Select an adjacent node to node 'row_index'

    adjacent_nodes = np.argwhere(adj_mat[5] != 0).flatten()
    if len(adjacent_nodes) == 0:
        return -1
    return random.choice(adjacent_nodes)


def make_random_walks(adj_mat, num_of_walks, len_of_walks):
    # Generate a sentence for each random walk
    random_walks_sentences = []

    num_of_adjacency_matrix_rows = adj_mat.shape[0]
    # Iterate over the rows of the adjacency matrix
    # Variable i represents the starting node of the random walk
    for i in range(num_of_adjacency_matrix_rows):
        for j in range(num_of_walks):
            current_node = i

            # Starting node - always node i
            current_walk = list(["Node" + str(i)])

            # travel to other nodes and append them to the random walk
            for k in range(len_of_walks):
                current_node = get_neighbor(current_node, adj_mat)
                if current_node != -1:
                    current_walk.append("Node" + str(current_node))
                else:
                    break

            # append to the result matrix
            current_sentence = ' '.join(current_walk)
            random_walks_sentences.append(current_sentence)
    result = pd.DataFrame({"String": random_walks_sentences})

    # Value counts
    listses = [x.split(" ") for x in random_walks_sentences]
    biglist = [item for sublist in listses for item in sublist]
    count2 = dict(Counter(biglist))

    final_list = [count2["Node"+str(i)] for i in range(len(count2))]

    return result, final_list, listses


def convert_nodes_to_name(adj_mat,Training_Data,Gdict):
    """
    This function recieves the Training data that was generated by make_random_walks and changes the names of the Nodes to to the names of the rows in the send graph.
    :param adj_mat: Graph that is being used for training
    :param Training_Data: Training data, before changing the names
    :param Gdict: Dictionary of row names of adj_mat in order to replace the default names in the Training_Data
    :return: Returns the Training Data with correct names
    """
    row_num = len(adj_mat)
    for Node_num in range(row_num): #A run for each row in the Graph.
        #searchign for a Node# which has no number after it
        Reg_exp = "Node" + str(Node_num) + "(?=[\D]|$)"
        Reg_compiled = re.compile(Reg_exp, re.VERBOSE)
        Training_Data = Reg_compiled.sub(Gdict[Node_num],Training_Data)

    return Training_Data




def save_to_csv(random_walks, csv_path):
    random_walks.to_csv(csv_path, index=False)


def calculate_num_of_iteration(number_of_walks, length_of_walks, num_of_vectors):
    return number_of_walks * (length_of_walks + 1) * num_of_vectors


def make_graph_and_calculate_centrality(graph):
    """
    # make graph
    graph = graph_maker()

    # draw the graph if you want to
    nx.draw_networkx(graph)
    if show_graph:
        plt.show()

    # get the adjacency matrix
    adj_matrix = nx.adjacency_matrix(graph)

    # turn it from sparse to regular
    sparse_df = pd.SparseDataFrame(
        [pd.SparseSeries(adj_matrix[x].toarray().ravel()) for x in np.arange(adj_matrix.shape[0])])
    df = sparse_df.to_dense()

    # change the name of the rows
    df.index = ['Node' + str(x) for x in df]
    adj_matrix = df
    """

    # get the adjacency matrix
    adj_matrix = nx.adjacency_matrix(graph)

    # turn it from sparse to regular
    sparse_df = pd.SparseDataFrame(
        [pd.SparseSeries(adj_matrix[x].toarray().ravel()) for x in np.arange(adj_matrix.shape[0])])
    df = sparse_df.to_dense()

    # change the name of the rows
    df.index = ['Node' + str(x) for x in df]
    adj_matrix = df


    # adj_matrix = Superposition.Get_Original_Graph_from_Path()
    # make the random walks
    random_walks, value_counts, separated_string = make_random_walks(adj_matrix, number_of_walks, length_of_walks)
    return random_walks


def wevi_parser(random_walks_df, window_size):
    df = random_walks_df
    words = []
    contexts_to_words = []
    for current_sentence in df["String"]:
        list_current_words = current_sentence.split()
        for index, word in enumerate(list_current_words):
            contexts_to_words.append(get_context_of_word(list_current_words, index, window_size) + "|" + word)
    output_contexts_string = ','.join(contexts_to_words)
    return output_contexts_string

def is_in_range(words_list, i):
    return 0 <= i < len(words_list)


def get_context_of_word(word_list, index_of_word, window_size=2):
    current_context = []
    for i in range(window_size):
        i += 1
        if is_in_range(word_list, index_of_word - i):
            current_context.append(word_list[index_of_word - i])
        if is_in_range(word_list, index_of_word + i):
            current_context.append(word_list[index_of_word + i])
    return '^'.join(current_context)


def generate_data(corpus, window_size, V):
    maxlen = window_size * 2
    for words_string in corpus:
        words = words_string.split(' ')
        L = len(words)
        for index, word in enumerate(words):
            contexts = []
            labels = []
            s = index - window_size
            e = index + window_size + 1

            contexts.append([words[i] for i in range(s, e) if 0 <= i < L and i != index])
            labels.append(word)

            x = sequence.pad_sequences(contexts, maxlen=maxlen)
            y = np_utils.to_categorical(labels, V)
            yield (x, y)


def main():
    # graph = nx.gnp_random_graph(50, 0.04, seed=1234)
    graph = read_as_network_x()
    random_walks = make_graph_and_calculate_centrality(graph)['String']
    # wevi_parser(random_walks, 5)
    a = list(generate_data(random_walks, 5, 50))
    pass

if __name__ == "__main__":
    main()
