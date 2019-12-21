#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb

db = MySQLdb.connect('localhost','root','root','chain',charset = 'utf8')
cursor = db.cursor()

sql = "CREATE TABLE UTXO(UTXO CHAR(200), OWNER CHAR(100), IF_USE CHAR(1));"
cursor.execute(sql)	
db.commit()

sql = "CREATE TABLE TXS(TXS_HEX TEXT(500));"
cursor.execute(sql)
db.commit()

sql = "CREATE TABLE BLOCK(id INT PRIMARY KEY AUTO_INCREMENT,BLOCK_HEX TEXT(1000));"
cursor.execute(sql)
db.commit()


sql = "CREATE TABLE USER(USERNAME CHAR(30), USER_PK CHAR(100),USER_SK CHAR(100));"
cursor.execute(sql)
db.commit()

db.close()
