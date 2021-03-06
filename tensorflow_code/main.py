#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time    : 2017/11/18 18:24
# Author  : Shi Bo
# File    : main.py

import numpy as np
import os

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
from datetime import datetime
import sys
import shutil
from networks import blackboxDiscriminator

from utils import load_dataset
from utils import evaluate
from utils import writeLog


def train_seq_malGAN():
    """
    main training function: first train subD, then alternately train boxD and malG
    :return: None
    """

    max_seq_len = 1024
    # make workspace directory for current mission and copy code
    timeTag = datetime.now().strftime('%Y-%m-%d')
    #timeTag = '2017-11-19'
    dir_path = '../tensorflow_result/'
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    dir_path = '../tensorflow_result/' + timeTag
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    if os.path.exists(os.path.join(dir_path, 'code')):
        shutil.rmtree(os.path.join(dir_path, 'code'))
    shutil.copytree('.', os.path.join(dir_path, 'code'))
    log_path=dir_path + '/log.txt'
    score_template = 'TPR %(TPR)f\tFPR %(FPR)f\tAccuracy %(Accuracy)f\tAUC %(AUC)f'
    print((str(datetime.now()) + '\tStart training seq_malGAN.'))

    # define substituteD as subD, black box D as boxD and malware Genarator as G
    boxD = blackboxDiscriminator(cell_type='LSTM', rnn_layers=[128], is_bidirectional=True,
                                 attention_layers=[128], ff_layers=[128], batch_size=64, num_token=161,
                                 max_seq_len=max_seq_len * 2, num_class=2, learning_rate=0.001,
                                 scope='black_box_D', model_path=dir_path + '/black_box_D_model')
    # boxD_params = {'vocab_num': 160, 'embedding_dim': 160, 'hidden_dim': 128, 'is_bidirectional': False,
    #                'max_seq_len': 1024, 'attention_layers': None, 'ff_layers': [512], 'class_num': 2}
    # G_params = {}
    print((str(datetime.now()) + '\tFinish defining subD, boxD and G.'))

    # load data
    X_malware, seqLen_malware, X_benigh, seqLen_benigh = \
        load_dataset('../data/API_rand_trainval_len_2048.txt', max_seq_len, 0)
    X = np.vstack((X_malware, X_benigh))
    seqLen = np.hstack((seqLen_malware, seqLen_benigh))
    Y = np.array([1] * len(X_malware) + [0] * len(X_benigh))
    X_malware_test, seqLen_malware_test, X_benigh_test, seqLen_benigh_test = \
        load_dataset('../data/API_rand_test_len_2048.txt', max_seq_len, 0)
    X_test = np.vstack((X_malware_test, X_benigh_test))
    seqLen_test = np.hstack((seqLen_malware_test, seqLen_benigh_test))
    Y_test = np.array([1] * len(X_malware_test) + [0] * len(X_benigh_test))
    print((str(datetime.now()) + '\tFinish loading data.'))
    print((str(datetime.now()) + '\tlen(X)=%d\tlen(X_malware)=%d\tlen(X_benigh)=%d\t' %
                 (len(X), len(X_malware), len(X_benigh))))
    print((str(datetime.now()) + '\tlen(X_test)=%d\tlen(X_malware_test)=%d\tlen(X_benigh_test)=%d' %
                 (len(X_test), len(X_malware_test), len(X_benigh_test))))

    # train substitute Discrimanator first
    print((str(datetime.now()) + '\tStart training black box Discriminator.'))
    boxD.train(np.hstack((X, np.zeros_like(X))), seqLen, Y, max_epochs=50, max_epochs_val=5)
    print((str(datetime.now()) + '\tFinish training subD.'))
    print((str(datetime.now()) + '\tTraining set result:'))
    print((score_template % evaluate(boxD, np.hstack((X, np.zeros_like(X))), seqLen, Y)))
    print((str(datetime.now()) + '\tTest set result:'))
    print((score_template % evaluate(boxD, np.hstack((X_test, np.zeros_like(X_test))), seqLen_test, Y_test)))

    # # train substitute Discriminator and Generator of malGAN
    # for epoch_i in range(5):
    #     pass
    #     # train G
    #     # todo
    #
    #     # train D
    #     # todo
    #
    #     # sample from G and evaluate on current black box D
    #     # todo
    #
    #     # retrain black box D and evaluate generated data from G
    #     # todo
    #
    #     # write to log
    #     # todo


if __name__ == '__main__':
    train_seq_malGAN()
