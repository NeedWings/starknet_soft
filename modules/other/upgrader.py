from random import randint

from starknet_py.contract import Contract

from modules.base_classes.base_account import BaseAccount
from modules.config import SETTINGS

UPGRADE_ARGENT = [{"name": "upgrade","type": "function","inputs": [{"name": "new_implementation","type": "felt"},{"name": "calldata","type": "felt*"}],"outputs":[]}]
BRAAVOS_UPGRADE = [{"name":"upgrade","type":"function","inputs":[{"name":"new_implementation","type":"felt"}],"outputs":[]}]

class Upgrader:

    async def upgrade_argent(self, sender: BaseAccount):
        new_impl = int(SETTINGS["new_implementation_for_upgrade"], 16)

        contract = Contract(sender.stark_native_account.address, UPGRADE_ARGENT, sender.stark_native_account, cairo_version=await sender.stark_native_account.cairo_version)
        
        call = contract.functions["upgrade"].prepare(
                new_impl,
                [0]
        )

        calldata = [call]

        return calldata
    
    async def upgrade_braavos(self, sender: BaseAccount):
        new_impl = int(SETTINGS["new_implementation_for_upgrade"], 16)

        contract = Contract(sender.stark_native_account.address, BRAAVOS_UPGRADE, sender.stark_native_account, cairo_version=await sender.stark_native_account.cairo_version)
        
        call = contract.functions["upgrade"].prepare(
                new_impl
        )

        calldata = [call]

        return calldata

upgrader = Upgrader()