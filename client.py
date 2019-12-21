#!/usr/bin/env python
from utils import *

def check_utxo(blocks, pk):
    value = 0
    for block in blocks:
        block_parsed = parse_block(block)
        block_obj = block_parsed.get_block()
        block_dict = block_obj.get_dict()
        for i in range(block_dict['sum_tx']):
            for j in range(block_dict['txs'][i]['sum_tx_output']):
                script = block_dict['txs'][i]['tx_outputs'][j]['scriptPubKey']
                if verify(script, pk) == True:
                    value += block_dict['txs'][i]['tx_outputs'][j]['value']
                else:
                    continue
    return value

def generate_utxo(pk, value):
    pass

def create_tx(src_pk, dst_pk, value):
    tx_inputs = []
    tx_input1 = tx_input('0' * 64, 0, 3, '123456')
    tx_inputs.append(tx_input1)
    tx_outputs = []
    tx_output1 = tx_output(value, 3, 'abcdef')
    tx_outputs.append(tx_output1)
    new_tx = tx(len(tx_inputs), tx_inputs, len(tx_outputs), tx_outputs)
    return new_tx

def mining(txs):
    version = 1
    prev_hash = '0' * 64
    tx_hashes = cal_tx_hashes(txs)
    merkle_root = cal_merkle_root(tx_hashes)
    timestamp = int(time.time())
    nbits = 11
    header = cal_header(version, prev_hash, merkle_root, timestamp, nbits)
    (hash_result, nonce) = proof_of_work(header, nbits)
    print 'mining result:', hash_result
    block_size = 96
    for i in range(len(txs)):
        block_size += len(txs[i].get_raw())
    new_block = block(block_size, version, prev_hash, merkle_root, timestamp, nbits, nonce, len(txs), txs)
    print new_block.get_dict()
    return new_block

if __name__ == '__main__':
    txs = []
    tx1 = create_tx('123', '456', 50)
    txs.append(tx1)
    new_block = mining(txs)

