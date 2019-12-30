# Chain-of-Blocks

Our Final Work of Cryptocurrencies and Blockchain Technology. A mini coin (using SM2 & SM3) based on Python.

## Environment

macOS Mojave 10.14.4

```bash
$ python -V
Python 2.7.17
$ mysql -V
mysql  Ver 14.14 Distrib 5.7.28, for osx10.14 (x86_64) using  EditLine wrapper
```

## How to start

Set your db configs in `config.py`.

```bash
$ cat config.py
#!/usr/bin/env python

db_host = 'localhost'
db_user = 'root'
db_pass = 'root'
```

Run `setup.py` to init system.

```bash
$ ./setup.py
Hello admin! Here is your key pair!
[*] pk = ***
[*] sk = ***
Shh! Here is your password!
[!] passwd = ********
Now start creating genesis block!
Success with nonce ***
Hash is ***
=== Wallet interface ===
choose an option:
1.create a tx
2.start mining
3.get balance
4.exit
choose:
```

Run `client.py` to register other users:

```bash
$ ./client.py 
=== Welcome to C-moon coin system ===
login or register new account:
1.login
2.register
3.exit
choose:
```

## TODO

- P2SH (now is P2PKH)
- Miner's fee
- GUI
- P2P

