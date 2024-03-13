from random import uniform, choice

from web3 import Web3

from modules.utils.token_checker import token_checker
from modules.routers.bridge.starkgate import Starkgate
from modules.routers.bridge.orbiter import Orbiter
from modules.DEXes.one_inch import OneInch
from modules.base_classes.base_account import BaseAccount
from modules.utils.token_storage import eth_ethereum, eth, eth_arbitrum, nets_eth
from modules.config import SETTINGS
from modules.utils.utils import get_random_value, get_random_value_int, sleeping
from modules.utils.logger import logger

STARKGATE = 1
ORBITER_BRIDGE = 2
ORBITER_WITHDRAW = 3

class BridgeRouter:

    def __init__(self, account: BaseAccount, recipient: str):
        self.account = account
        self.recipient = recipient
        self.starkgate = Starkgate(account, recipient)
        self.orbiter_handler = Orbiter(account, recipient)
        self.one_inch_handler = OneInch()


    async def off_bridge(self):
        start_balance = (await eth.balance_of(self.recipient, self.account.client))[1]
        while True:
            try:
                w3 = self.account.get_w3("ethereum")
                human_balance = (await eth_ethereum.balance_of(self.account.evm_address, w3=w3))[1] - get_random_value(SETTINGS["SaveOnWallet"])

                usd_amount_to_bridge = get_random_value(SETTINGS["USDAmountToBridge"])

                eth_price = await eth_ethereum.get_price()

                amount_to_bridge = eth_price*usd_amount_to_bridge

                if amount_to_bridge > human_balance:
                    amount_to_bridge = human_balance
                
                txn = await self.starkgate.bridge_to_stark(amount_to_bridge)

                self.account.send_txn(txn, "ethereum")
                await sleeping(self.account.evm_address)
                break
            except Exception as e:
                logger.error(f"[{self.account.evm_address}] got error: {e}")
                await sleeping(self.account.evm_address, True)

        new_balance = start_balance
        while new_balance == start_balance:
            await sleeping(self.recipient)
            new_balance = (await eth.balance_of(self.recipient, self.account.client))[1]

            logger.info(f"[{self.recipient}] waiting for balance. current: {new_balance} ETH")
            

        logger.success(f"[{self.recipient}] found balance! Current: {new_balance} ETH")

    async def orbiter_bridge(self):
        start_balance = (await eth.balance_of(self.recipient, self.account.client))[1]
        while True:
            try:
                value, net, token = await token_checker.get_max_valued_native(self.account, SETTINGS["nets_for_deposit"])

                human_balance = value/1e18 - get_random_value(SETTINGS["SaveOnWallet"])

                usd_amount_to_bridge = get_random_value(SETTINGS["USDAmountToBridge"])

                eth_price = await eth_ethereum.get_price()

                amount_to_bridge = eth_price*usd_amount_to_bridge

                if amount_to_bridge > human_balance:
                    amount_to_bridge = human_balance

                if amount_to_bridge > SETTINGS["MinEthValue"] and amount_to_bridge > 0.002:
                    logger.info(f'[{self.account.evm_address}] Will bridge from: {net}, balance: {human_balance} ETH')
                    
                    txn = await self.orbiter_handler.bridge_native_to_starknet(amount_to_bridge, net)
                    if txn == -1:
                        return
                    await self.account.send_txn_evm(txn, net)
                    break
                else:
                    logger.info(f'[{self.account.evm_address}] Cant find any ETH balances, will check WETH balances...')

                    value, net, token = token_checker.get_max_valued_wrapped(self.account, SETTINGS["check weth nets"])
                    
                    human_balance = value/1e18
                    
                    logger.info(f'[{self.account.evm_address}] Top chain with WETH assets: {net}, with balance: {human_balance}')

                    if human_balance > SETTINGS["MinEthValue"] and human_balance > 0.002:
                        amount_to_bridge = eth_price*usd_amount_to_bridge

                        if amount_to_bridge > human_balance:
                            amount_to_bridge = human_balance

                        txn = self.orbiter_handler.bridge_weth_to_stark(amount_to_bridge, net)
                        
                        if txn == -1:
                            return
                        await self.account.send_txn_evm(txn, net)
                        break

                    else:
                        logger.info(f'[{self.account.evm_address}] Weth amount is lower than MinEthValue or minimal orbiter limits, will check stable assets')

                        value, net, token = token_checker.get_max_valued_stable(self.account, SETTINGS["check stables nets"])

                        if value == 0:
                            logger.info(f'[{self.account.evm_address}] Cant find any stable assets...')
                            return
            
                        to_recv_amount = (value / 10**token.decimals)/eth_price

                        logger.info(f'[{self.account.evm_address}] Can recieve {round(to_recv_amount, 5)} $eth from selling stable assets')
                        if to_recv_amount > SETTINGS["MinEthValue"] and to_recv_amount > 0.002:
                            logger.info(f'[{self.account.evm_address}] Will try to swap token to ETH or WETH')

                            txn = await self.one_inch_handler.swap_stable(token, value, self.account)
                            await self.account.send_txn_evm(txn, net)
                            await sleeping(self.account.evm_address)
                            await self.orbiter_bridge()
                        else:
                            logger.info(f'[{self.account.evm_address}] to_recv_amount is lower than settings or minimal orbiter value')
                            return
            except Exception as e:
                logger.error(f"[{self.account.evm_address}] got error: {e}")
                await sleeping(self.account.evm_address, True)

        new_balance = start_balance
        while new_balance == start_balance:
            await sleeping(self.recipient)
            new_balance = (await eth.balance_of(self.recipient, self.account.client))[1]

            logger.info(f"[{self.recipient}] waiting for balance. current: {new_balance} ETH")
            

        logger.success(f"[{self.recipient}] found balance! Current: {new_balance} ETH")

    async def withdraw_orbiter(self):
        self.recipient = Web3.to_checksum_address(self.recipient)
        net = choice(SETTINGS["DistNet"])
        start_balance =( await nets_eth[net].balance_of(self.recipient, w3=self.account.get_w3(net)))[1]
        while True:
            try:
            
                amount = get_random_value(SETTINGS["EtherToWithdraw"])

                balance = (await self.account.get_balance_starknet())[1]

                balance = balance - get_random_value(SETTINGS["WithdrawSaving"])

                if amount > balance:
                    amount = balance

                if amount < 0.002:
                    logger.error(f"[{self.account.stark_address}] amount to bridge less than minimal amount")
                    return

                logger.info(f"[{self.account.stark_address}] going to bridge {amount} ETH to {self.recipient}")

                txn = await self.orbiter_handler.bridge_from_stark(amount, net)
                await self.account.send_txn_starknet(txn)

                break
            except Exception as e:
                logger.error(f"[{self.account.stark_address}] got error: {e}")
                await sleeping(self.account.stark_address, True)
                
        
        new_balance = start_balance
        while new_balance == start_balance:
            await sleeping(self.recipient)
            new_balance = (await nets_eth[net].balance_of(self.recipient, w3=self.account.get_w3(net)))[1]

            logger.info(f"[{self.recipient}] waiting for balance. current: {new_balance} ETH")
            

        logger.success(f"[{self.recipient}] found balance! Current: {new_balance} ETH")


    async def bridge(self, bridge_type):
        if bridge_type == STARKGATE:
            await self.off_bridge()
        elif bridge_type == ORBITER_BRIDGE:
            await self.orbiter_bridge()
        elif bridge_type == ORBITER_WITHDRAW:
            await self.withdraw_orbiter()






