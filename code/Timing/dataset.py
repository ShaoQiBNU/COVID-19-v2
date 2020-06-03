# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import json
import torch.utils.data as data
import torch
import math
import scipy.sparse as sp


# COVID Dataset
class COVIDDataSet(data.Dataset):

    def __init__(self, opt, subset="train"):

        self.subset = subset
        self.mode = opt["mode"]
        self.model = opt["model"]

        self.T = opt["T"]
        self.nodes = opt["nodes"]
        self.fealen = opt["fealen"]

        self.train_date_path = opt["train_date"]
        self.test_date_path = opt["test_date"]

        self.train_feature_path = opt["train_feature"]
        self.test_feature_path = opt["test_feature"]

        self.adj_path = opt["adj_path"]
        self.city_id_path = opt["city_id"]

        self.idx_map = self.city_map(self.city_id_path)
        self.__loadData()



    ############ get data ###########
    def __getitem__(self, index):

        if self.model in ["lstm", "gru", "tcnn"]:
            if self.train:
                city_id, date, feature, label = self.train_data.iloc[index:index+1, 0].values[0], self.train_data.iloc[index:index+1, 1].values[0], self.train_data.iloc[index:index+1, 3:].values[0], self.train_data.iloc[index:index+1, 2].values[0]
            else:
                city_id, date, feature, label = self.test_data.iloc[index:index+1, 0].values[0], self.test_data.iloc[index:index+1, 1].values[0], self.test_data.iloc[index:index+1, 3:].values[0], self.test_data.iloc[index:index+1, 2].values[0]
            
            feature = np.resize(feature, (self.T, self.fealen))
            label_log = math.log(label+1)

            return city_id, date, feature, None, label, label_log
        
        else:
            if self.train:
                date = self.train_date.iloc[index:index+1, 0].values[0]
                train_df = self.train_feature[self.train_feature["date_label"]==date].sort_values(['id'], ascending = True)
                city_id, feature, label = train_df.iloc[:, 0].values[0], train_df.iloc[:, 3:].values[0], train_df.iloc[:, 2].values[0]
            
            else:
                date = self.test_date.iloc[index:index+1, 0].values[0]
                test_df = self.test_feature[self.train_feature["date_label"]==date].sort_values(['id'], ascending = True)
                city_id, feature, label = test_df.iloc[:, 0].values[0], test_df.iloc[:, 3:].values[0], test_df.iloc[:, 2].values[0]
                
            
            feature = np.resize(feature, (self.nodes, self.T, self.fealen))
            feature = np.transpose(feature, (1, 0, 2))
            adj = self.calculate_laplacian(self.adj_path, date, self.idx_map)
            label_log = math.log(label+1)

            return city_id, date, feature, adj, label, label_log



    ############ get data length ###########
    def __len__(self):

        if self.model in ["lstm", "gru", "tcnn"]:
            if self.train:
                return len(self.train_data)
            else:
                return len(self.test_data)
        
        else:
            if self.train:
                return len(self.train_date)
            else:
                return len(self.test_date)

    


    ############ load data ###########
    def __loadData(self):

        if self.model in ["lstm", "gru", "tcnn"]:
            self.train_data = pd.read_csv(self.train_feature_path, sep=',')
            self.test_data = pd.read_csv(self.test_feature_path, sep=',')
        
        else:
            self.train_date = pd.read_csv(self.train_date_path, sep=',')
            self.test_date = pd.read_csv(self.test_date_path, sep=',')

            self.train_feature = pd.read_csv(self.train_feature_path, sep=',')
            self.test_feature = pd.read_csv(self.test_feature_path, sep=',')
    



    ############ build city map ###########
    def __city_map(self, city_id_path):
        """ build city map:  110000: 0   120000: 1   ... """
        
        # China location id
        china_location = pd.read_csv(city_id_path)
        china_location = china_location[['id', 'location', 'city', 'distinct', 'city_id']]

        china_city = china_location[china_location['city'] == 1]
        china_city = china_city[['id', 'location']]
        print("china city number: " + str(len(china_city)))

        china_distinct = china_location[(china_location['distinct'] == 1) & (china_location['city_id'] == -999)]
        china_distinct = china_distinct[['id', 'location']]
        print("china distinct number: " + str(len(china_distinct)))

        china_city_distinct = pd.concat([china_city, china_distinct])
        china_city_distinct = china_city_distinct[~china_city_distinct['id'].isin(['710000', '810000', '820000', '659006', '659007', '659008', '460300'])]
        print("china city and distinct number: " + str(len(china_city_distinct)))

        china_city_distinct = china_city_distinct.sort_values(['id'], ascending = True)
        china_city_distinct = list(china_city_distinct['id'])

        city_map = {j: i for i, j in enumerate(china_city_distinct)}

        return city_map




    ############ calculate laplacian adj ###########
    def calculate_laplacian(adj_path, date, idx_map):

        """ calculate laplacian adj """

        # build graph
        edges_unordered = np.genfromtxt("{}covid.cites.{}".format(adj_path, date),
                                        dtype=np.int32)
        edges = np.array(list(map(idx_map.get, edges_unordered.flatten())),
                            dtype=np.int32).reshape(edges_unordered.shape)
        adj = sp.coo_matrix((np.ones(edges.shape[0]), (edges[:, 0], edges[:, 1])),
                            shape=(len(idx_map), len(idx_map)),
                            dtype=np.float32)
        # build symmetric adjacency matrix
        adj = adj + adj.T.multiply(adj.T > adj) - adj.multiply(adj.T > adj)

        #features = normalize(features)
        adj = self.normalize(adj + sp.eye(adj.shape[0]))

        adj = self.sparse_mx_to_torch_sparse_tensor(adj)

        return adj
    



    ############ calculate laplacian adj ###########
    def normalize(mx):
        """Row-normalize sparse matrix"""
        rowsum = np.array(mx.sum(1))
        r_inv = np.power(rowsum, -1).flatten()
        r_inv[np.isinf(r_inv)] = 0.
        r_mat_inv = sp.diags(r_inv)
        mx = r_mat_inv.dot(mx)
        return mx
    


    ############ calculate laplacian adj ###########
    def sparse_mx_to_torch_sparse_tensor(sparse_mx):
        """Convert a scipy sparse matrix to a torch sparse tensor."""
        sparse_mx = sparse_mx.tocoo().astype(np.float32)
        indices = torch.from_numpy(
            np.vstack((sparse_mx.row, sparse_mx.col)).astype(np.int64))
        values = torch.from_numpy(sparse_mx.data)
        shape = torch.Size(sparse_mx.shape)
        return torch.sparse.FloatTensor(indices, values, shape)