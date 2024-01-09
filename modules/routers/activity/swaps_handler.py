from random import choice, shuffle

from modules.DEXes.avnu import Avnu
from modules.DEXes.fibrous import Fibrous
from modules.DEXes.jediswap import JediSwap
from modules.DEXes.myswap import MySwap
from modules.DEXes.sithswap import SithSwap
from modules.DEXes.tenkswap import TenKSwap
from modules.config import SETTINGS, SLIPPAGE, MAX_PRICE_IMPACT
from modules.base_classes.base_account import BaseAccount
from modules.base_classes.base_defi import BaseDEX
from modules.utils.token import StarkToken
from modules.utils.token_storage import tokens, tokens_dict
from modules.utils.logger import logger
from modules.utils.utils import get_random_value, get_random_value_int, sleeping
from modules.utils.token_checker import token_checker


swap_dexes = [
    Avnu(),
    Fibrous(),
    JediSwap(),
    MySwap(),
    SithSwap(),
    TenKSwap()
]

supported_dexes_for_swap = []
suppotred_tokens = []

for name in SETTINGS["SwapDEXs"]:
    for dex in swap_dexes:
        if dex.name == name:
            supported_dexes_for_swap.append(dex)

        
for name in SETTINGS["Supported_tokens"]:
    for token in tokens:
        if token.symbol == name:
            suppotred_tokens.append(token)

