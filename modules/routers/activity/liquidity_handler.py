from random import choice, shuffle

from starknet_py.contract import Contract

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
from modules.utils.token_storage import eth

liq_dexes = [
    JediSwap(),
    MySwap(),
    SithSwap(),
    TenKSwap()
]
suppotred_tokens = []
supported_dexes_for_liq = []

for name in SETTINGS["LiqDEXs"]:
    for dex in liq_dexes:
        if dex.name == name:
            supported_dexes_for_liq.append(dex)

        
for name in SETTINGS["Supported_tokens"]:
    for token in tokens:
        if token.symbol == name:
            suppotred_tokens.append(token)

class LiquidityHandler:
    def __init__(self, account: BaseAccount) -> None:
        self.account = account

    def supported_tokens_str_to_token(self, tokens):
        res = []
        for token in tokens:
            res.append(tokens_dict[token])

        return res
    
    async def add_liq(self):
        liq_amount = get_random_value_int(SETTINGS["AddLiqAmount"])
        if liq_amount < 1:
            return
        
        for i in range(liq_amount):
            try:
                dex: BaseDEX = choice(supported_dexes_for_liq)
                token1, usd_value = await token_checker.get_max_valued_token(self.account, self.supported_tokens_str_to_token(dex.supported_tokens))
                assert token1 is not None, "all balances are 0"
        
                token1: StarkToken = token1
                token2 = dex.get_pair_for_token(token1.symbol)

                if token2 == -5:
                    continue
                token2: StarkToken = tokens_dict[token2]
                token2_usd_value = await token2.get_usd_value((await self.account.get_balance_starknet(token2))[1])

                amount_to_add = usd_value * get_random_value(SETTINGS["LiqWorkPercent"])/2

                token1_real_price = await token1.get_price()
                token2_real_price = await token2.get_price()
                token1_val = amount_to_add/token1_real_price

                token1_for_token2_pool_price = await dex.get_token1_for_token2_price(token1, token2, token1_val, self.account)
                
                token2_max_val = amount_to_add/token2_real_price
                token2_pool_val = token1_val/token1_for_token2_pool_price

                assert 1-MAX_PRICE_IMPACT <= (1-SLIPPAGE) * token2_pool_val /token2_max_val, "price impact too high"

                logger.info(f"[{self.account.stark_address}] going to add liquidity in {dex.name} in {token1.symbol}/{token2.symbol} pair for {token1_val} {token1.symbol} and {token2_pool_val} {token2.symbol}")
                
                if token2_usd_value < amount_to_add*(1+MAX_PRICE_IMPACT+0.01):
                    logger.info(f"[{self.account.stark_address}] not enough second token for adding, will make swap")
                    
                    amount_to_swap = amount_to_add*(1+MAX_PRICE_IMPACT+0.01) - token2_usd_value
                    token1_amount_to_swap = amount_to_swap/await token1.get_price()
                    amount_out = token1_amount_to_swap/token1_for_token2_pool_price
                    
                    logger.info(f"[{self.account.stark_address}] going to swap {token1_amount_to_swap} {token1.symbol} for {token2.symbol} in {dex.name}")
                    
                    swap_txn = await dex.create_txn_for_swap(token1_amount_to_swap, token1, amount_out, token2, self.account)

                    if swap_txn == -1:
                        logger.error(f"[{self.account.stark_address}] can't create txn for swap")
                        await sleeping(self.account.stark_address, True)
                        continue

                    if (await self.account.send_txn_starknet(swap_txn))[0] != 1:
                        continue
                    await sleeping(self.account.stark_address)
                liq_txn = await dex.create_txn_for_liq(token1_val, token1, token2_pool_val, token2, self.account)
                if liq_txn == -1:
                    await sleeping(self.account.stark_address, True)
                    continue

                await self.account.send_txn_starknet(liq_txn)
                await sleeping(self.account.stark_address)

            except Exception as e:
                logger.error(f"[{self.account.stark_address}] got erroor: {e}")
                await sleeping(self.account.stark_address, True)

    async def remove_liq(self):
        dexes = supported_dexes_for_liq.copy()
        shuffle(dexes)
        for dex in dexes:
            dex: BaseDEX
            lptokens = dex.lpts.copy()
            shuffle(lptokens)
            for lpt in lptokens:
                lpt: StarkToken
                balance = (await self.account.get_balance_starknet(lpt))[0]

                if balance <= 0:
                    logger.info(f"[{self.account.stark_address}] {lpt.symbol} pool value is 0. Skip")
                    continue

                txn = await dex.create_txn_for_remove_liq(lpt, self.account)

                if txn == -1:
                    continue
                logger.info(f"[{self.account.stark_address}] going to remove {lpt.symbol} in {dex.name}")
                await self.account.send_txn_starknet(txn)
                await sleeping(self.account.stark_address)

    
    
    