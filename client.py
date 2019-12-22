#!/usr/bin/env python
# -*- coding:utf-8 -*-
import random
from sm2 import *
from utils import *


def generate_utxo(pk, value):
    pass


def create_tx(src_pk, dst_pk):
    tx_inputs = []
    tx_input1 = tx_input('0' * 64, 0, 3, '123456')  # utxo
    tx_inputs.append(tx_input1)
    tx_outputs = []
    tx_output1 = tx_output(50, 3, 'abcdef')  # transfer
    tx_outputs.append(tx_output1)
    tx_output2 = tx_output(99, 3, 'abcdef')  # fee
    tx_outputs.append(tx_output2)
    tx_output3 = tx_output(43, 3, 'abcdef')  # charge
    tx_outputs.append(tx_output3)
    new_tx = tx(len(tx_inputs), tx_inputs, len(tx_outputs), tx_outputs)
    txs = new_tx.get_raw().encode('hex')
    db_operate(choice=6, txs_hex=txs)
    return new_tx


def login():
    print 'login or register new account:'
    print '1.login'
    print '2.register'
    choice = raw_input('choose:')
    if choice == '1':
        username = raw_input('please input your name:')
        flag = 1
        pk, sk = db_operate(2, username)
        if pk == 0 and sk == 0:
            print "No users!"
            return False
        else:
            return True
    elif choice == '2':
	    username = raw_input('please input your name:')
	    print username
	    result = db_operate(2, username)
	    if result[0] == 0 and result[1] == 0:
            pk, sk = keygen()
            db_operate(4, username, [pk, sk])
	        print 'register successfully!\nyour pk:%s \nyour sk:%s' % (pk, sk)
            return True
        else:
            print "The name has been registered!"
            return False


if __name__ == '__main__':
    while True:
        if login():
            break
    txs = []
    tx1 = create_tx('123', '456')
    txs.append(tx1)
    new_block = mining(txs)

