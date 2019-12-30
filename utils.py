#!/usr/bin/env python
# -*- coding:utf-8 -*-
import hashlib
import time
import json
import copy
from sm3 import sm3
from sm2 import verify, sign
import MySQLdb
from config import *


hash256 = lambda m: sm3(sm3(m).decode('hex'))
hash160 = lambda m: hashlib.new('ripemd160', sm3(m).decode('hex')).hexdigest()


class tx_input:
    def __init__(self, tx_id, idx, lengthOfScriptSig, scriptSig, is_coinbase=False):
        self.tx_id = tx_id
        self.idx = idx
        self.is_coinbase = is_coinbase
        if self.is_coinbase == True:
            self.coinbase_size = lengthOfScriptSig
            self.coinbase = scriptSig
        else:
            self.lengthOfScriptSig = lengthOfScriptSig
            self.scriptSig = scriptSig

    def get_raw(self):
        raw = ''
        raw += self.tx_id.decode('hex')[::-1]
        raw += hex(self.idx)[2:].zfill(8).decode('hex')[::-1]
        if self.is_coinbase == True:
            raw += hex(self.coinbase_size)[2:].zfill(16).decode('hex')[::-1]
            raw += self.coinbase.decode('hex')[::-1]
        else:
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
            tx_dict['tx_outputs'][i] = copy.deepcopy(
                self.tx_outputs[i].__dict__)
        return tx_dict


class block:
    def __init__(self, block_size, version, prev_hash, merkle_root, timestamp, nbits, nonce, sum_tx, txs):
        self.magic = 0xD9B4BEF9  # Magic Number
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
                tx_dict['tx_inputs'][j] = copy.deepcopy(
                    block_dict['txs'][i].tx_inputs[j].__dict__)
            for j in range(block_dict['txs'][i].sum_tx_output):
                tx_dict['tx_outputs'][j] = copy.deepcopy(
                    block_dict['txs'][i].tx_outputs[j].__dict__)
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
        self.prev_tx_hash = handle.read(32)[::-1].encode('hex')
        self.prev_tx_idx = int(handle.read(4)[::-1].encode('hex'), 16)
        if self.prev_tx_hash == '0' * 64:  # Coinbase
            self.coinbase_size = int(handle.read(8)[::-1].encode('hex'), 16)
            self.coinbase = handle.read(self.coinbase_size)[::-1].encode('hex')
        else:
            self.script_size = int(handle.read(8)[::-1].encode('hex'), 16)
            self.script = handle.read(self.script_size)[::-1].encode('hex')

    def get_tx_input(self):
        if self.prev_tx_hash == '0' * 64:
            return tx_input(self.prev_tx_hash, self.prev_tx_idx, self.coinbase_size, self.coinbase, is_coinbase=True)
        else:
            return tx_input(self.prev_tx_hash, self.prev_tx_idx, self.script_size, self.script)


class parse_tx_output:
    def __init__(self, handle):
        if type(handle) == str:
            handle = fstring(handle)
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
        self.inputs = [parse_tx_input(handle).get_tx_input()
                       for i in range(self.sum_in)]
        self.sum_out = int(handle.read(4)[::-1].encode('hex'), 16)
        self.outputs = [parse_tx_output(handle).get_tx_output()
                        for i in range(self.sum_out)]
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


def cal_tx_hashes(txs):
    tx_hashes = []
    for tx in txs:
        tx_hashes.append(hash256(tx.get_raw()))
    return tx_hashes


def cal_merkle_root(tx_hashes):
    if len(tx_hashes) == 0:
        return hash256('')
    elif len(tx_hashes) == 1:
        return tx_hashes[0]
    else:
        if len(tx_hashes) % 2 == 1:
            new_tx_hashes = []
            for i in range(len(tx_hashes) / 2):
                new_tx_hashes.append(
                    hash256(tx_hashes[2 * i] + tx_hashes[2 * i + 1]))
            new_tx_hashes.append(hash256(tx_hashes[-1]) * 2)
            return cal_merkle_root(new_tx_hashes)
        else:
            new_tx_hashes = []
            for i in range(len(tx_hashes) / 2):
                new_tx_hashes.append(
                    hash256(tx_hashes[2 * i] + tx_hashes[2 * i + 1]))
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
        hash_result = hash256(header + hex(nonce)[2:].zfill(8).decode('hex')[::-1])
        # check if this is a valid result, below the target
        if long(hash_result, 16) < target:
            print "Success with nonce %d" % nonce
            print "Hash is %s" % hash_result
            return nonce
        nonce += 1


