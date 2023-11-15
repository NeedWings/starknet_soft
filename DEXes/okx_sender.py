from ..BaseClasses import *


class Sender():
    async def create_txn(self, eth: Token, okx_starknet_address: str, sender: StarkAccount, WithdrawSaving=None):
        contract = Contract(eth.contract_address, STARK_TOKEN_ABI, sender.stark_native_account)
        balance = await sender.get_balance() - get_random_value(WithdrawSaving if WithdrawSaving else SETTINGS["WithdrawSaving"])*1e18
        if balance <=0:
            return -1, 'Balance is lower than minBalance for saving'
        call = contract.functions["transfer"].prepare(
            int(okx_starknet_address, 16),
            int(balance)
        )

        return 0, [call]