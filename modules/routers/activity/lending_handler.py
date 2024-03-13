from random import choice, shuffle

from starknet_py.contract import Contract

from modules.lends.zklend import ZkLend
from modules.config import SETTINGS, SLIPPAGE, MAX_PRICE_IMPACT
from modules.base_classes.base_account import BaseAccount
from modules.base_classes.base_defi import BaseLend
from modules.utils.token import StarkToken
from modules.utils.token_storage import tokens, tokens_dict
from modules.utils.logger import logger
from modules.utils.utils import get_random_value, get_random_value_int, sleeping
from modules.utils.token_checker import token_checker
from modules.utils.token_storage import eth

zklend = ZkLend()
lends = [zklend]

supported_lends = []

for name in SETTINGS["Lends"]:
    for lend in lends:
        if lend.name == name:
            supported_lends.append(lend)

class LendingHandler:
    def __init__(self, account: BaseAccount) -> None:
        self.account = account

    def supported_tokens_str_to_token(self, tokens):
        res = []
        for token in tokens:
            res.append(tokens_dict[token])

        return res
    
    async def collateral(self):
        for i in range(get_random_value_int(SETTINGS["zklend_collateral_amount"])):
            lend_contract = Contract(ZkLend().contract_address, zklend.ABI, self.account.stark_native_account)
            call3 = lend_contract.functions["enable_collateral"].prepare_call(
                    eth.contract_address
                )
            calldata = [call3]
            logger.info(f"[{self.account.stark_address}] enabling collateral")
            await self.account.send_txn_starknet(calldata)
            await sleeping(self.account.stark_address)
            call3 = lend_contract.functions["disable_collateral"].prepare_call(
                    eth.contract_address
                )
            calldata = [call3]
            logger.info(f"[{self.account.stark_address}] disabling collateral")
            await self.account.send_txn_starknet(calldata)
            await sleeping(self.account.stark_address)


    async def lend_actions(self):
        add_amount = get_random_value_int(SETTINGS["AddLendAmount"])

        for i in range(add_amount):
            try:
                lend: BaseLend = choice(supported_lends)
                token, usd_value = await token_checker.get_max_valued_token(self.account, self.supported_tokens_str_to_token(lend.supported_tokens))
                assert token is not None, "all balances are 0"

                token: StarkToken

                amount_to_add = usd_value * get_random_value(SETTINGS["LendWorkPercent"])
                amount_to_add_in_token = amount_to_add/await token.get_price()
                
                logger.info(f"[{self.account.stark_address}] going to add {amount_to_add_in_token} {token.symbol} in {lend.name}")

                txn = await lend.create_txn_for_adding_token(token, amount_to_add_in_token, self.account)

                await self.account.send_txn_starknet(txn)

                await sleeping(self.account.stark_address)
            except Exception as e:
                logger.error(f"[{self.account.stark_address}] got erroor: {e}")
                await sleeping(self.account.stark_address, True)

        borrow_return_amount = get_random_value_int(SETTINGS["BorrowAddAmount"])
        for i in range(borrow_return_amount):
            try:
                lend: BaseLend = choice(supported_lends)
                token = choice(self.supported_tokens_str_to_token(lend.supported_tokens))

                
                total_borroved = await lend.get_total_borrowed(self.account)
                total_supplied = await lend.get_total_supplied(self.account)
                usd_val = total_supplied-total_borroved

                
                to_borrow_usd = (usd_val)*get_random_value(SETTINGS["BorrowWorkPercent"])*lend.coeffs_for_borrow[token.symbol]
                assert to_borrow_usd != 0, "to borrow is zero"
                
                amount = to_borrow_usd/await token.get_price()
                logger.info(f"[{self.account.stark_address}] going to borrow {amount} {token.symbol} in {lend.name}")

                txn = await lend.create_txn_for_borrow(amount, token, self.account)

                if (await self.account.send_txn_starknet(txn))[0] != 1:
                    continue

                await sleeping(self.account.stark_address)
                logger.info(f"[{self.account.stark_address}] going to return {amount} {token.symbol} in {lend.name}")
                txn = await lend.create_txn_for_return(token, self.account)

                await self.account.send_txn_starknet(txn)

                await sleeping(self.account.stark_address)

            except Exception as e:
                logger.error(f"[{self.account.stark_address}] got erroor: {e}")
                await sleeping(self.account.stark_address, True)

    async def remove_from_lend(self):
        lends = supported_lends.copy()
        shuffle(lends)
        for lend in lends:
            lend: BaseLend
            lend_tokens = lend.lend_tokens.copy()
            shuffle(lend_tokens)
            for token in lend_tokens:
                token: StarkToken
                balance = (await self.account.get_balance_starknet(token))[0]
                balance = int(balance)

                if balance <= 0:
                    logger.info(f"[{self.account.stark_address}] Supplied {token.symbol} is 0. Skip")
                    continue

                logger.info(f"[{self.account.stark_address}] going to return {token.symbol} from {lend.name}")
                txn = await lend.create_txn_for_removing_token(balance, token, self.account)
                if txn == -1:
                    logger.info(f"[{self.account.stark_address}] not enough repayed for removing. Skip")
                    continue
                await self.account.send_txn_starknet(txn)

                await sleeping(self.account.stark_address)

    async def return_borrowed(self):
        for lend in lends:
            tokens = self.supported_tokens_str_to_token(lend.supported_tokens).copy()
            shuffle(tokens)
            for token in tokens:
                try:
                    txn = await lend.create_txn_for_return(token, self.account)
                    if txn == -1:
                        logger.info(f"[{self.account.stark_address}] borrowed {token.symbol} is 0. Skip")
                        continue
                    logger.info(f"[{self.account.stark_address}] going to return borroved {token.symbol}")
                    await self.account.send_txn_starknet(txn)

                    await sleeping(self.account.stark_address)

                except Exception as e:
                    logger.error(f"[{self.account.stark_address}] got erroor: {e}")
                    await sleeping(self.account.stark_address, True)