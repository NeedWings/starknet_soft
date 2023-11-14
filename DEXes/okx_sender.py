from ..BaseClasses import *


class Sender():
    

    async def create_txn(self, eth: Token, rec: str, sender: StarkAccount):
        
        contract = Contract(eth.contract_address, STARK_TOKEN_ABI, sender.stark_native_account)
        balance = await sender.get_balance() - get_random_value(SETTINGS["WithdrawSaving"])*1e18
        if balance <=0:
            return -1
        call = contract.functions["transfer"].prepare(
            int(rec, 16),
            int(balance)
        )

        return [call]