def db_operate(choice, username=None, password=None, key=[], block_hex=None, block_header_hash=None,tx_hex=None, tx_hash=None, user_pk=None, value=None, utxo=None, is_coinbase=False, idx=None, owner=None):
    # 1:传出一个时间最久但未被打包使用的交易并将其IF_PACK设置为0
    # 2:查询用户公私钥 如果没有成功返回0,0 否则 pk,sk
    # 3:查询用户的账户未使用的utxo,返回列表形式utxo
    # 4:加入新用户
    # 5:将打包的BLCOK_HEX、BLOCK_HEADER传入数据库
    # 6:存入交易
    # 7:存入被放进区块的utxo
    # 8:查找用户公钥
    # 9:提供前一个区块头
    # 10:将已使用的utxo的字段IF_USE改为1
    # 11:返回utxo中的tx_hash和idx字段
    # 12:返回指定tx_hash对应的tx

    DB = MySQLdb.connect(db_host, db_user, db_pass, 'chain')
    CURSOR = DB.cursor()

    if choice == 1:  # 传出一个时间最久但未被打包使用的交易并将其IF_PACK设置为1
        sql = "SELECT * FROM TXS WHERE IF_PACK='0' LIMIT 1"
        CURSOR.execute(sql)
        results = CURSOR.fetchall()
        tx = None
        for row in results:
            idx = row[0]
            tx = row[1]
        sql = "UPDATE TXS SET IF_PACK='1' WHERE id = '%s'" % (idx)
        CURSOR.execute(sql)
        DB.commit()
        return tx
    elif choice == 2:  # 查询用户公私钥 如果没有成功返回0,0
        sql = "SELECT * FROM USER WHERE USERNAME='%s'" % (username)
        CURSOR.execute(sql)
        results = CURSOR.fetchall()
        if len(results) == 0:
            return True
        for row in results:
            username = row[0]
            password = row[1]
            pk = row[2]
            sk = row[3]
        return password, pk, sk
    elif choice == 3:  # 查询用户的账户未使用的utxo,返回列表形式utxo
        sql = "SELECT * FROM UTXO WHERE OWNER='%s' AND IF_USE='0' ORDER BY VALUE" % (owner)
        CURSOR.execute(sql)
        results = CURSOR.fetchall()
        utxos = {}
        for row in results:
            utxo = row[1]
            utxos[utxo] = row[5]
        return utxos
    elif choice == 4:  # 加入新用户
        sql = "INSERT INTO USER(USERNAME,PASSWORD,USER_PK,USER_SK) VALUES ('%s','%s','%s','%s')" % (username, password, key[0], key[1])
        CURSOR.execute(sql)
        DB.commit()
    elif choice == 5:  # 将打包的BLCOK_HEX、BLOCK_HEADER传入数据库
        sql = "INSERT INTO BLOCK(BLOCK_HEX,BLOCK_HEADER_HASH) VALUES ('%s','%s')" % (block_hex, block_header_hash)
        CURSOR.execute(sql)
        DB.commit()
    elif choice == 6:  # 存入交易
        if is_coinbase == False:
            sql = "INSERT INTO TXS(TX_HEX, IF_PACK, TX_HASH) VALUES ('%s','%s','%s')" % (tx_hex, '0', tx_hash)
        else:
            sql = "INSERT INTO TXS(TX_HEX, IF_PACK, TX_HASH) VALUES ('%s','%s','%s')" % (tx_hex, '1', tx_hash)
        CURSOR.execute(sql)
        DB.commit()
    elif choice == 7:  # 存入被放进区块的utxo
        sql = "INSERT INTO UTXO(UTXO, TX_HASH, IDX, OWNER, VALUE, IF_USE) VALUES ('%s','%s','%d','%s','%d','%s')" % (utxo, tx_hash, idx, owner, value, '0')
        CURSOR.execute(sql)
        DB.commit()
    elif choice == 8:  # 查找用户公钥
        sql = "SELECT * FROM USER WHERE USERNAME='%s'" % (username)
        CURSOR.execute(sql)
        results = CURSOR.fetchall()
        if len(results) == 0:
            return True
        for row in results:
            username = row[0]
            pk = row[2]
        return pk
    elif choice == 9:  #提供前一个区块头
        sql = "SELECT * FROM BLOCK ORDER BY ID DESC LIMIT 1"
        CURSOR.execute(sql)
        results = CURSOR.fetchall()
        header_hash = '0' * 64
        for row in results:
            header_hash = row[2]
        return header_hash
    elif choice == 10: #将已经使用的utxo置1	
        sql = "UPDATE UTXO SET IF_USE='1' WHERE UTXO='%s'" % (utxo)
        CURSOR.execute(sql)
        DB.commit()
    elif choice == 11: #获取指定utxo对应的tx_id和索引
        sql = "SELECT * FROM UTXO WHERE UTXO='%s'" % (utxo)
        CURSOR.execute(sql)
        result = CURSOR.fetchall()[0]
        return result[2], result[3]
    elif choice == 12:  #获取指定tx_hash的交易
        sql = "SELECT * FROM TXS WHERE TX_HASH='%s'" % (tx_hash)
        CURSOR.execute(sql)
        result = CURSOR.fetchall()[0]
        return result[1]
    DB.close()


def get_utxo(block):
    res_all = []
    for i in range(len(block.txs)):
        idx = 0
        for j in range(len(block.txs[i].tx_outputs)):
            res = {}
            utxo = block.txs[i].tx_outputs[j]
            res['tx_hash'] = hash256(block.txs[i].get_raw())
            res['idx'] = idx
            res['pk_hash'] = utxo.scriptPubKey
            res['utxo'] = utxo.get_raw().encode('hex')
            res['value'] = utxo.value
            res_all.append(res)
            idx += 1
    return res_all


