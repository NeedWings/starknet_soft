from asyncio import sleep
from random import choice

from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient
from web3 import AsyncWeb3

from modules.base_classes.base_account import BaseAccount
from modules.utils.utils import req, sleeping, get_random_value_int
from modules.utils.logger import logger
from modules.utils.txn_data_handler import TxnDataHandler
from modules.config import (
    RPC_LIST, 
    SETTINGS,
    NATIVE_TOKENS_SYMBOLS, 
    NATIVE_WRAPPED_CONTRACTS
)


STARK_TOKEN_ABI = [{"name":"Uint256","size":2,"type":"struct","members":[{"name":"low","type":"felt","offset":0},{"name":"high","type":"felt","offset":1}]},{"data":[{"name":"from_","type":"felt"},{"name":"to","type":"felt"},{"name":"value","type":"Uint256"}],"keys":[],"name":"Transfer","type":"event"},{"data":[{"name":"owner","type":"felt"},{"name":"spender","type":"felt"},{"name":"value","type":"Uint256"}],"keys":[],"name":"Approval","type":"event"},{"name":"name","type":"function","inputs":[],"outputs":[{"name":"name","type":"felt"}],"stateMutability":"view"},{"name":"symbol","type":"function","inputs":[],"outputs":[{"name":"symbol","type":"felt"}],"stateMutability":"view"},{"name":"totalSupply","type":"function","inputs":[],"outputs":[{"name":"totalSupply","type":"Uint256"}],"stateMutability":"view"},{"name":"decimals","type":"function","inputs":[],"outputs":[{"name":"decimals","type":"felt"}],"stateMutability":"view"},{"name":"balanceOf","type":"function","inputs":[{"name":"account","type":"felt"}],"outputs":[{"name":"balance","type":"Uint256"}],"stateMutability":"view"},{"name":"allowance","type":"function","inputs":[{"name":"owner","type":"felt"},{"name":"spender","type":"felt"}],"outputs":[{"name":"remaining","type":"Uint256"}],"stateMutability":"view"},{"name":"permittedMinter","type":"function","inputs":[],"outputs":[{"name":"minter","type":"felt"}],"stateMutability":"view"},{"name":"initialized","type":"function","inputs":[],"outputs":[{"name":"res","type":"felt"}],"stateMutability":"view"},{"name":"get_version","type":"function","inputs":[],"outputs":[{"name":"version","type":"felt"}],"stateMutability":"view"},{"name":"get_identity","type":"function","inputs":[],"outputs":[{"name":"identity","type":"felt"}],"stateMutability":"view"},{"name":"initialize","type":"function","inputs":[{"name":"init_vector_len","type":"felt"},{"name":"init_vector","type":"felt*"}],"outputs":[]},{"name":"transfer","type":"function","inputs":[{"name":"recipient","type":"felt"},{"name":"amount","type":"Uint256"}],"outputs":[{"name":"success","type":"felt"}]},{"name":"transferFrom","type":"function","inputs":[{"name":"sender","type":"felt"},{"name":"recipient","type":"felt"},{"name":"amount","type":"Uint256"}],"outputs":[{"name":"success","type":"felt"}]},{"name":"approve","type":"function","inputs":[{"name":"spender","type":"felt"},{"name":"amount","type":"Uint256"}],"outputs":[{"name":"success","type":"felt"}]},{"name":"increaseAllowance","type":"function","inputs":[{"name":"spender","type":"felt"},{"name":"added_value","type":"Uint256"}],"outputs":[{"name":"success","type":"felt"}]},{"name":"decreaseAllowance","type":"function","inputs":[{"name":"spender","type":"felt"},{"name":"subtracted_value","type":"Uint256"}],"outputs":[{"name":"success","type":"felt"}]},{"name":"permissionedMint","type":"function","inputs":[{"name":"recipient","type":"felt"},{"name":"amount","type":"Uint256"}],"outputs":[]},{"name":"permissionedBurn","type":"function","inputs":[{"name":"account","type":"felt"},{"name":"amount","type":"Uint256"}],"outputs":[]}]
EVM_TOKEN_ABI = [{"inputs":[{"internalType":"string","name":"_name","type":"string"},{"internalType":"string","name":"_symbol","type":"string"},{"internalType":"uint256","name":"_initialSupply","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"spender","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint8","name":"decimals_","type":"uint8"}],"name":"setupDecimals","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]
WRAPPED_TOKEN_ABI = [{"anonymous": False,"inputs":[{"indexed": True,"internalType":"address","name":"src","type":"address"},{"indexed": True,"internalType":"address","name":"guy","type":"address"},{"indexed": False,"internalType":"uint256","name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous": False,"inputs":[{"indexed": True,"internalType":"address","name":"dst","type":"address"},{"indexed": False,"internalType":"uint256","name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous": False,"inputs":[{"indexed": True,"internalType":"address","name":"src","type":"address"},{"indexed": True,"internalType":"address","name":"dst","type":"address"},{"indexed": False,"internalType":"uint256","name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous": False,"inputs":[{"indexed": True,"internalType":"address","name":"src","type":"address"},{"indexed": False,"internalType":"uint256","name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"},{"payable": True,"stateMutability":"payable","type":"fallback"},{"constant": True,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": False,"inputs":[{"internalType":"address","name":"guy","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable": False,"stateMutability":"nonpayable","type":"function"},{"constant": True,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": True,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": False,"inputs":[],"name":"deposit","outputs":[],"payable": True,"stateMutability":"payable","type":"function"},{"constant": True,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": True,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": True,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable": False,"stateMutability":"view","type":"function"},{"constant": False,"inputs":[{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable": False,"stateMutability":"nonpayable","type":"function"},{"constant": False,"inputs":[{"internalType":"address","name":"src","type":"address"},{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable": False,"stateMutability":"nonpayable","type":"function"},{"constant": False,"inputs":[{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable": False,"stateMutability":"nonpayable","type":"function"}]

class EVMToken():
    def __init__(self, symbol, contract_address, decimals, net, stable = False) -> None:
        self.net_name = net
        self.decimals = decimals
        self.symbol = symbol
        self.contract_address = contract_address
        self.stable = stable


    async def balance_of(self, address, w3 = None, of_wrapped = False):
        if w3:
            self.w3 = w3
        else:
            w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(choice(RPC_LIST[self.net])))
        contract = w3.eth.contract(self.contract_address, abi=EVM_TOKEN_ABI)
        while True:
            try:
                balance = await contract.functions.balanceOf(address).call()
                human_balance = balance/10**self.decimals
                return balance, human_balance
            except Exception as e:
                logger.error(f"[{address}] can't get balance of {self.symbol}: {e}")
                await sleeping(address, True)
    
    async def get_approve_txn(self, sender: BaseAccount, spender: str, amount: int, w3 = None):
        if w3:
            w3 = w3
        else:
            w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(choice(RPC_LIST[self.net])))
        contract = w3.eth.contract(self.contract_address, abi=EVM_TOKEN_ABI)
        for i in range(5):
            try:
                txn_data_handler = TxnDataHandler(sender, self.net_name, w3=w3)
                txn = await contract.functions.approve(spender, amount).build_transaction(
                                    await txn_data_handler.get_txn_data()
                                )
                
                await sender.send_txn_evm(txn, self.net_name)
                t = get_random_value_int(SETTINGS["ApproveSleep"])
                logger.info(f"[{sender.evm_address}] sleeping {t} s")
                await sleep(t)
                return None
            except Exception as e:
                logger.error(f"[{sender.evm_address}] can't get approve txn: {e}")
                await sleeping(sender.evm_address, True)
    
    async def get_price(self):
        if self.stable:
            return 1
        else:
            def __find__(ticker: str, rates: list):
                for k in rates:
                    name = k.get("symbol")
                    if name == ticker.upper() + 'USDT':
                        return float(k.get("price"))
            while True:
                response = await req("https://api.binance.com/api/v3/ticker/price")
                if type(response) is list:
                    return __find__(self.symbol, response)
                else:
                    print(f'Cant get response from binance, tring again...')
                    await sleep(5)

    async def get_usd_value(self, amount):
        return (await self.get_price()) * amount      
            

class EVMNativeToken(EVMToken):
    def __init__(self, net) -> None:
        self.net_name = net
        self.decimals = 18
        self.symbol = NATIVE_TOKENS_SYMBOLS[net]
        self.contract_address = NATIVE_WRAPPED_CONTRACTS[net]
        self.abi = WRAPPED_TOKEN_ABI
        self.stable = False

    async def balance_of(self, address, w3 = None, of_wrapped = False):
        if w3:
            w3 = w3
        else:
            w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(choice(RPC_LIST[self.net])))
        contract = w3.eth.contract(self.contract_address, abi=self.abi)
        while True:
            try:
                if not of_wrapped:
                    balance = await w3.eth.get_balance(address)
                    human_balance = balance/10**self.decimals
                    return balance, human_balance
                else:
                    balance = await contract.functions.balanceOf(address).call()
                    human_balance = balance/10**self.decimals
                    return balance, human_balance
            except Exception as e:
                logger.error(f"[{address}] can't get balance of {self.symbol}: {e}")
                await sleeping(address, True)

    async def create_unwrap_txn(self, sender: BaseAccount, w3 = None):
        if w3:
            w3 = w3
        else:
            w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(choice(RPC_LIST[self.net])))

        contract = w3.eth.contract(self.contract_address, abi=self.abi)
        txn_data_handler = TxnDataHandler(sender, self.net_name, w3=w3)
        
        amount = await self.balance_of(sender.evm_address, w3=w3)[0]
               
        if amount <= 1:
            return None
        txn = await contract.functions.withdraw(
            amount
        ).build_transaction(await txn_data_handler.get_txn_data())
        return txn
    
    async def create_wrap_txn(self, wei: bool, amount, sender, w3 = None):
        if w3:
            w3 = w3
        else:
            w3 = w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(choice(RPC_LIST[self.net])))

        contract = w3.eth.contract(self.contract_address, abi=self.abi)
        txn_data_handler = TxnDataHandler(sender, self.net_name, w3=w3)

        if not wei:
            amount = int(amount*10**self.decimals)

        txn = await contract.functions.deposit().build_transaction(await txn_data_handler.get_txn_data(amount))

        return txn

    async def get_approve_txn(self, address, spender, amount, w3 = None):
        return None
    
    
    async def get_approve_txn_wrapped(self, sender: BaseAccount, spender: str, amount: int, w3 = None):
        if w3:
            w3 = w3
        else:
            w3 = w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(choice(RPC_LIST[self.net])))
        contract = w3.eth.contract(self.contract_address, abi=self.abi)
        while True:
            try:

                txn_data_handler = TxnDataHandler(sender, self.net_name, w3=w3)
                txn = await contract.functions.approve(spender, amount).build_transaction(
                                    await txn_data_handler.get_txn_data()
                                )
                
                await sender.send_txn_evm(txn, self.net_name)

                t = get_random_value_int(SETTINGS["ApproveSleep"])
                logger.info(f"[{sender.evm_address}] sleeping {t} s")
                await sleep(t)

                return None
            except Exception as e:
                logger.error(f"[{sender.evm_address}] can't get approve txn: {e}")
                await sleeping(sender.evm_address, True)

class StarkToken():
    def __init__(self, symbol: str, contract_address: int, decimals: int, stable: bool = False) -> None:
        self.decimals = decimals
        self.symbol = symbol
        self.contract_address = contract_address
        self.stable = stable

    async def balance_of(self, address, client: FullNodeClient = None):
        if client is None:
            client = FullNodeClient(choice(RPC_LIST["starknet"]))
        contract = Contract(self.contract_address, STARK_TOKEN_ABI, client)

        while True:
            try:
                balance = (await contract.functions["balanceOf"].call(int(address, 16))).balance
                human_balance = balance/10**self.decimals
                return balance, human_balance
            except Exception as e:
                logger.error(f"[{address}] can't get balance of {self.symbol}: {e}")
                await sleeping(address, True)
        

    def get_approve_call(self, amount: float, spender: int, sender: BaseAccount):
        contract = Contract(self.contract_address, STARK_TOKEN_ABI, sender.stark_native_account)
        decimals = self.decimals
        call = contract.functions["approve"].prepare(
            spender, int(amount*10**decimals)
        )
        return call
    
    def get_approve_call_wei(self, amount: int, spender: int, sender: BaseAccount):
        contract = Contract(self.contract_address, STARK_TOKEN_ABI, sender.stark_native_account)

        call = contract.functions["approve"].prepare(
            spender, amount
        )
        return call
    
    async def get_price(self):
        if self.stable:
            return 1
        elif self.symbol == "LORDS":
            while True:
                response = await req("https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd&ids=lords")
                if isinstance(response, dict):
                    return response["lords"]["usd"]
                else:
                    print(f'Cant get response from binance, tring again...')
                    await sleep(5)
        elif self.symbol == "WSTETH":
            while True:
                response = await req("https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd&ids=wrapped-steth")
                if isinstance(response, dict):
                    return response["wrapped-steth"]["usd"]
                else:
                    print(f'Cant get response from binance, tring again...')
                    await sleep(5)
        else:
            def __find__(ticker: str, rates: list):
                for k in rates:
                    name = k.get("symbol")
                    if name == ticker.upper() + 'USDT':
                        return float(k.get("price"))
            while True:
                response = await req("https://api.binance.com/api/v3/ticker/price")
                if isinstance(response, list):
                    return __find__(self.symbol, response)
                else:
                    print(f'Cant get response from binance, tring again...')
                    await sleep(5)

    async def get_usd_value(self, amount):
        return (await self.get_price()) * amount