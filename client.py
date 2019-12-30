#!/usr/bin/env python
# -*- coding:utf-8 -*-
import random
from sm3 import sm3
from sm2 import keygen
from utils import db_operate, get_balance, create_tx, parse_tx, mining
import getpass


info = {}


def login():
    print '=== Welcome to C-moon coin system ==='
    print 'login or register new account:'
    print '1.login'
    print '2.register'
    print '3.exit'
    choice = raw_input('choose:')
    if choice == '1':
        username = raw_input('Username:')
        result = db_operate(choice=2, username=username)
        if result == True:
            print "The name does not exist!"
            return False
        password = getpass.getpass()
        if sm3(password) != result[0]:
            print 'Wrong password!'
            return False
        else:
            info['username'] = username
            info['pk'] = result[1]
            info['sk'] = result[2]
            return True
    elif choice == '2':
        username = raw_input('Username:')
        result = db_operate(choice=2, username=username)
        if result != True:
            print "The name has been registered!"
            return False
        password = getpass.getpass()
        pk, sk = keygen()
        db_operate(choice=4, username=username,
                   password=sm3(password), key=[pk, sk])
        print 'register successfully!\nyour pk:%s \nyour sk:%s' % (pk, sk)
        info['username'] = username
        info['pk'] = pk
        info['sk'] = sk
        return True
    elif choice == '3':
        exit()
    else:
        print 'Wrong option!'
        return False


def wallet():
    balance = get_balance(info['username'])
    print '=== Wallet interface ==='
    print 'choose an option:'
    print '1.create a tx'
    print '2.start mining'
    print '3.get balance'
    print '4.exit'
    choice = raw_input('choose:')
    if choice == '1':
        dst_username = raw_input('Please input the other name:')
        result = db_operate(choice=2, username=dst_username)
        if result == True:
            print '[!] User does not exist...'
            return False
        value = int(raw_input('Please input the transfer value:'))
        if value > balance:
            print '[!] You do not have this money...'
            return False
        src_pk = info['pk']
        dst_pk = db_operate(choice=8, username=dst_username)
        create_tx(src_pk=src_pk, dst_pk=dst_pk,
                  value=value, src_sk=info['sk'])
        return True
    elif choice == '2':
        txs = []
        tx1 = db_operate(choice=1)
        if tx1 == None:
            print '[!] No tx now...'
            return False
        txs.append(parse_tx(tx1.decode('hex')).get_tx())
        mining(txs, info['pk'])
        return True
    elif choice == '3':
        print '[*] Your balance:', balance
    elif choice == '4':
        exit()
    else:
        return False


if __name__ == '__main__':
    try:
        while True:
            if login():
                break
        while True:
            wallet()
    except KeyboardInterrupt:
        exit()