class SwapsHandler:
    def __init__(self, account: BaseAccount) -> None:
        self.account = account

    def supported_tokens_str_to_token(self, tokens):
        res = []
        for token in tokens:
            res.append(tokens_dict[token])

        return res

    async def random_swaps(self):
        amount = get_random_value_int(SETTINGS["swapAmounts"])
        for i in range(amount):
            try:
                
                dex: BaseDEX = choice(supported_dexes_for_swap)
                token1, usd_value = await token_checker.get_max_valued_token(self.account, self.supported_tokens_str_to_token(dex.supported_tokens))

                assert token1 is not None, "all balances are 0"

                token1: StarkToken = token1
                pair_name = dex.get_pair_for_token(token1.symbol)

                assert pair_name != -5, "can't find pair for token"

                token2: StarkToken = tokens_dict[pair_name]
                
                amount_to_swap = usd_value * get_random_value(SETTINGS["WorkPercent"])

                token1_real_price = await token1.get_price()
                token2_real_price = await token2.get_price()
                token1_val = amount_to_swap/token1_real_price

                logger.info(f"[{self.account.stark_address}] going to swap {token1_val} {token1.symbol} for {token2.symbol} in {dex.name}")
                token1_for_token2_pool_price = await dex.get_token1_for_token2_price(token1, token2, token1_val, self.account)
                
                token2_max_val = amount_to_swap/token2_real_price
                token2_pool_val = token1_val/token1_for_token2_pool_price

                assert 1-MAX_PRICE_IMPACT <= (1-SLIPPAGE) * token2_pool_val / token2_max_val, "price impact too high"


                swap_txn = await dex.create_txn_for_swap(token1_val, token1, token2_pool_val, token2, self.account)
                if swap_txn == -1:
                    await sleeping(self.account.stark_address, True)
                    continue

                await self.account.send_txn_starknet(swap_txn)
                await sleeping(self.account.stark_address)

            except Exception as e:
                logger.error(f"[{self.account.stark_address}] got erroor: {e}")
                await sleeping(self.account.stark_address, True)

    async def save_assets(self, to="ETH"):
        token = tokens_dict[to]
        tokens_for_swap = suppotred_tokens.copy() 
        shuffle(tokens_for_swap)
        for token_to_swap in tokens_for_swap:
            try:
                token_to_swap: StarkToken
                if token == token_to_swap:
                    continue

                balance = (await self.account.get_balance_starknet(token_to_swap))[0]

                if token_to_swap.symbol == "ETH":
                    balance -= int(get_random_value(SETTINGS["SaveEthOnBalance"])*1e18)
                else:
                    if balance/10**token_to_swap.decimals < SETTINGS["MINIMAL_SWAP_AMOUNTS"][token_to_swap.symbol]:
                        balance = 0

                if balance <= 0:
                    logger.info(f"[{self.account.stark_address}] {token_to_swap.symbol} balance 0 or less MINIMAL_SWAP_AMOUNTS. skip")
                    continue

                selected = False
                for i in range(10):
                    dex: BaseDEX = choice(supported_dexes_for_swap)
                    if token_to_swap.symbol in dex.supported_tokens:
                        selected = True
                        break
                
                assert selected, f"can't find dex for {token_to_swap.symbol}"

                amount_to_swap = await token_to_swap.get_usd_value(balance/10**token_to_swap.decimals)

                token1_real_price = await token_to_swap.get_price()
                token2_real_price = await token.get_price()
                token1_val = amount_to_swap/token1_real_price

                token1_for_token2_pool_price = await dex.get_token1_for_token2_price(token_to_swap, token, token1_val, self.account)
                token2_max_val = amount_to_swap/token2_real_price
                token2_pool_val = token1_val/token1_for_token2_pool_price

                assert 1-MAX_PRICE_IMPACT <= (1-SLIPPAGE) * token2_pool_val /token2_max_val, "price impact too high"


                logger.info(f"[{self.account.stark_address}] going to swap {balance/10**token_to_swap.decimals} {token_to_swap.symbol} for {token.symbol} in {dex.name}")
                
                
                swap_txn = await dex.create_txn_for_swap(balance/10**token_to_swap.decimals, token_to_swap, token2_pool_val, token, self.account, full = True)
                if swap_txn != -1:
                    await self.account.send_txn_starknet(swap_txn)
                    await sleeping(self.account.stark_address)

            except Exception as e:
                logger.error(f"[{self.account.stark_address}] got error: {e}")
                await sleeping(self.account.stark_address, True)
    
    async def danger_save_assets(self, to="ETH"):
        token = tokens_dict[to]
        tokens_for_swap = suppotred_tokens.copy() 
        shuffle(tokens_for_swap)
        for token_to_swap in tokens_for_swap:
            try:
                token_to_swap: StarkToken
                if token == token_to_swap:
                    continue

                balance = (await self.account.get_balance_starknet(token_to_swap))[0]

                if token_to_swap.symbol == "ETH":
                    balance -= int(get_random_value(SETTINGS["SaveEthOnBalance"])*1e18)
                else:
                    if balance/10**token_to_swap.decimals < SETTINGS["MINIMAL_SWAP_AMOUNTS"][token_to_swap.symbol]:
                        balance = 0

                if balance <= 0:
                    logger.info(f"[{self.account.stark_address}] {token_to_swap.symbol} balance 0 or less MINIMAL_SWAP_AMOUNTS. skip")
                    continue

                selected = False
                for i in range(10):
                    dex: BaseDEX = choice(supported_dexes_for_swap)
                    if token_to_swap.symbol in dex.supported_tokens:
                        selected = True
                        break
                
                assert selected, f"can't find dex for {token_to_swap.symbol}"

                token1_val = balance/10**token_to_swap.decimals

                token1_for_token2_pool_price = await dex.get_token1_for_token2_price(token_to_swap, token, token1_val, self.account)
                token2_pool_val = token1_val/token1_for_token2_pool_price


                logger.info(f"[{self.account.stark_address}] going to swap {balance/10**token_to_swap.decimals} {token_to_swap.symbol} for {token.symbol} in {dex.name}")
                
                
                swap_txn = await dex.create_txn_for_swap(token1_val, token_to_swap, token2_pool_val, token, self.account, full = True)
                if swap_txn != -1:
                    await self.account.send_txn_starknet(swap_txn)
                    await sleeping(self.account.stark_address)

            except Exception as e:
                logger.error(f"[{self.account.stark_address}] got error: {e}")
                await sleeping(self.account.stark_address, True)
        