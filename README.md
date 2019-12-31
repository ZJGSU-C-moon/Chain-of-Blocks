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

## Import my data

Data is in `init.sql` (containing three users).

| Username | Password |
| :------: | :------: |
|  admin   | admin123 |
|  alice   |  123456  |
|   bob    |  123456  |

Create database `chain` and source the `.sql` file:

```bash
$ mysql -uroot -p
Enter password:
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 1733
Server version: 5.7.28 Homebrew

Copyright (c) 2000, 2019, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> DROP DATABASE IF EXISTS chain;
Query OK, 0 rows affected (0.00 sec)

mysql> CREATE DATABASE chain;
Query OK, 1 row affected (0.00 sec)

mysql> USE chain;
Database changed
mysql> source setup.sql
Query OK, 0 rows affected (0.00 sec)
...
Query OK, 0 rows affected (0.00 sec)

mysql>
```

## How to start on your own system

Set your db configs in `config.py`.

```bash
$ cat config.py
#!/usr/bin/env python

db_host = 'localhost'
db_user = 'root'
db_pass = 'root'
```

Run `init.py` to init system.

```bash
$ ./init.py
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
- Change password
