from random import randint

from starknet_py.contract import Contract

from modules.base_classes.base_account import BaseAccount
from modules.config import SETTINGS

UPGRADE_ARGENT = [{"name": "upgrade","type": "function","inputs": [{"name": "new_implementation","type": "felt"},{"name": "calldata","type": "felt*"}],"outputs":[]}]
BRAAVOS_UPGRADE = [{"name":"upgrade_regenesis","type":"function","inputs":[{"name":"new_implementation","type":"felt"}, {"name":"regenesis_account_id","type":"felt"}],"outputs":[]}]

class Upgrader:

    async def upgrade_argent(self, sender: BaseAccount):
        new_impl = int(SETTINGS["new_implementation_for_upgrade"], 16)

        contract = Contract(sender.stark_native_account.address, UPGRADE_ARGENT, sender.stark_native_account, cairo_version=await sender.stark_native_account.cairo_version)
        
        call = contract.functions["upgrade"].prepare_call(
                new_impl,
                [0]
        )

        calldata = [call]

        return calldata
    
    async def upgrade_braavos(self, sender: BaseAccount):

        contract = Contract(sender.stark_native_account.address, BRAAVOS_UPGRADE, sender.stark_native_account, cairo_version=await sender.stark_native_account.cairo_version)
        
        call = contract.functions["upgrade_regenesis"].prepare_call(
                0x816dd0297efc55dc1e7559020a3a825e81ef734b558f03c83325d4da7e6253,
                0x2ceccef7f994940b3962a6c67e0ba4fcd37df7d131417c604f91e03caecc1cd
        )

        calldata = [call]

        return calldata

upgrader = Upgrader()