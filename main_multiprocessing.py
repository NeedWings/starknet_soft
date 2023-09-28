import runner
from peewee import *
from playhouse.sqlcipher_ext import SqlCipherDatabase
import random
import time
import argparse
import os
import multiprocessing
from getpass import getpass

message = """
Enter task number:
1    ##bridge from arb/opti/eth to start(orbiter/layerswap)
2    random swaps
3    swap to eth
4    add liquidity
5    remove liquidity
6    ##starkgate
7    full module
8    withdraw from stark
9    ##swap stables from chains and bridge to stark
10    show addresses ##
13    deploy accounts
17    lending task
18    remove from lend
21    ##send to stark from different wallet(EVM)
22    ##send from stark to different wallet(EVM)
23    dmail
24    starknet_id
25    ##send to stark off bridge different wallet(EVM)
26    full withdraw(remove liquidity, swap to eth, bridge to chain)
27    full withdraw to different wallet(EVM)
28    collateral zklend
29    universal braavos upgrader
30    return borrowed tokens
31    universal argent upgrader
32    mint cheap domain\n
"""

'''
unavailible tasks:

11    encrypt_secrets #
12    generator #
14    myswap quest #
15    myswap mint nft #
16    stats #
19    mint nft from turkey campain #
20    swaps on fibrous #
'''

def range_generator(user_input):
    tmp=user_input.replace(',',' ').split()
    values =[]
    for a in tmp:
        if '-' in a:
            start, end = (int(x) for x in a.split('-'))
            values +=list(range(start,end+1))
        else:
            values.append(int(a))
    return values

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Starknet bot with proxy support')
    parser.add_argument('-t', type=int,
                        help='task_number')
    parser.add_argument('-i', type=str,
                        help='account ids. ex.: "1-5, 8, 10-50"')
    parser.add_argument('-e', type=str,
                        help='account ids to exclude. ex.: "1-5, 8, 10-50"')
    args = parser.parse_args()
    task_number = args.t if args.t else int(input(message))
    work_values = range_generator(args.i if args.i else input('Enter accs range\n'))
    exclude_values = range_generator(args.e if args.e else input('Enter accs range to exclude\n'))
    work_values = [v for v in work_values if v not in exclude_values]

passphrase = getpass('Enter db password\n')
db = SqlCipherDatabase('../dbs/wallets.db', passphrase = passphrase)

class Wallet(Model):
    walletId =   AutoField()
    seed = TextField()
    eth_key = TextField(null = True)
    eth_address = TextField(null = True)
    argent_seed = TextField(null = True)
    argent_key = TextField(null = True)
    argent_address = TextField(null = True)
    owner = TextField(null = True)
    class Meta:
        database = db

db.connect()

def run(task_arg):
    os.environ['http_proxy'] = task_arg['proxy_server']
    os.environ['HTTP_PROXY'] = task_arg['proxy_server']
    os.environ['https_proxy'] = task_arg['proxy_server']
    os.environ['HTTPS_PROXY'] = task_arg['proxy_server']
    os.environ['no_proxy'] = '127.0.0.1, localhost'
    os.environ['NO_PROXY'] = '127.0.0.1, localhost'
    try:
        runner.run(task_number, task_arg)
    except:
        with open('data/Failed.txt', 'a') as f:
            f.write(f'{task_arg["id"]} : {task_number}\n')
    time.sleep(runner.get_random_value_int(runner.SETTINGS["ThreadRunnerSleep"]))

if __name__ == "__main__":
    task_args = []
    with open('data/proxyServers.txt') as f:
        proxy_servers = f.read().splitlines()
    proxynum = len(proxy_servers)
    for value in work_values:
        wallet = Wallet.get(Wallet.walletId == value)
        task_args.append({'argent_key': wallet.argent_key, 'eth_key': wallet.eth_key, 'proxy_server': proxy_servers[value % proxynum]})
    random.shuffle(task_args)
    with multiprocessing.Pool(processes=1) as s:
        s.map(run, task_args)
    input("Finished\n")
db.close()
