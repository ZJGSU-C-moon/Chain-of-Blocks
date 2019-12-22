#!/usr/bin/env python
#-*- coding:utf-8 -*-
import MySQLdb
import random
from sm2 import *
from utils import *
from config import *

DB = MySQLdb.connect(db_host, db_user, db_pass, 'chain')
CURSOR = DB.cursor()

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
    txs = new_tx.get_raw().encode('hex')
    Database(choice=6,txs_hex=txs)
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
    BLOCK_HEX = new_block.get_raw().encode('hex')
    Database(choice=5,block_hex=BLOCK_HEX)
    #sql = "INSERT INTO BLOCK(BLOCK_HEX) VALUES ('%s')" % (new_block.get_raw().encode('hex'))
    #CURSOR.execute(sql)
    #DB.commit()

    #print new_block.get_raw().encode('hex')
    return new_block

def Database(choice,username='NULL',key=[],block_hex='NULL',txs_hex='NULL'):
#1:传出一个时间最久但未被打包使用的交易并将其IF_PACK设置为0
#2:查询用户公私钥 如果没有成功返回0,0 否则 pk,sk
#3:查询用户的账户未使用的utxo,返回列表形式utxo
#4:加入新用户
#5:将打包的BLCOK_HEX传入数据库
#6:存入交易
#:将已使用的utxo的字段IF_USE改为1

    if choice == 1: #传出一个时间最久但未被打包使用的交易并将其IF_PACK设置为0
        sql = "SELECT *  FROM TXS WHERE IF_PACK='0' LIMIT 1"
        CURSOR.execute(sql)
        results = CURSOR.fetchall()
        for row in results:
      	    index = row[0]
      	    txs = row[1]
        sql = "UPDATE TXS SET IF_PACK='1' WHERE id = '%s'" %(index)
	CURSOR.execute(sql)
	DB.commit()
        return txs
    elif choice == 2: #查询用户公私钥 如果没有成功返回0,0
        sql = "SELECT * FROM USER WHERE USERNAME='%s'" % username	
	CURSOR.execute(sql)
	results = CURSOR.fetchall()
        if len(results) == 0:
            return 0,0
    	for row in results:
      	    username = row[0]
      	    pk = row[1]
            sk = row[2]
        return pk,sk
    elif choice == 3: #查询用户的账户未使用的utxo,返回列表形式utxo
        sql = "SELECT * FROM UTXO WHERE OWNER='%s' AND IF_USE='0' " % username	
	URSOR.execute(sql)
	results = CURSOR.fetchall()
        utxos=[]
    	for row in results:
      	    utxo = row[1]
            utxos.append(utxo)
        return utxos
    elif choice == 4: #加入新用户
        sql = "INSERT INTO USER(USERNAME,USER_PK,USER_SK) VALUES ('%s','%s','%s')" % (username,key[0],key[1])
	CURSOR.execute(sql)
	DB.commit()
    elif choice == 5: #将打包的BLCOK_HEX传入数据库
        sql = "INSERT INTO BLOCK(BLOCK_HEX) VALUES ('%s')" % (block_hex)
        CURSOR.execute(sql)
        DB.commit()
    elif choice == 6: #
        sql = "INSERT INTO TXS(TXS_HEX,IF_PACK) VALUES ('%s','%s')" % (txs_hex,'0')
        CURSOR.execute(sql)
        DB.commit()



def login():
    print 'login or register new account:'
    print '1.login'
    print '2.register'
    choice = raw_input('choose:') 
    if choice == '1': 
        username = raw_input('please input your name:')
        flag = 1
        while flag:
            pk,sk = Database(2,username) 
            if pk != 0 and sk != 0:
                flag = 0
            else: 
                username = raw_input('please input the correct name:') 
    elif choice == '2':
	    username = raw_input('please input your name:')
	    print username
	    result = Database(2,username)
	    if result[0] == 0 and result[1] == 0:
	        create_user()
            pk, sk = keygen()
            Database(4,username,[pk,sk])
	    print 'register successfully!\nyour pk:%s \nyour sk:%s' % (pk,sk)

def create_user():
    pass	

if __name__ == '__main__':
    login()
    txs = []
    tx1 = create_tx('123', '456', 50)
    txs.append(tx1)
    new_block = mining(txs)

