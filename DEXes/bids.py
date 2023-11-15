from ..BaseClasses import *

class Bidder:
    async def create_bid_tx(self, eth, account, flex):
        match flex:
            case 1:
                creator = self.create_txn_for_flex
            case 2:
                creator = self.create_txn_for_unframed
            case 3:
                creator = self.create_txn_for_element
            case _:
                return -1, 'Unknown flex'
        return creator(eth, account)

    async def create_txn_for_unframed(self, eth: Token, sender: StarkAccount):
        logger.info(f"[{sender.formatted_hex_address}] going to bid on unframed")
        contract = Contract(eth.contract_address, STARK_TOKEN_ABI, sender.stark_native_account)
        val = random.randint(1000000000000, 100000000000000)
        val = int(int(val/10000)*10000)
        call = contract.functions["increaseAllowance"].prepare(
            0x51734077ba7baf5765896c56ce10b389d80cdcee8622e23c0556fb49e82df1b,
            val
        )

        return [call]
    
    async def create_txn_for_flex(self, eth: Token, sender: StarkAccount):
        logger.info(f"[{sender.formatted_hex_address}] going to bid on flexing")
        contract = Contract(eth.contract_address, STARK_TOKEN_ABI, sender.stark_native_account)
        val = random.randint(1000000000000, 100000000000000)
        val = int(int(val/10000)*10000)
        call = contract.functions["approve"].prepare(
            0x4b1b3fdf34d00288a7956e6342fb366a1510a9387d321c87f3301d990ac19d4,
            val
        )

        return [call]
    
    async def create_txn_for_element(self, eth: Token, sender: StarkAccount):
        logger.info(f"[{sender.formatted_hex_address}] going to bid on element")
        contract = Contract(eth.contract_address, STARK_TOKEN_ABI, sender.stark_native_account)
        val = random.randint(1000000000000, 100000000000000)
        val = int(int(val/10000)*10000)
        call = contract.functions["approve"].prepare(
            0x1dd1cc15dfa8da7e75e9f4f4e7417f84992f216d50631ad9a7d3530ac9e3821,
            val
        )

        return [call]
    
bidder = Bidder()