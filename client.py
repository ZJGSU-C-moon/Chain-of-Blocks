#!/usr/bin/env python
# -*- coding:utf-8 -*-
import random
from sm2 import *
from utils import *
import getpass


username = ''
pk = ''
sk = ''


def login():
    print '=== Welcome to C-moon coin system ==='
    print 'login or register new account:'
    print '1.login'
    print '2.register'
    print '3.exit'
    choice = raw_input('choose:')
    if choice == '1':
        username = raw_input('Username:')
        result = db_operate(2, username)
        if result == True:
            print "The name does not exist!"
            return False
        password = getpass.getpass()
        if sm3(password) != result[0]:
            print 'Wrong password!'
            return False
        else:
            return True
    elif choice == '2':
        username = raw_input('Username:')
        result = db_operate(2, username)
        if result != True:
            print "The name has been registered!"
            return False
        password = getpass.getpass()
        pk, sk = keygen()
        db_operate(4, username, sm3(password), [pk, sk])
        print 'register successfully!\nyour pk:%s \nyour sk:%s' % (pk, sk)
        return True
    elif choice == '3':
        exit()
    else:
        print 'Wrong option!'
        return False


def wallet():
    print '=== Wallet interface ==='
    print 'choose an option:'
    print '1.create a tx'
    print '2.start mining'
    print '3.exit'
    choice = raw_input('choose:')
    if choice == '1':
        src_pk = raw_input('Please input your pk:')
        dst_pk = raw_input('Please input the other pk:')
        value = raw_input('Please input the tx fee:')
        tx = create_tx(src_pk, src_pk, value)
        #db_operate()
        return True
    elif choice == '2':
        #txs = db_operate()
        new_block = mining(txs, pk)
        return True:
    elif choice == '3':
        exit()
    else:
        return False


if __name__ == '__main__':
    while True:
        if login():
            break
    while True:
        wallet()

