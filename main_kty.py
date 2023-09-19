import runner
from peewee import *
from playhouse.sqlcipher_ext import SqlCipherDatabase
from getpass import getpass

passphrase = getpass('Enter db password\n')
db = SqlCipherDatabase('dbs/wallets.db', passphrase = passphrase)

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


if __name__ == "__main__":
    stark_keys = []
    eth_keys = []
    task_number = int(input(message))
    work_values = range_generator(input('Enter accs range\n'))
    for value in work_values:
        wallet = Wallet.get(Wallet.walletId == value)
        stark_keys.append(wallet.argent_key)
        eth_keys.append(wallet.eth_key)
    with open('data/proxyServers.txt') as f:
        proxy_servers = f.read().splitlines()
    keysnum = len(work_values)
    proxynum = len(proxy_servers)
    proxy_servers = [proxy_servers[i % proxynum] for i in range(keysnum)]
    runner.run(task_number, stark_keys, eth_keys, proxy_servers)
    input("Finished\n")
