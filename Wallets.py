from peewee import *
from playhouse.sqlcipher_ext import SqlCipherDatabase
from getpass import getpass

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
    argent_provider = TextField(null = True)
    okx_evm_address = TextField(null = True)
    okx_starknet_address = TextField(null = True)
    owner = TextField(null = True)
    tags = TextField(null = True)
    class Meta:
        database = db

db.connect()
