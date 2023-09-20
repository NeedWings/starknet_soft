from BaseClasses import *

class DmailHandler:
    async def create_txn_for_dmail(self, sender:StarkAccount):
        l = "1234567890abcdef"
        t = [random.choice(l) for i in range(32)]
        text = ""
        for i in t:
            text += i
            
        addr_raw = [random.choice(l) for i in range(32)]
        addr = ""
        for i in addr_raw:
            addr += i
        
        felt_text = int(text, 16)
        felt_rec = int(addr, 16)
        logger.info(f"[{sender.formatted_hex_address}] going to send message({text}) to {addr}")

        dmail_contract = Contract(0x0454f0bd015e730e5adbb4f080b075fdbf55654ff41ee336203aa2e1ac4d4309, DMAIL, sender.stark_native_account)

        call = dmail_contract.functions["transaction"].prepare(
                felt_rec,
                felt_text
            )
        return [call]
    
dmail_hand = DmailHandler()