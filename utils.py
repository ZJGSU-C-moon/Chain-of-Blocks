#!/usr/bin/env python
import hashlib
import time
import json
import copy
from sm3 import *

__author__ = 'assassinq'

# hash256 = lambda m: hashlib.sha256(hashlib.sha256(m).hexdigest()).hexdigest().decode('hex')[::-1].encode('hex')
hash256 = lambda m: sm3(sm3(m)).decode('hex')[::-1].encode('hex')

class tx_input:
    def __init__(self, tx_id, idx, lengthOfScriptSig, scriptSig):
        self.tx_id = tx_id
        self.idx = idx
        self.lengthOfScriptSig = lengthOfScriptSig
        self.scriptSig = scriptSig

    def get_raw(self):
        raw = ''
        raw += self.tx_id.decode('hex')[::-1]
        raw += hex(self.idx)[2:].zfill(8).decode('hex')[::-1]
        raw += hex(self.lengthOfScriptSig)[2:].zfill(16).decode('hex')[::-1]
        raw += self.scriptSig.decode('hex')[::-1]
        return raw
    
    def get_dict(self):
        return self.__dict__

class tx_output:
    def __init__(self, value, lengthOfScriptPubKey, scriptPubKey):
        self.value = value
        self.lengthOfScriptPubKey = lengthOfScriptPubKey
        self.scriptPubKey = scriptPubKey

    def get_raw(self):
        raw = ''
        raw += hex(self.value)[2:].zfill(16).decode('hex')[::-1]
        raw += hex(self.lengthOfScriptPubKey)[2:].zfill(16).decode('hex')[::-1]
        raw += self.scriptPubKey.decode('hex')[::-1]
        return raw

    def get_dict(self):
        return self.__dict__

class tx:
    def __init__(self, sum_tx_input, tx_inputs, sum_tx_output, tx_outputs):
        self.sum_tx_input = sum_tx_input
        self.tx_inputs = tx_inputs
        self.sum_tx_output = sum_tx_output
        self.tx_outputs = tx_outputs
        self.self_hash = hash256(self.get_raw())

    def get_raw(self):
        raw = ''
        raw += hex(self.sum_tx_input)[2:].zfill(8).decode('hex')[::-1]
        for i in range(self.sum_tx_input):
            raw += self.tx_inputs[i].get_raw()
        raw += hex(self.sum_tx_output)[2:].zfill(8).decode('hex')[::-1]
        for i in range(self.sum_tx_output):
            raw += self.tx_outputs[i].get_raw()
        return raw

    def get_dict(self):
        tx_dict = copy.deepcopy(self.__dict__)
        for i in range(self.sum_tx_input):
            tx_dict['tx_inputs'][i] = copy.deepcopy(self.tx_inputs[i].__dict__)
        for i in range(self.sum_tx_output):
            tx_dict['tx_outputs'][i] = copy.deepcopy(self.tx_outputs[i].__dict__)
        return tx_dict

class block:
    def __init__(self, block_size, version, prev_hash, merkle_root, timestamp, nbits, nonce, sum_tx, txs):
        self.magic = 0xD9B4BEF9 # Magic Number
        self.block_size = block_size
        # Header
        self.version = version
        self.prev_hash = prev_hash
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.nbits = nbits
        self.nonce = nonce
        # Transactions
        self.sum_tx = sum_tx
        self.txs = txs
        # Else
        self.self_hash = hash256(self.get_raw())
        self.header_hash = hash256(self.get_raw()[8:88])

    def get_raw(self):
        raw = ''
        raw += hex(self.magic)[2:].zfill(8).decode('hex')[::-1]
        raw += hex(self.block_size)[2:].zfill(8).decode('hex')[::-1]
        # Header
        raw += hex(self.version)[2:].zfill(8).decode('hex')[::-1]
        raw += self.prev_hash.decode('hex')[::-1]
        raw += self.merkle_root.decode('hex')[::-1]
        raw += hex(self.timestamp)[2:].zfill(8).decode('hex')[::-1]
        raw += hex(self.nbits)[2:].zfill(8).decode('hex')[::-1]
        raw += hex(self.nonce)[2:].zfill(8).decode('hex')[::-1]
        # Transactions
        raw += hex(self.sum_tx)[2:].zfill(16).decode('hex')[::-1]
        for tx in self.txs:
            raw += tx.get_raw()
        return raw

    def get_dict(self):
        block_dict = copy.deepcopy(self.__dict__)
        for i in range(self.sum_tx):
            tx_dict = copy.deepcopy(block_dict['txs'][i].__dict__)
            for j in range(block_dict['txs'][i].sum_tx_input):
                tx_dict['tx_inputs'][j] = copy.deepcopy(block_dict['txs'][i].tx_inputs[j].__dict__)
            for j in range(block_dict['txs'][i].sum_tx_output):
                tx_dict['tx_outputs'][j] = copy.deepcopy(block_dict['txs'][i].tx_outputs[j].__dict__)
            block_dict['txs'][i] = tx_dict
        return block_dict

class fstring():
    def __init__(self, data):
        self.pos = 0
        self.data = data

    def read(self, length=None):
        if length == None:
            length = len(self.data)
        res = self.data[self.pos:self.pos + length]
        self.pos += length
        return res

    def seek(self, pos):
        self.pos = pos

    def get_pos(self):
        return self.pos

