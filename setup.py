#!/usr/bin/python
# -*- coding: UTF-8 -*-
import MySQLdb
from config import *
from utils import *
from sm2 import *
import random
import string

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

sql = "CREATE TABLE UTXO(id INT PRIMARY KEY AUTO_INCREMENT,UTXO TEXT(500), OWNER TEXT(800), IF_USE CHAR(1));"
cursor.execute(sql)
db.commit()

sql = "CREATE TABLE TXS(id INT PRIMARY KEY AUTO_INCREMENT, TXS_HEX TEXT(500),IF_PACK CHAR(1));"
cursor.execute(sql)
db.commit()

sql = "CREATE TABLE BLOCK(id INT PRIMARY KEY AUTO_INCREMENT,BLOCK_HEX TEXT(1000));"
cursor.execute(sql)
db.commit()

sql = "CREATE TABLE USER(USERNAME CHAR(30), PASSWORD CHAR(100), USER_PK TEXT(800),USER_SK TEXT(800));"
cursor.execute(sql)
db.commit()

print 'Hello admin! Here is your key pair!'
pk, sk = keygen()
print '[*] pk =', pk
print '[*] sk =', sk

print 'Shh! Here is your password!'
passwd = ''
for i in range(8):
    passwd += string.printable[random.randint(0, 93)]
print '[!] passwd =', passwd
db_operate(4, 'admin', sm3(passwd), [pk, sk])

print 'Now start creating genesis block!'
info = 'this is a small blockchain system based on sm.'
init_block = mining([], pk, info)

db.close()
