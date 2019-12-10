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
    pass

if __name__ == '__main__':
    pass