def get_balance(username):
    user_pk = db_operate(choice=2, username=username)[1]
    #print user_pk
    utxos = db_operate(choice=3, owner=hash160(user_pk))
    balance = 0
    #print utxos
    for val in utxos.values():
        balance += int(val)
    return balance


def generate_utxo(pk, sk, value):
    utxos = db_operate(choice=3, owner=hash160(pk))
    total = 0
    result = []
    for utxo, val in utxos.items():
        tx_hash = db_operate(choice=11, utxo=utxo)[0]
        signature = sign(tx_hash, sk)
        prev_tx_hash, idx = db_operate(choice=11, utxo=utxo)
        result.append([prev_tx_hash, idx, signature])
        db_operate(choice=10, utxo=utxo)
        total += int(val)
        if total >= value:
            return result, (total - value)


def create_tx(src_pk, dst_pk, value=0, info='', is_coinbase=False, src_sk=None):
    tx_inputs = []
    if is_coinbase:
        tx_input1 = tx_input('0' * 64, 0, len(info), info[::-1].encode('hex'), is_coinbase=is_coinbase)  # utxo
        tx_inputs.append(tx_input1)
    else:
        inputs, charge = generate_utxo(src_pk, src_sk, value)
        #print inputs
        for prev_tx_hash, idx, signature in inputs:
            single_tx_input = tx_input(prev_tx_hash, int(idx), len((signature + src_pk).decode('hex')), signature + src_pk)  # utxo
            #print single_tx_input.get_dict()
            tx_inputs.append(single_tx_input)
    tx_outputs = []
    #print dst_pk
    #print hash160(dst_pk)
    if is_coinbase:
        tx_output1 = tx_output(50, len(hash160(dst_pk).decode('hex')), hash160(dst_pk))  # transfer
        tx_outputs.append(tx_output1)
    else:
        tx_output1 = tx_output(value, len(hash160(dst_pk).decode('hex')), hash160(dst_pk))  # transfer
        tx_outputs.append(tx_output1)
        #tx_output2 = tx_output(value,64, miner_pk)  # fee
        #tx_outputs.append(tx_output2)
        if charge > 0:
            tx_output3 = tx_output(charge, len(hash160(src_pk).decode('hex')), hash160(src_pk))  # charge
            tx_outputs.append(tx_output3)
    #print tx_output1.get_dict()
    new_tx = tx(len(tx_inputs), tx_inputs, len(tx_outputs), tx_outputs)
    tx_hex = new_tx.get_raw().encode('hex')
    db_operate(choice=6, tx_hex=tx_hex, tx_hash=new_tx.self_hash, is_coinbase=is_coinbase)
    return new_tx


def verify_txs_p2pkh(txs):
    for tx in txs:
        for tx_input in tx.tx_inputs:
            if tx_input.is_coinbase == True:
                continue
            e = tx_input.tx_id
            idx = tx_input.idx
            script = tx_input.scriptSig
            signature = script[:128]
            pk = script[128:]
            prev_tx_hex = db_operate(choice=12, tx_hash=e)
            prev_tx = parse_tx(prev_tx_hex.decode('hex')).get_tx()
            pk_hash = prev_tx.tx_outputs[idx].scriptPubKey
            #print e
            #print signature
            #print pk
            #print pk_hash
            if pk_hash != hash160(pk):
                return False
            res = verify(signature, e, pk)
            if res == False:
                return False
    return True


def mining(txs, miner_pk, info=''):
    version = 1
    prev_hash = db_operate(choice=9)
    coinbase = create_tx(src_pk='0'*64, dst_pk=miner_pk, info=info, is_coinbase=True)
    txs.append(coinbase)
    if verify_txs_p2pkh(txs) == False:
        print '[!] Transactions invalid...'
        return False
    tx_hashes = cal_tx_hashes(txs)
    merkle_root = cal_merkle_root(tx_hashes)
    timestamp = int(time.time())
    nbits = 10
    header = cal_header(version, prev_hash, merkle_root, timestamp, nbits)
    nonce = proof_of_work(header, nbits)
    block_size = 96
    for i in range(len(txs)):
        block_size += len(txs[i].get_raw())
    new_block = block(block_size, version, prev_hash,
                      merkle_root, timestamp, nbits, nonce, len(txs), txs)
    #print new_block.get_dict()
    BLOCK_HEX = new_block.get_raw().encode('hex')
    BLOCK_HEADER_HASH = new_block.header_hash
    db_operate(choice=5, block_hex=BLOCK_HEX, block_header_hash=BLOCK_HEADER_HASH)
    res_all = []
    res_all = get_utxo(new_block)
    for res in res_all:
        db_operate(choice=7, tx_hash=res['tx_hash'], idx=res['idx'], utxo=res['utxo'], owner=res['pk_hash'], value=res['value'])
    return new_block

