import json
from random import choice, randint
from asyncio import sleep
from time import time
from time import sleep as sync_sleep

from aiohttp_socks import ProxyConnector
from aiohttp import ClientSession
import requests
from web3 import AsyncWeb3
from eth_account import Account as ethAccount
from starknet_py.hash.address import compute_address
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account as StarkNativeAccount
from starknet_py.utils.iterable import ensure_iterable
from starknet_py.net.models import StarknetChainId 
from starknet_py.net.models.transaction import Invoke
from loguru import logger as console_log

from modules.base_classes.base_account import BaseAccount
from modules.config import RPC_LIST, SETTINGS, SETTINGS_PATH, PUBLIC_KEYS_PAIRS, json_remove_comments
from modules.utils.logger import logger
from modules.utils.utils import sleeping, normalize_to_32_bytes, handle_dangerous_request
from modules.utils.token import EVMToken, StarkToken
from modules.utils.token_storage import eth

class Account(BaseAccount): #TODO: combine get_balance_evm and get_balance_starknet to get_balance
    w3 = {}
    session = None
    def __init__(self, private_key: str, proxy = None):
        private_key = normalize_to_32_bytes(private_key)
        self.private_key = private_key
        self.evm_address = ethAccount.from_key(private_key).address
        self.setup_w3(proxy=proxy)
        self.proxy = proxy
        self.is_set = False

    async def setup_account(self):
        await self.setup_client(proxy=self.proxy)
        self.stark_key_pair = KeyPair.from_private_key(int(self.private_key, 16))
        self.stark_address = Account.get_starknet_address_from_private(self.private_key)
        self.stark_native_account = StarkNativeAccount(
            address=self.stark_address,
            client=self.client,
            key_pair=self.stark_key_pair,
            chain=StarknetChainId.MAINNET
        )
        self.is_set = True

    async def send_txn_starknet(self, calldata):
        await self.wait_for_better_eth_gwei()
        i = 0
        while SETTINGS["RetriesLimit"] > i:
            resp = await self.get_invocation(calldata)
            if resp == -3:
                logger.error(f"[{self.stark_address}] max retries limit reached")
                return -3, ""
            try:
                logger.success(f"[{self.stark_address}] sending txn with hash: {hex(resp.transaction_hash)}")
                await self.stark_native_account.client.wait_for_tx(resp.transaction_hash)
                logger.success(f"[{self.stark_address}] tnx has sent! Hash: {hex(resp.transaction_hash)}")
                return 1, hex(resp.transaction_hash)
            except Exception as e:
                logger.error(f"[{self.stark_address}]  got error while sending txn: {hex(resp.transaction_hash)}. Error: {e}")
                await sleeping(self.stark_address, True)
            i +=1
        logger.error(f"[{self.stark_address}] max retries limit reached")
        return -1, ""
        
    async def get_invocation(self, calls):
        i = 0
        while i <= SETTINGS["RetriesLimit"]:
            i+=1
            try:
                invocation = await self.stark_native_account.execute_v1(calls=calls, auto_estimate=True)
                return invocation
            except Exception as e:
                logger.error(f"[{self.stark_address}] can't create transaction. Error:{e}")
                await sleeping(self.stark_address, True)
        return -3

    async def get_balance_starknet(self, token: StarkToken = None):
        if token is None:
            token = eth
        balance = await handle_dangerous_request(
            self.stark_native_account.get_balance, 
            f"can't get balance of {token.symbol}. Error", 
            self.stark_address, 
            token.contract_address
        )

        return balance, balance/10**token.decimals



    @staticmethod
    def create_starknet_address(private_key: str):
        if SETTINGS["Provider"].lower() in ["argent_newest", "argent"]:
            class_hash = 0x01a736d6ed154502257f02b1ccdf4d9d1089f80811cd6acad48e6b6a9d1f2003

            key_pair = KeyPair.from_private_key(int(private_key, 16))
            salt = key_pair.public_key


            account_initialize_call_data = [key_pair.public_key, 0]

            call_data = [
                *account_initialize_call_data
            ]
        elif SETTINGS["Provider"].lower() == "braavos":
            class_hash = 0x03131fa018d520a037686ce3efddeab8f28895662f019ca3ca18a626650f7d1e
            key_pair = KeyPair.from_private_key(int(private_key, 16))
            salt = key_pair.public_key
            account_initialize_call_data = [key_pair.public_key]

            call_data = [
                0x5aa23d5bb71ddaa783da7ea79d405315bafa7cf0387a74f4593578c3e9e6570,
                0x2dd76e7ad84dbed81c314ffe5e7a7cacfb8f4836f01af4e913f275f89a3de1a,
                len(account_initialize_call_data),
                *account_initialize_call_data
            ]  
        else:
            console_log.error(f"Selecterd unsupported provider: {SETTINGS['Provider']}. Please use Argent or Braavos")
            input()
            exit() 
            return
        address = compute_address(
            salt=salt,
            class_hash=class_hash,  
            constructor_calldata=call_data,
            deployer_address=0,
        )
        PUBLIC_KEYS_PAIRS[normalize_to_32_bytes(hex(key_pair.public_key))] = normalize_to_32_bytes(hex(address))
        return normalize_to_32_bytes(hex(address))
        

    @staticmethod
    def get_starknet_address_from_private(private_key: str):
        key_pair =  KeyPair.from_private_key(int(private_key, 16))
        pub_key = normalize_to_32_bytes(hex(key_pair.public_key))
        if pub_key in list(PUBLIC_KEYS_PAIRS.keys()):
            return normalize_to_32_bytes(PUBLIC_KEYS_PAIRS[pub_key])
        base_link = "https://recovery.braavos.app/pubkey-to-address/?network=mainnet-alpha&pubkey="

        while True:
            try:
                resp = requests.get(f"{base_link}{pub_key}")
                addrs = resp.json()["address"]
                if len(addrs) == 0:
                    return Account.create_starknet_address(private_key)
                PUBLIC_KEYS_PAIRS[pub_key] = normalize_to_32_bytes(addrs[0])
                return normalize_to_32_bytes(addrs[0])
                    
            except Exception as e:
                console_log.error(f"can't get address:{e} trying again")
                sync_sleep(5)
       



    async def setup_client(self, proxy):
        if self.session is not None:
            await self.session.close()
            self.session = None
        if proxy is not None:
            self.session = ClientSession(connector=ProxyConnector.from_url(proxy))
        else:
            self.session = ClientSession()
        self.client = FullNodeClient(choice(RPC_LIST["starknet"]), session=self.session)

    def setup_w3(self, proxy=None):
        if proxy:
            req_proxy = {
                "proxy": proxy,
                "timeout": 10,
                "ssl": False,
            }
            self.proxies = req_proxy["proxy"]
            for chain in RPC_LIST:
                self.w3[chain] =  AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(choice(RPC_LIST[chain]), request_kwargs=req_proxy))
        else:
            req_proxy = {
                
                "timeout": 10,
                "ssl": False,
            }
            for chain in RPC_LIST:
                self.w3[chain] =  AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(choice(RPC_LIST[chain]), request_kwargs=req_proxy))

    def get_w3(self, net_name):
        self.setup_w3(self.proxy)
        return self.w3[net_name]
    
    async def get_balance_evm(self, token: EVMToken):
        return await token.balance_of(self.evm_address, self.get_w3(token.net_name))
    
    async def wait_for_better_eth_gwei(self):
        w3 = self.w3["ethereum"]
        while True:
            while True:
                try:
                    f = open(f"{SETTINGS_PATH}settings.json", "r")
                    a = json_remove_comments(f.read())
                    SETTINGS = json.loads(a)
                    f.close()
                    break
                except Exception as e:
                    input("Error with settings.json. Please fix it and press Enter")
            max_gas = AsyncWeb3.to_wei(SETTINGS["MaxEthGwei"], 'gwei')
            try:
                gas_price = await w3.eth.gas_price
                if gas_price > max_gas:
                    h_gas, h_max = AsyncWeb3.from_wei(gas_price, 'gwei'), AsyncWeb3.from_wei(max_gas, 'gwei')
                    logger.error(f'[{self.stark_address}] Current gasPrice in eth: {h_gas} | Max gas price in eth: {h_max}')
                    t = randint(*SETTINGS["WaitGWEISleep"])
                    logger.info(f"[{self.stark_address}] sleeping {t} seconds")
                    await sleep(t)
                else:
                    return round(gas_price)
                
            except Exception as error:
                print(error)
                logger.error(f'[{self.evm_address}] Error: {error}')
                await sleeping(self.evm_address, True)

    async def send_without_wait_evm(self, txn, net):
        await self.wait_for_better_eth_gwei()
            
        w3: AsyncWeb3 = self.w3[net]

        gasEstimate = await w3.eth.estimate_gas(txn)

        txn['gas'] = round(gasEstimate*1.5) 
        signed_txn = w3.eth.account.sign_transaction(txn, private_key=self.private_key)
        tx_token = w3.to_hex(await w3.eth.send_raw_transaction(signed_txn.rawTransaction))

        logger.success(f"[{self.evm_address}] sending txn: {tx_token}")
        return True, signed_txn, tx_token
        
    async def send_txn_evm(self, txn, net):
        for i in range(10):
            try:
                await self.wait_for_better_eth_gwei()
            
                w3: AsyncWeb3 = self.w3[net]

                gasEstimate = await w3.eth.estimate_gas(txn)

                txn['gas'] = round(gasEstimate*1.5) 
                signed_txn = w3.eth.account.sign_transaction(txn, private_key=self.private_key)
                tx_token = w3.to_hex(await w3.eth.send_raw_transaction(signed_txn.rawTransaction))

                logger.success(f"[{self.evm_address}] sending txn: {tx_token}")
                success = await self.wait_until_txn_finished_evm(tx_token, net)
                return success, signed_txn, tx_token
            except Exception as e:
                logger.error(f"[{self.evm_address}] got error: {e}")
                await sleeping(self.evm_address, True)

    
    async def wait_until_txn_finished_evm(self, hash, net, max_time = 500):
        w3: AsyncWeb3 = self.w3[net]
        start_time = time()
        while True:
            try:
                if time() - start_time > max_time:
                    logger.error(f'[{self.evm_address}] {hash} transaction is failed (timeout)')
                    return False
                receipts = await w3.eth.get_transaction_receipt(hash)
                status = receipts.get("status")

                if status == 1:
                    logger.success(f"[{self.evm_address}] {hash} is completed")
                    return True
                elif status is None:
                    #print(f'[{hash}] still processed') #DEBUG
                    await sleep(0.3)
                elif status != 1:
                    logger.error(f'[{self.evm_address}] {hash} transaction is failed')
                    return False
            except:
                #print(f"[{hash}] still in progress") #DEBUG
                await sleep(1)         
