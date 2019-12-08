#!/usr/bin/env python
import sys
import requests

tx_url = 'https://blockchain.info/tx/{}?format={}'
block_url = 'https://blockchain.info/block/{}?format={}'

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage:', sys.argv[0], '[CHOICE] [FORMAT] [HASH]'
        print '       [CHOICE] => block / tx'
        print '       [FORMAT] => hex / json'
        exit()
    fmt = sys.argv[2].lower()
    if fmt != 'hex' and fmt != 'json':
        print '[ERROR] Unknown format. hex or json???'
        exit()
    if sys.argv[1].lower() == 'tx':
        tx_hash = sys.argv[3]
        tx_url = tx_url.format(tx_hash, fmt)
        print '=== Downloading from {} ==='.format(tx_url)
        r = requests.get(tx_url)
        print '=== Here is the data of tx {} ==='.format(tx_hash)
        print r.text
    elif sys.argv[1].lower() == 'block':
        block_hash = sys.argv[3]
        block_url = block_url.format(block_hash, fmt)
        print '=== Downloading from {} ==='.format(block_url)
        r = requests.get(block_url)
        print '=== Here is the data of block {} ==='.format(block_hash)
        print r.text
    else:
        print '[ERROR] Unknown choice. block or tx???'
        exit()
