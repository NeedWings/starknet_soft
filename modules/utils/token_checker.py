from typing import List

from modules.base_classes.base_account import BaseAccount
from modules.utils.token import StarkToken, EVMToken
from modules.utils.token_storage import nets_eth, nets_stables, nets_weth
from modules.utils.logger import logger
from modules.utils.utils import get_random_value
from modules.config import SETTINGS

class TokenChecker:
    async def get_max_valued_token(self, sender: BaseAccount, tokens: List[StarkToken]):
        max_valued = None
        max_value = 0
        for token in tokens:
            balance = (await sender.get_balance_starknet(token))[0]
            if token.symbol == "ETH":
                balance = balance - get_random_value(SETTINGS["SaveEthOnBalance"])*1e18
                logger.info(f"[{sender.stark_address}] {token.symbol} balance: {balance/10**token.decimals}")
            else:
                if balance/10**token.decimals < SETTINGS["MINIMAL_SWAP_AMOUNTS"][token.symbol]:
                    balance = 0
                    logger.info(f"[{sender.stark_address}] {token.symbol} balance below MINIMAL_SWAP_AMOUNTS, will count as 0")
                else:
                    logger.info(f"[{sender.stark_address}] {token.symbol} balance: {balance/10**token.decimals}")
            usd_value = await token.get_usd_value(balance/10**token.decimals)
            if usd_value>max_value:
                max_valued = token
                max_value = usd_value
        return max_valued, max_value

    async def get_max_valued_native(self, sender: BaseAccount, chains: List[str]):
        value, net, token = 0, None, None

        for chain in chains:
            chain_token: EVMToken = nets_eth[chain]
            token_value = (await chain_token.balance_of(sender.evm_address, sender.get_w3(chain)))[0]
            logger.info(f"[{sender.evm_address}] ({chain}) {chain_token.symbol} balance: {token_value/10**chain_token.decimals}")
            if token_value > value:
                value = token_value
                net = chain
                token = chain_token
        
        return value, net, token

    async def get_max_valued_wrapped(self, sender: BaseAccount, chains: List[str]):
        value, net, token = 0, None, None
        
        for chain in chains:
            chain_token: EVMToken = nets_weth[chain]
            token_value = (await chain_token.balance_of(sender.evm_address, sender.get_w3(chain)))[0]
            logger.info(f"[{sender.evm_address}] ({chain}) {chain_token.symbol} balance: {token_value/10**chain_token.decimals}")
            if token_value > value:
                value = token_value
                net = chain
                token = chain_token
        
        return value, net, token


    async def get_max_valued_stable(self, sender: BaseAccount, chains: List[str]):
        value, net, token = 0, None, None
        
        for chain in chains:
            tokens: List[EVMToken] = nets_stables[chain]
            for chain_token in tokens:
                token_value = (await chain_token.balance_of(sender.evm_address, sender.get_w3(chain)))[1]
                logger.info(f"[{sender.evm_address}] ({chain}) {chain_token.symbol} balance: {token_value}")
                if token_value > value:
                    value = token_value
                    net = chain
                    token = chain_token
        if value != 0:
            value = value*10**token.decimals
        return int(value), net, token


token_checker = TokenChecker()

