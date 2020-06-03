# -*- coding: utf-8 -*-
import math
import numpy as np
import torch
import torch.nn as nn
from torch.nn.parameter import Parameter
from torch.nn.modules.module import Module

# TextCNN
class TCNN(nn.Module):
    def __init__(self, opt):
        super(TCNN, self).__init__()

        self.fealen = opt["fealen"]
        self.T = opt["T"]
        self.kernel_dim = opt["kernel_dim"]
        self.window_sizes = [2, 3, 4]

        self.convs = nn.ModuleList([nn.Sequential(
            nn.Conv1d(in_channels=self.fealen, out_channels=self.kernel_dim, kernel_size=h),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=self.T-h+1))
            for h in self.window_sizes])
        
        self.fc = nn.Linear(self.kernel_dim * len(self.window_sizes), 1)

    def forward(self, x, adj=None):
        """
        x:  [batch, T, fealen]
        out: [batch, 1]

        batch: batch size  T: Time series length   fealen: feature length
        """

        # x:  [batch, T, fealen] ---> [batch, fealen, T]
        x = x.permute(0, 2, 1) 
        
        # out[i]:  [batch, self.kernel_dim, 1]
        out = [conv(x) for conv in self.convs]

        # out:  [batch, self.kernel_dim*len(self.window_sizes), 1]
        out = torch.cat(out, dim=1) 
        # out:  [batch, self.kernel_dim*len(self.window_sizes)]
        out = out.view(-1, out.size(1)) 

        # out:  [batch, 1]
        out = self.fc(out)
        return out

# LSTM
class LSTM(nn.Module):
    def __init__(self, opt):
        super(LSTM, self).__init__()
        self.fealen = opt["in_dim"]
        self.hidden_dim = opt["hidden_dim"]
        self.lstm = nn.LSTM(self.fealen, self.hidden_dim, batch_first=True)
        self.fc = nn.Linear(self.hidden_dim, 1)

    def forward(self, x, adj=None):
        """
        x:  [batch, T, fealen]
        out: [batch, 1]

        batch: batch size  T: Time series length   fealen: feature length
        """
        # out:  [batch, T, self.hidden_dim]
        out, _ = self.lstm(x)

        # out:  [batch, 1, self.hidden_dim]
        out = out[:, -1, :]

        # out:  [batch, hidden_dim]
        out = out.squeeze(dim=1)

        # out:  [batch, 1]
        out = self.fc(out)

        return out

# GRU 
class GRU(nn.Module):
    def __init__(self, opt):
        super(GRU, self).__init__()
        self.fealen = opt["fealen"]
        self.hidden_dim = opt["hidden_dim"]
        self.gru = nn.GRU(self.fealen, self.hidden_dim, batch_first=True)
        self.fc = nn.Linear(self.hidden_dim, 1)

    def forward(self, x, adj=None):
        """
        x:  [batch, T, fealen] 
        out: [batch, 1]

        batch: batch size  T: Time series length   fealen: feature length
        """

        # out:  [batch, T, self.hidden_dim]
        out, _ = self.gru(x)

        # out:  [batch, 1, self.hidden_dim]
        out = out[:, -1, :]

        # out:  [batch, hidden_dim]
        out = out.squeeze(dim=1)

        # out:  [batch, 1]
        out = self.fc(out)

        return out



class GraphConvolution(Module):
    """
    Simple GCN layer, similar to https://arxiv.org/abs/1609.02907
    """

    def __init__(self, in_features, out_features, bias=True):
        super(GraphConvolution, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight = Parameter(torch.FloatTensor(in_features, out_features))
        if bias:
            self.bias = Parameter(torch.FloatTensor(out_features))
        else:
            self.register_parameter('bias', None)
        self.reset_parameters()

    def reset_parameters(self):
        stdv = 1. / math.sqrt(self.weight.size(1))
        self.weight.data.uniform_(-stdv, stdv)
        if self.bias is not None:
            self.bias.data.uniform_(-stdv, stdv)

    def forward(self, input, adj):
        support = torch.mm(input, self.weight)
        output = torch.spmm(adj, support)
        if self.bias is not None:
            return output + self.bias
        else:
            return output

    def __repr__(self):
        return self.__class__.__name__ + ' (' \
               + str(self.in_features) + ' -> ' \
               + str(self.out_features) + ')'

# GCN+GRU
class TGCN(nn.Module):
    def __init__(self, opt):
        super(GRU, self).__init__()

        self.fealen = opt["fealen"]
        self.nodes = opt["nodes"]
        self.gcn_hidden_dim = opt["gcn_hidden_dim"]
        self.hidden_dim = opt["hidden_dim"]

        self.gcn = GraphConvolution(self.fealen, self.gcn_hidden_dim)
        self.gru = nn.GRU(self.nodes*self.gcn_hidden_dim, self.nodes*self.hidden_dim, batch_first=True)
        self.fc = nn.Linear(self.hidden_dim, 1)

    def forward(self, x, adj):
        """
        x:  [batch, T, nodes, fealen] 
        adj:  [batch, T, nodes, nodes] 
        out: [batch, 1]

        batch: batch size  T: Time series length   nodes: the number of cities 361    fealen: feature length
        """

        # [batch*T*nodes, fealen]
        x = x.view(-1, self.fealen).contiguous()

        # [batch*T*nodes, nodes]
        adj = adj.view(-1, self.nodes).contiguous()

        # [batch*T*nodes, gcn_hidden_dim]
        gcn_out = self.gcn(x, adj)

        # [batch, T, nodes*gcn_hidden_dim]
        gcn_out = gcn_out.view(-1, self.nodes, self.gcn_hidden_dim)
        gcn_out = gcn_out.view(-1, self.T, self.nodes, self.gcn_hidden_dim)
        gcn_out = gcn_out.view(-1, self.T, self.nodes*self.gcn_hidden_dim)

        # [batch, T, nodes*hidden_dim]
        gru_out = self.gru(gcn_out)

        # out:  [batch, 1, nodes*hidden_dim]
        out = gru_out[:, -1, :]

        # out:  [batch, nodes*hidden_dim]
        out = out.squeeze(dim=1)

        # out:  [batch*nodes, hidden_dim]
        out = out.view(-1, self.nodes, self.hidden_dim)
        out = out.view(-1, self.hidden_dim)

        # out:  [batch*nodes, 1]
        out = self.fc(out)

        # out:  [batch, nodes]
        out = out.view(-1, self.nodes)

        return out