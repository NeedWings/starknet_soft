from modules.base_classes.base_account import BaseAccount
from random import choice
from asyncio import sleep
import base64
import hmac

import ccxt
import requests
from web3 import AsyncWeb3
from starknet_py.contract import Contract

from modules.utils.logger import logger
from modules.utils.txn_data_handler import TxnDataHandler
from modules.utils.utils import sleeping, get_random_value, get_pair_for_address_from_file
from modules.utils.token import STARK_TOKEN_ABI
from modules.utils.token_storage import nets_eth
from modules.utils.token_storage import eth as stark_eth
from modules.config import SETTINGS


class OKXHelper:
    address: str = None
    net_names = {
        "arbitrum": "Arbitrum One",
        "optimism": "Optimism",
        "zksync": "zkSync Era",
        "linea": "Linea",
        "starknet": "Starknet"
    }

    fees = {
        "arbitrum":  0.0001,
        "optimism":  0.0001,
        "zksync": 0.0003,
        "linea": 0.0004,
        "starknet": 0.0001

    }
    def __init__(self, api_key: str, secret: str, password: str, account: BaseAccount) -> None:
        self.okx_account = ccxt.okex5({
        'apiKey': api_key,
        'secret': secret,
        'password': password,
        'enableRateLimit': True,
    })
        self.account = account

    def okx_data(self, api_key, secret_key, passphras, request_path="/api/v5/account/balance?ccy=USDT", body='', meth="GET"):
        try:
            import datetime
            def signature(
                timestamp: str, method: str, request_path: str, secret_key: str, body: str = ""
            ) -> str:
                if not body:
                    body = ""

                message = timestamp + method.upper() + request_path + body
                mac = hmac.new(
                    bytes(secret_key, encoding="utf-8"),
                    bytes(message, encoding="utf-8"),
                    digestmod="sha256",
                )
                d = mac.digest()
                return base64.b64encode(d).decode("utf-8")

            dt_now = datetime.datetime.utcnow()
            ms = str(dt_now.microsecond).zfill(6)[:3]
            timestamp = f"{dt_now:%Y-%m-%dT%H:%M:%S}.{ms}Z"

            base_url = "https://www.okex.com"
            headers = {
                "Content-Type": "application/json",
                "OK-ACCESS-KEY": api_key,
                "OK-ACCESS-SIGN": signature(timestamp, meth, request_path, secret_key, body),
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": passphras,
                'x-simulated-trading': '0'
            }
        except Exception as ex:
            logger.error(f"[{self.address}] got error: {ex}")
        return base_url, request_path, headers

    def withdraw(self, amount, net):
        try:            
            self.okx_account.withdraw(
                code    = "ETH",
                amount  = amount,
                address = self.address,
                tag     = None, 
                params  = {
                    "network": self.net_names[net],
                    "fee": self.fees[net],
                    "pwd": self.okx_account.password
                }
            )
            logger.success(f"[{self.address}] withdraw successfull: {amount}")
            return True
        
        except Exception as error:
            logger.error(f"[{self.address}] got errror : {error}")
        return False

    async def withdraw_handl(self):
        net = choice(SETTINGS["nets for okx"])
        if net == "starket":
            self.address = self.account.stark_address
            start_balance = (await self.account.get_balance_starknet(stark_eth))[1]
            new_balance = start_balance
            res = False
            while not res:
                to_withdraw = get_random_value(SETTINGS["to withdraw from okx"])
        
                logger.info(f"[{self.address}] going to withdraw {to_withdraw} ETH from OKX")
                res = self.withdraw(to_withdraw, net)
                if not res:
                    logger.error(f"[{self.address}] got error. trying to send from subs")
                    await self.transfer_to_main_account()
                    await sleeping(self.address, True)
            while new_balance == start_balance:
                logger.info(f"[{self.address}] waiting for balance. current: {new_balance} ETH")
                await sleeping(self.address)
                new_balance = (await self.account.get_balance_starknet(stark_eth))[1]
        else:
            self.address = self.account.evm_address
            start_balance = (await self.account.get_balance_evm(nets_eth[net]))[1]
            new_balance = start_balance
            res = False
            while not res:
                to_withdraw = get_random_value(SETTINGS["to withdraw from okx"])
        
                logger.info(f"[{self.address}] going to withdraw {to_withdraw} ETH from OKX")
                res = self.withdraw(to_withdraw, net)
                if not res:
                    logger.error(f"[{self.address}] got error. trying to send from subs")
                    await self.transfer_to_main_account()
                    await sleeping(self.address, True)
            while new_balance == start_balance:
                logger.info(f"[{self.address}] waiting for balance. current: {new_balance} ETH")
                await sleeping(self.address)
                new_balance = (await self.account.get_balance_evm(nets_eth[net]))[1]

                

        logger.success(f"[{self.address}] found balance! Current: {new_balance} ETH")

    async def deposit_evm(self, to: str, amount: float, from_net: str):
        try:
            w3 = self.account.get_w3(from_net)
            txn_data_handler = TxnDataHandler(self.account, from_net, w3=w3)
            txn = await txn_data_handler.get_txn_data(value=int(amount*1e18))
            txn["to"] = to

            await self.account.send_txn_evm(txn, from_net)
            return True
        except Exception as e:
            logger.error(f"[{self.address}] can't deposit to okx. Error: {e}")
            return False
    
    async def deposit_stark(self, to: str, amount: float):
        try:
           
            contract = Contract(stark_eth.contract_address, STARK_TOKEN_ABI, self.account.stark_native_account)
           
            call = contract.functions["transfer"].prepare(
                int(to, 16),
                int(amount*1e18)
            )
            txn = [call]
            await self.account.send_txn_starknet(txn)
            return True
        except Exception as e:
            logger.error(f"[{self.address}] can't deposit to okx. Error: {e}")
            return False
        
    async def deposit_handl(self):
        net = SETTINGS["send to okx from"]
        if net == "starknet":
            self.address = self.account.stark_address
            rec = get_pair_for_address_from_file("okx_wallet_pairs.txt", self.address)
            if rec is None:
                logger.error(f"[{self.address}] can't find pair. Skip")
                return
           
            balance = (await self.account.get_balance_starknet(stark_eth))[1]
            res = False
            for i in range(10):
                to_send = balance - get_random_value(SETTINGS["WithdrawSaving"])
                logger.info(f"[{self.address}] going to send {to_send} ETH to {rec}")
                res = await self.deposit_stark(rec, to_send)
                if not res:
                    await sleeping(self.address, True)
                if res:
                    break
        else:
            self.address = self.account.evm_address
            rec = get_pair_for_address_from_file("okx_wallet_pairs.txt", self.address)
            if rec is None:
                logger.error(f"[{self.address}] can't find pair. Skip")
                return
            reс = AsyncWeb3.to_checksum_address(reс)
            
            eth = nets_eth[net]
            balance = (await self.account.get_balance_evm(eth))[1]
            
            res = False
            for i in range(10):
                to_send = balance - get_random_value(SETTINGS["WithdrawSaving"])
                logger.info(f"[{self.address}] going to send {to_send} ETH to {rec}")
                res = await self.deposit_evm(rec, to_send, net)
                if not res:
                    await sleeping(self.address, True)
                if res:
                    break
        logger.info(f"[{self.address}] waiting {SETTINGS['wait for okx deposit']} minutes")
        await sleep(SETTINGS["wait for okx deposit"]*60)
        await self.transfer_to_main_account()

    async def transfer_to_main_account(self):
        
        api_key = self.okx_account.apiKey
        secret = self.okx_account.secret
        password =  self.okx_account.password
        session = requests.Session()
        
        _, _, headers = self.okx_data(api_key, secret, password, request_path=f"/api/v5/users/subaccount/list", meth="GET")
        while True:
            try:
                list_sub =  session.get("https://www.okx.cab/api/v5/users/subaccount/list", timeout=10, headers=headers).json()
                list_sub["data"]
                break
            except:
                await sleep(2)
        for sub_data in list_sub['data']:

            name_sub = sub_data['subAcct']

            _, _, headers = self.okx_data(api_key, secret, password, request_path=f"/api/v5/asset/subaccount/balances?subAcct={name_sub}&ccy=ETH", meth="GET")
            while True:
                try:
                    sub_balance = session.get(f"https://www.okx.cab/api/v5/asset/subaccount/balances?subAcct={name_sub}&ccy=ETH",timeout=10, headers=headers)
                    sub_balance = sub_balance.json()  
                    sub_balance = sub_balance['data'][0]['bal']
                    break
                except:
                    await sleep(4)
            logger.info(f'[{self.address}] {name_sub} | sub_balance : {sub_balance} ETH')
            if float(sub_balance) > 0:
                while True:
                    body = {"ccy": f"ETH", "amt": str(sub_balance), "from": 6, "to": 6, "type": "2", "subAcct": name_sub}

                    _, _, headers = self.okx_data(api_key, secret, password, request_path=f"/api/v5/asset/transfer", body=str(body), meth="POST")
                    a = session.post("https://www.okx.cab/api/v5/asset/transfer", data=str(body), timeout=10, headers=headers)
                    if a.status_code != 200:
                        logger.error(f"[{self.address}] failed to send from sub: {a.text}")
                        await sleeping(self.address, True)
                        continue
                    logger.success(f"[{self.address}] sent from sub({name_sub}) ")
                    await sleep(1)
                    break