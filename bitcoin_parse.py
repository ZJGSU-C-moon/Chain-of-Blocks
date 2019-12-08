#!/usr/bin/env python
import sys
import hashlib
import time

def hash256(m):
    return hashlib.sha256(hashlib.sha256(m).hexdigest()).hexdigest()

class fstream():
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
            handle = fstream(handle)
        start = handle.get_pos()
        self.prev_tx_hash = handle.read(32)[::-1].encode('hex')
        self.prev_tx_idx = int(handle.read(4)[::-1].encode('hex'), 16)
        if self.prev_tx_hash == '0' * 64: # Coinbase
            self.coinbase_size = ord(handle.read(1))
            if self.coinbase_size >= 253:
                pass
            self.coinbase = handle.read(self.coinbase_size)
            self.sequence = int(handle.read(4)[::-1].encode('hex'), 16)
        else:
            self.script_size = ord(handle.read(1))
            if self.script_size >= 253:
                pass
            self.script = handle.read(self.script_size)
            self.sequence = int(handle.read(4)[::-1].encode('hex'), 16)

class parse_tx_output:
    def __init__(self, handle):
        if type(handle) == str:
            handle = fstream(handle)
        start = handle.get_pos()
        self.value = int(handle.read(8)[::-1].encode('hex'), 16)
        self.script_size = ord(handle.read(1))
        if self.script_size >= 253:
            pass
        self.script = handle.read(self.script_size)

class parse_tx:
    def __init__(self, handle):
        if type(handle) == str:
            handle = fstream(handle)
        start = handle.get_pos()
        self.version = int(handle.read(4)[::-1].encode('hex'), 16)
        self.sum_in = ord(handle.read(1))
        if self.sum_in >= 253:
            pass
        self.inputs = [parse_tx_input(handle) for i in range(self.sum_in)]
        self.sum_out = ord(handle.read(1))
        if self.sum_out >= 253:
            pass
        self.outputs = [parse_tx_output(handle) for i in range(self.sum_out)]
        self.locktime = int(handle.read(4)[::-1].encode('hex'), 16)
        self.size = handle.get_pos() - start
        handle.seek(start)
        self.raw = handle.read(self.size)
        self.hash = hash256(self.raw)[::-1].encode('hex')

class parse_block:
    def __init__(self, handle):
        if type(handle) == str:
            handle = fstream(handle)
        self.magic = handle.read(4)
        self.size = int(handle.read(4)[::-1].encode('hex'), 16)
        start = handle.get_pos()
        # Block Header
        self.version = int(handle.read(4)[::-1].encode('hex'), 16)
        self.prev_block_hash = handle.read(32)[::-1].encode('hex')
        self.merkle_root = handle.read(32)[::-1].encode('hex')
        self.timestamp = time.gmtime(int(handle.read(4)[::-1].encode('hex'), 16))
        self.nbits = handle.read(4)
        self.nonce = int(handle.read(4)[::-1].encode('hex'), 16)
        handle.seek(start)
        self.header = handle.read(80)
        self.hash = hash256(self.header[::-1].encode('hex'))
        # Transactions
        self.sum_tx = ord(handle.read(1))
        if sum_tx >= 253:
            pass
        self.txs = [parse_tx(handle) for i in range(self.sum_tx)]
        self.size = handle.get_pos() - start
        handle.seek(start)
        self.raw = handle.read(self.size)
        pass

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:', sys.argv[0], '[HEX_STR]'
        exit()
    try:
        data = sys.argv[1]
        pass
    except Exception as e:
        print '[!] Error => ', e

