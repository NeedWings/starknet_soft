import runner

#from peewee import *

#if __name__ == "__main__":
#    i = 0
#    options = []
#    print('Choose your database\n')
#    for file in os.listdir('data'):
#        if file.endswith(".db"):
#            print(f'{i} {file}')
#            options.append(file)
#            i += 1
#    option = int(input('Enter number\n'))
#    db = SqliteDatabase(f'data/{option}')

#class Wallet(Model):
#    walletId =   AutoField()
#    #seedEncrypted = TextField()
#    seed = TextField()
#    walletAddress = TextField()
#    walletKey = TextField()
#    ethAddress = TextField()
#    ethKey = TextField()
#    class Meta:
#        database = db

#db.connect()

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
32    mint cheap domain
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

def ping(proxy):
    proxyurl = proxy.split('@')[1].split(':')[0]
    response = os.system("ping -c 1 " + proxyurl)
    if response == 0:
        pass

def checkProxy(proxy_list):
    good_proxy = []
    proxy = [proxy.split('@')[1].split(':')[0] for proxy in proxy_list]

if __name__ == "__main__":
    task_number = int(input(message))
    with open('data/starknet_keys.txt', 'r') as f:
        stark_keys = f.read().splitlines()
    with open('data/eth_keys.txt') as f:
        eth_keys = f.read().splitlines()
    with open('data/proxyServers.txt') as f:
        proxy_servers = f.read().splitlines()
    keysnum = len(stark_keys)
    proxynum = len(proxy_servers)
    proxy_servers = [proxy_servers[i % proxynum] for i in range(keysnum)]
    runner.run(task_number, stark_keys, eth_keys, proxy_servers)
    input("Finished\n")
