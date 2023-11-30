from random import choice

from starknet_py.contract import Contract

from modules.base_classes.base_account import BaseAccount
from modules.utils.logger import logger
from modules.utils.utils import str_to_felt

DMAIL_ABI = [{"data":[{"name":"from_address","type":"felt"},{"name":"to","type":"felt"},{"name":"theme","type":"felt"}],"keys":[],"name":"send","type":"event"},{"name":"transaction","type":"function","inputs":[{"name":"to","type":"felt"},{"name":"theme","type":"felt"}],"outputs":[]}]


class DmailHandler:
    async def create_txn_for_dmail(self, sender: BaseAccount):
        l = "1234567890abcdef"
        t = [choice(l) for i in range(31)]
        text = ""
        for i in t:
            text += i
            
        addr_raw = [choice(l) for i in range(31)]
        addr = ""
        for i in addr_raw:
            addr += i
        
        felt_text = str_to_felt(text)
        felt_rec = str_to_felt(addr)
        logger.info(f"[{sender.stark_address}] going to send message({text}) to {addr}")

        dmail_contract = Contract(0x0454f0bd015e730e5adbb4f080b075fdbf55654ff41ee336203aa2e1ac4d4309, DMAIL_ABI, sender.stark_native_account)

        call = dmail_contract.functions["transaction"].prepare(
                felt_rec,
                felt_text
            )
        return [call]
    
dmail_hand = DmailHandler()