#!/usr/bin/env python
import sys
import hashlib
import time
from utils import *

__author__ = 'assassinq'


def pack():
    tx_inputs = []
    tx_input1 = tx_input('0' * 64, 0, 3, '123456')
    tx_inputs.append(tx_input1)
    print tx_input1.get_dict()
    tx_input2 = tx_input(hash256('utxo0'), 3, 4, '12345678')
    tx_inputs.append(tx_input2)
    print tx_input2.get_dict()
    tx_input3 = tx_input(hash256('utxo1'), 7, 6, '123456654321')
    tx_inputs.append(tx_input3)
    print tx_input3.get_dict()

    tx_outputs = []
    tx_output1 = tx_output(20, 3, 'abcdef')
    tx_outputs.append(tx_output1)
    print tx_output1.get_dict()
    tx_output2 = tx_output(30, 9, 'abcdefabcdefabcdef')
    tx_outputs.append(tx_output2)
    print tx_output2.get_dict()
    tx_output3 = tx_output(78, 4, 'abcdef12')
    tx_outputs.append(tx_output3)
    print tx_output3.get_dict()

    txs = []
    tx1 = tx(1, tx_inputs[:1], 2, tx_outputs[:2])
    tx2 = tx(2, tx_inputs[1:], 3, tx_outputs)
    tx3 = tx(3, tx_inputs, 1, tx_outputs[2:])
    txs.append(tx1)
    txs.append(tx2)
    txs.append(tx3)
    print tx1.get_dict()
    print tx2.get_dict()
    print tx3.get_dict()

    version = 1
    block_size = 96
    for i in range(len(txs)):
        block_size += len(txs[i].get_raw())
    tx_hashes = []
    for i in range(len(txs)):
        tx_hashes.append(txs[i].self_hash)
    merkle_root = cal_merkle_root(tx_hashes)
    timestamp = 1575537538  # int(time.time())
    nbits = 24
    nonce = 1234567
    blocks = []
    block1 = block(block_size, version, '0' * 64, merkle_root,
                   timestamp, nbits, nonce, len(txs), txs)
    blocks.append(block1)
    print block1.get_dict()
    data = block1.get_raw().encode('hex')
    print data
    return data


def parse_tx_test(data):
    try:
        data = data.decode('hex')
        tx_parsed = parse_tx(data)
        tx = tx_parsed.get_tx()
        print tx.get_dict()
        return tx
    except Exception as e:
        print '[!] Error => ', e


def parse_block_test(data):
    try:
        data = data.decode('hex')
        block_parsed = parse_block(data)
        block = block_parsed.get_block()
        print block.get_dict()
        return block
    except Exception as e:
        print '[!] Error => ', e


if __name__ == '__main__':
    #print '===== GENERATE ====='
    #data = pack()
    #print '===== PARSE ====='
    data = raw_input()
    parse_tx_test(data)
    #parse_block_test(data)
