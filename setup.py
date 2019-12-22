#!/usr/bin/python
# -*- coding: UTF-8 -*-
import MySQLdb
from config import *
from utils import *
from sm2 import *

db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, charset='utf8')
cursor = db.cursor()

sql = "DROP DATABASE IF EXISTS chain;"
cursor.execute(sql)
db.commit()

sql = "CREATE DATABASE chain;"
cursor.execute(sql)
db.commit()

sql = "USE chain;"
cursor.execute(sql)
db.commit()

sql = "CREATE TABLE UTXO(id INT PRIMARY KEY AUTO_INCREMENT,UTXO TEXT(500), OWNER TEXT(800), IF_USE CHAR(1));"
cursor.execute(sql)	
db.commit()

sql = "CREATE TABLE TXS(id INT PRIMARY KEY AUTO_INCREMENT, TXS_HEX TEXT(500),IF_PACK CHAR(1));"
cursor.execute(sql)
db.commit()

sql = "CREATE TABLE BLOCK(id INT PRIMARY KEY AUTO_INCREMENT,BLOCK_HEX TEXT(1000));"
cursor.execute(sql)
db.commit()


sql = "CREATE TABLE USER(USERNAME CHAR(30), USER_PK TEXT(800),USER_SK TEXT(800));"
cursor.execute(sql)
db.commit()

print 'Hello! Here is your key pair!'
pk, sk = keygen()
print '[*] pk =', pk
print '[*] sk =', sk
print 'Now start creating genesis block!'

tx_inputs = []
info = 'this is a small blockchain system based on sm.'
tx_input1 = tx_input('0' * 64, 0, len(info), info.encode('hex'))
tx_inputs.append(tx_input1)
tx_outputs = []
tx_output1 = tx_output(50, 64, str(pk))
tx_outputs.append(tx_output1)
init_tx = tx(len(tx_inputs), tx_inputs, len(tx_outputs), tx_outputs)
tx_hex = init_tx.get_raw().encode('hex')
db_operate(choice=6, txs_hex=tx_hex)

init_block = mining([init_tx])

db.close()
