#!/usr/bin/python
# -*- coding: UTF-8 -*-
import MySQLdb
from config import *
from utils import db_operate, mining
from sm2 import keygen
from sm3 import sm3
import random
import string
from client import wallet, info


def init():
    global info
    db = MySQLdb.connect(host=db_host, user=db_user,
                         passwd=db_pass, charset='utf8')
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

    sql = "CREATE TABLE UTXO(id INT PRIMARY KEY AUTO_INCREMENT, UTXO TEXT(500), TX_HASH TEXT(100), IDX CHAR(10), OWNER TEXT(800), VALUE CHAR(20), IF_USE CHAR(1));"
    cursor.execute(sql)
    db.commit()

    sql = "CREATE TABLE TXS(id INT PRIMARY KEY AUTO_INCREMENT, TX_HEX TEXT(500), IF_PACK CHAR(1), TX_HASH TEXT(100));"
    cursor.execute(sql)
    db.commit()

    sql = "CREATE TABLE BLOCK(id INT PRIMARY KEY AUTO_INCREMENT, BLOCK_HEX TEXT(1000), BLOCK_HEADER_HASH TEXT(100));"
    cursor.execute(sql)
    db.commit()

    sql = "CREATE TABLE USER(USERNAME CHAR(30), PASSWORD CHAR(100), USER_PK TEXT(800), USER_SK TEXT(800));"
    cursor.execute(sql)
    db.commit()

    print 'Hello admin! Here is your key pair!'
    pk, sk = keygen()
    print '[*] pk =', pk
    print '[*] sk =', sk
    info['username'] = 'admin'
    info['pk'] = pk
    info['sk'] = sk

    print 'Shh! Here is your password!'
    passwd = ''
    for i in range(8):
        passwd += string.printable[random.randint(0, 93)]
    print '[!] passwd =', passwd
    db_operate(choice=4, username='admin', password=sm3(passwd), key=[pk, sk])

    print 'Now start creating genesis block!'
    info = '1712190426-QIANFEIFAN-&-1712190410-JIAXIAOFENG-&-1712190107-CHENKAIFAN'
    init_block = mining([], pk, info)

    db.close()

if __name__ == '__main__':
    try:
        init()
        while True:
            wallet()
    except KeyboardInterrupt:
        exit()