class parse_tx_input:
    def __init__(self, handle):
        if type(handle) == str:
            handle = fstring(handle)
        start = handle.get_pos()
        self.prev_tx_hash = handle.read(32)[::-1].encode('hex')
        self.prev_tx_idx = int(handle.read(4)[::-1].encode('hex'), 16)
        if self.prev_tx_hash == '0' * 64: # Coinbase
            self.coinbase_size = int(handle.read(8)[::-1].encode('hex'), 16)
            self.coinbase = handle.read(self.coinbase_size)[::-1].encode('hex')
        else:
            self.script_size = int(handle.read(8)[::-1].encode('hex'), 16)
            self.script = handle.read(self.script_size)[::-1].encode('hex')

    def get_tx_input(self):
        if self.prev_tx_hash == '0' * 64:
            return tx_input(self.prev_tx_hash, self.prev_tx_idx, self.coinbase_size, self.coinbase)
        else:
            return tx_input(self.prev_tx_hash, self.prev_tx_idx, self.script_size, self.script)

class parse_tx_output:
    def __init__(self, handle):
        if type(handle) == str:
            handle = fstring(handle)
        start = handle.get_pos()
        self.value = int(handle.read(8)[::-1].encode('hex'), 16)
        self.script_size = int(handle.read(8)[::-1].encode('hex'), 16)
        self.script = handle.read(self.script_size)[::-1].encode('hex')

    def get_tx_output(self):
        return tx_output(self.value, self.script_size, self.script)

class parse_tx:
    def __init__(self, handle):
        if type(handle) == str:
            handle = fstring(handle)
        start = handle.get_pos()
        self.sum_in = int(handle.read(4)[::-1].encode('hex'), 16)
        self.inputs = [parse_tx_input(handle).get_tx_input() for i in range(self.sum_in)]
        self.sum_out = int(handle.read(4)[::-1].encode('hex'), 16)
        self.outputs = [parse_tx_output(handle).get_tx_output() for i in range(self.sum_out)]
        self.size = handle.get_pos() - start
        handle.seek(start)
        self.raw = handle.read(self.size)
        self.self_hash = hash256(self.raw)

    def get_tx(self):
        return tx(self.sum_in, self.inputs, self.sum_out, self.outputs)

class parse_block:
    def __init__(self, handle):
        if type(handle) == str:
            handle = fstring(handle)
        self.magic = int(handle.read(4)[::-1].encode('hex'), 16)
        self.block_size = int(handle.read(4)[::-1].encode('hex'), 16)
        start = handle.get_pos()
        # Block Header
        self.version = int(handle.read(4)[::-1].encode('hex'), 16)
        self.prev_hash = handle.read(32)[::-1].encode('hex')
        self.merkle_root = handle.read(32)[::-1].encode('hex')
        # self.timestamp = time.gmtime(int(handle.read(4)[::-1].encode('hex'), 16))
        self.timestamp = int(handle.read(4)[::-1].encode('hex'), 16)
        self.nbits = int(handle.read(4)[::-1].encode('hex'), 16)
        self.nonce = int(handle.read(4)[::-1].encode('hex'), 16)
        handle.seek(start)
        self.header = handle.read(80)
        self.header_hash = hash256(self.header)
        # Transactions
        self.sum_tx = int(handle.read(8)[::-1].encode('hex'), 16)
        self.txs = [parse_tx(handle).get_tx() for i in range(self.sum_tx)]
        handle.seek(start)
        self.raw = handle.read(self.block_size)
        self.self_hash = hash256(self.raw)

    def get_block(self):
        return block(self.block_size, self.version, self.prev_hash, self.merkle_root, self.timestamp, self.nbits, self.nonce, self.sum_tx, self.txs)

def cal_tx_hashes(txs):
    tx_hashes = []
    for tx in txs:
        tx_hashes.append(hash256(tx.get_raw()))
    return tx_hashes

def cal_merkle_root(tx_hashes):
    if len(tx_hashes) == 0:
        print '[!] No tx...'
        exit()
    elif len(tx_hashes) == 1:
        return tx_hashes[0]
    else:
        if len(tx_hashes) % 2 == 1:
            new_tx_hashes = []
            for i in range(len(tx_hashes) / 2):
                new_tx_hashes.append(hash256(tx_hashes[2 * i] + tx_hashes[2 * i + 1]))
            new_tx_hashes.append(hash256(tx_hashes[-1]) * 2)
            return cal_merkle_root(new_tx_hashes)
        else:
            new_tx_hashes = []
            for i in range(len(tx_hashes) / 2):
                new_tx_hashes.append(hash256(tx_hashes[2 * i] + tx_hashes[2 * i + 1]))
            return cal_merkle_root(new_tx_hashes)

def cal_header(version, prev_hash, merkle_root, timestamp, nbits):
    raw = ''
    raw += hex(version)[2:].zfill(8).decode('hex')[::-1]
    raw += prev_hash.decode('hex')[::-1]
    raw += merkle_root.decode('hex')[::-1]
    raw += hex(timestamp)[2:].zfill(8).decode('hex')[::-1]
    raw += hex(nbits)[2:].zfill(8).decode('hex')[::-1]
    return raw

def proof_of_work(header, difficulty_bits):
    # calculate the difficulty target
    target = 2 ** (256 - difficulty_bits)
    nonce = 0

    while True:
        hash_result = hash256(header + str(nonce))
        # check if this is a valid result, below the target
        if long(hash_result, 16) < target:
            print "Success with nonce %d" % nonce
            print "Hash is %s" % hash_result
            return (hash_result, nonce)
        nonce += 1

