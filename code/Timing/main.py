import sys
import os
import json
import torch
import torch.nn.parallel
import torch.optim as optim
import numpy as np
import opts
from models import TCNN, LSTM, GRU, TGCN
import pandas as pd
from dataset import COVIDDataset
from scipy.stats import linregress
from sklearn.metrics import mean_squared_error #均方误差
from sklearn.metrics import mean_absolute_error #平方绝对误差
import os
os.environ["CUDA_VISIBLE_DEVICES"]="0"

# 评价指标
def evaluation(pred, label):
    _, _, r_value, _, _ = linregress(pred, label)
    mae = mean_absolute_error(real_y, prediction_y)
    rmse = mean_squared_error(real_y, prediction_y) ** 0.5

    return r_value, mae, rmse

def train_model(data_loader, model, optimizer, epoch, loss_function):

    print("Epoch %d Training:" % (epoch))

    model.train()
    epoch_loss = 0
    for n_iter, (city_id, date, input_data, adj, label, label_log) in enumerate(data_loader):

        pred_log = model(input_data, adj)

        loss = loss_function(pred_log, label_log)
        pred = np.trunc(np.exp(pred_log.cpu().detach().numpy())-1)

        r_value, mae, rmse = evaluation(pred, label)

        print("n_iter %d:    R2: %.03f      MAE: %.03f     RMSE: %.03f" % (n_iter, r_value**2, mae, rmse))

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        epoch_loss += loss[0].cpu().detach().numpy()

    print("Training loss: %.03f" % (epoch_loss / (n_iter + 1)))


def test_model(data_loader, model, epoch, loss_function):

    print("Epoch %d Testing:")

    model.eval()

    epoch_loss = 0
    preds = []
    labels = []
    for n_iter, (city_id, date, input_data, adj, label, label_log) in enumerate(data_loader):

        pred_log = model(input_data, adj)

        loss = loss_function(pred_log, label_log)
        pred = np.trunc(np.exp(pred_log.cpu().detach().numpy())-1)
        
        preds.append(pred)
        labels.append(label)

        epoch_loss += loss[0].cpu().detach().numpy()
    
    r_value, mae, rmse = evaluation(preds, labels)
    print("Testing loss: %.03f        R2: %.03f      MAE: %.03f     RMSE: %.03f" % (epoch_loss / (n_iter + 1), r_value**2, mae, rmse))


def Train(opt, model):

    ############## optimizer and loss ################
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=opt["training_lr"], weight_decay=opt["weight_decay"])
    loss_function = torch.nn.MSELoss()

    ############## train and test Dataloader ################

    train_loader = torch.utils.data.DataLoader(COVIDDataset(opt, subset="train"),
                                               batch_size=opt["batch_size"], shuffle=False)

    test_loader = torch.utils.data.DataLoader(COVIDDataset(opt, subset="test"),
                                              batch_size=1, shuffle=False)

    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=opt["step_size"], gamma=opt["step_gamma"])

    ############## train ################
    for epoch in range(opt["train_epochs"]):
        scheduler.step()
        train_model(train_loader, model, optimizer, epoch,  loss_function)
        test_model(test_loader, model, epoch,  loss_function)
    
    ############## save model ################
    torch.save(model, opt["checkpoint_path"] + "/model.pth.tar")


def Test(opt, model):

    ############## load checkpoint ################
    checkpoint = torch.load(opt["checkpoint_path"] + "/model.pth.tar")
    model = torch.load(checkpoint['state_dict'])

    model.eval()
    
    city_ids = []
    dates = [] 
    preds = []
    labels = []

    test_loader = torch.utils.data.DataLoader(COVIDDataset(opt, subset="test"),
                                              batch_size=1, shuffle=False)
    with torch.no_grad():
        for city_id, date, input_data, adj, label, label_log in test_loader:

            pred_log = model(input_data, adj)
            pred = np.trunc(np.exp(pred_log.cpu().detach().numpy())-1)

            city_ids.append(city_id)
            dates.append(date)
            preds.append(pred)
            labels.append(label)
    
    res = pd.DataFrame()
    res['id'] = city_ids
    res['date'] = dates
    res['pred'] = preds
    res['label'] = labels
    res.to_csv(opt['result_file'], index=False)

    print("Testing Result:")
    r_value, mae, rmse = evaluation(preds, labels)
    print("R2: %.03f      MAE: %.03f     RMSE: %.03f" % (r_value**2, mae, rmse))


def main(opt):
    ############## model ################
    if opt['model'] == 'lstm':
        model = LSTM(opt)
    elif opt['model'] == 'gru':
        model = GRU(opt)
    elif opt['model'] == 'tcnn':
        model = TCNN(opt)
    else:
        model = TGCN(opt)

    ############## CUDA ################
    if torch.cuda.is_available():
        print("*************** use gpu ****************")
        model = model.cuda()
    
    ############## train or test ################
    if opt["mode"] == "train":
        Train(opt, model)
    elif opt["mode"] == "test":
        if not os.path.exists("output/"):
            os.makedirs("output/")
        Test(opt, model)