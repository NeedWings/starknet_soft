"""
NOT USED
TODO: change to common domain
"""
from random import choice, randint

from starknet_py.contract import Contract

from modules.base_classes.base_account import BaseAccount, StarkNativeAccount
from modules.utils.logger import logger
from modules.utils.token import StarkToken
from modules.utils.utils import handle_dangerous_request, get_random_value_int
from modules.config import SETTINGS_PATH

lets = "abcdefghijklmnopqrstuvwxyz0123456789-"
o = len(lets) + 1
c = len(lets)
s = "这来"
d = len(s)
def buff(e: str):
    t = 0
    r = 1
    if e == "":
        return t

    for n in range(len(e)):
        a = e[n]
        try:
            f = lets.index(a)
            u = lets.index(a)
        except:
            f = -1
            u = -1
        try:
            if -1 != f:
                if n == len(e) - 1 and e[n] == lets[0]:
                    t += r * c
                    r *= o * o
                else:
                    t += r * u
                    r *= o
            elif -1 != s.index(a):
                t += r*c
                r *= o
                if n == len(e) - 1:
                    i = 1 + s.index(a)
                else:
                    i = 0 + s.index(a)
                t += r * i
                r *= d
        except:
            pass
    return t


class StarkId:
    abi1 = [{"name":"mint","type":"function","inputs":[{"name":"starknet_id","type":"felt"}],"outputs":[]}]
    contract_address1 = 0x05dbdedc203e92749e2e746e2d40a768d966bd243df04a6b712e222bc040a9af 
   
    abi3 = [{"name":"DomainData","size":6,"type":"struct","members":[{"name":"owner","type":"felt","offset":0},{"name":"resolver","type":"felt","offset":1},{"name":"address","type":"felt","offset":2},{"name":"expiry","type":"felt","offset":3},{"name":"key","type":"felt","offset":4},{"name":"parent_key","type":"felt","offset":5}]},{"name":"Uint256","size":2,"type":"struct","members":[{"name":"low","type":"felt","offset":0},{"name":"high","type":"felt","offset":1}]},{"name":"Discount","size":7,"type":"struct","members":[{"name":"domain_len_range","type":"(felt, felt)","offset":0},{"name":"days_range","type":"(felt, felt)","offset":2},{"name":"timestamp_range","type":"(felt, felt)","offset":4},{"name":"amount","type":"felt","offset":6}]},{"data":[{"name":"implementation","type":"felt"}],"keys":[],"name":"Upgraded","type":"event"},{"data":[{"name":"previousAdmin","type":"felt"},{"name":"newAdmin","type":"felt"}],"keys":[],"name":"AdminChanged","type":"event"},{"data":[{"name":"domain_len","type":"felt"},{"name":"domain","type":"felt*"},{"name":"address","type":"felt"}],"keys":[],"name":"domain_to_addr_update","type":"event"},{"data":[{"name":"domain_len","type":"felt"},{"name":"domain","type":"felt*"},{"name":"resolver","type":"felt"}],"keys":[],"name":"domain_to_resolver_update","type":"event"},{"data":[{"name":"address","type":"felt"},{"name":"domain_len","type":"felt"},{"name":"domain","type":"felt*"}],"keys":[],"name":"addr_to_domain_update","type":"event"},{"data":[{"name":"domain_len","type":"felt"},{"name":"domain","type":"felt*"},{"name":"prev_owner","type":"felt"},{"name":"new_owner","type":"felt"}],"keys":[],"name":"domain_transfer","type":"event"},{"data":[{"name":"domain_len","type":"felt"},{"name":"domain","type":"felt*"},{"name":"owner","type":"felt"},{"name":"expiry","type":"felt"}],"keys":[],"name":"starknet_id_update","type":"event"},{"data":[{"name":"domain_len","type":"felt"},{"name":"domain","type":"felt*"}],"keys":[],"name":"reset_subdomains_update","type":"event"},{"data":[{"name":"domain","type":"felt"},{"name":"metadata","type":"felt"}],"keys":[],"name":"SaleMetadata","type":"event"},{"name":"initializer","type":"function","inputs":[{"name":"starknetid_contract_addr","type":"felt"},{"name":"pricing_contract_addr","type":"felt"},{"name":"admin","type":"felt"},{"name":"l1_contract","type":"felt"}],"outputs":[]},{"name":"domain_to_address","type":"function","inputs":[{"name":"domain_len","type":"felt"},{"name":"domain","type":"felt*"}],"outputs":[{"name":"address","type":"felt"}],"stateMutability":"view"},{"name":"domain_to_expiry","type":"function","inputs":[{"name":"domain_len","type":"felt"},{"name":"domain","type":"felt*"}],"outputs":[{"name":"expiry","type":"felt"}],"stateMutability":"view"},{"name":"domain_to_data","type":"function","inputs":[{"name":"domain_len","type":"felt"},{"name":"domain","type":"felt*"}],"outputs":[{"name":"data","type":"DomainData"}],"stateMutability":"view"},{"name":"address_to_domain","type":"function","inputs":[{"name":"address","type":"felt"}],"outputs":[{"name":"domain_len","type":"felt"},{"name":"domain","type":"felt*"}],"stateMutability":"view"},{"name":"domain_to_token_id","type":"function","inputs":[{"name":"domain_len","type":"felt"},{"name":"domain","type":"felt*"}],"outputs":[{"name":"owner","type":"felt"}],"stateMutability":"view"},{"name":"set_domain_to_address","type":"function","inputs":[{"name":"domain_len","type":"felt"},{"name":"domain","type":"felt*"},{"name":"address","type":"felt"}],"outputs":[]},{"name":"set_domain_to_resolver","type":"function","inputs":[{"name":"domain_len","type":"felt"},{"name":"domain","type":"felt*"},{"name":"resolver","type":"felt"}],"outputs":[]},{"name":"set_address_to_domain","type":"function","inputs":[{"name":"domain_len","type":"felt"},{"name":"domain","type":"felt*"}],"outputs":[]},{"name":"book_domain","type":"function","inputs":[{"name":"domain_hash","type":"felt"}],"outputs":[]},{"name":"buy","type":"function","inputs":[{"name":"token_id","type":"felt"},{"name":"domain","type":"felt"},{"name":"days","type":"felt"},{"name":"resolver","type":"felt"},{"name":"address","type":"felt"},{"name":"sponsor","type":"felt"},{"name":"metadata","type":"felt"}],"outputs":[]},{"name":"buy_discounted","type":"function","inputs":[{"name":"token_id","type":"felt"},{"name":"domain","type":"felt"},{"name":"days","type":"felt"},{"name":"resolver","type":"felt"},{"name":"address","type":"felt"},{"name":"discount_id","type":"felt"},{"name":"metadata","type":"felt"}],"outputs":[]},{"name":"renew","type":"function","inputs":[{"name":"domain","type":"felt"},{"name":"days","type":"felt"},{"name":"sponsor","type":"felt"},{"name":"discount_id","type":"felt"},{"name":"metadata","type":"felt"}],"outputs":[]},{"name":"transfer_domain","type":"function","inputs":[{"name":"domain_len","type":"felt"},{"name":"domain","type":"felt*"},{"name":"target_token_id","type":"felt"}],"outputs":[]},{"name":"reset_subdomains","type":"function","inputs":[{"name":"domain_len","type":"felt"},{"name":"domain","type":"felt*"}],"outputs":[]},{"name":"set_admin","type":"function","inputs":[{"name":"address","type":"felt"}],"outputs":[]},{"name":"set_domain_owner","type":"function","inputs":[{"name":"domain_len","type":"felt"},{"name":"domain","type":"felt*"},{"name":"token_id","type":"felt"}],"outputs":[]},{"name":"set_pricing_contract","type":"function","inputs":[{"name":"address","type":"felt"}],"outputs":[]},{"name":"transfer_balance","type":"function","inputs":[{"name":"erc20","type":"felt"},{"name":"amount","type":"Uint256"}],"outputs":[]},{"name":"write_discount","type":"function","inputs":[{"name":"discount_id","type":"felt"},{"name":"discount","type":"Discount"}],"outputs":[]},{"name":"set_l1_contract","type":"function","inputs":[{"name":"l1_contract","type":"felt"}],"outputs":[]},{"name":"set_referral_contract","type":"function","inputs":[{"name":"address","type":"felt"}],"outputs":[]},{"name":"upgrade","type":"function","inputs":[{"name":"new_implementation","type":"felt"}],"outputs":[]}]
    contract_address3 = 0x06ac597f8116f886fa1c97a23fa4e08299975ecaf6b598873ca6792b9bbfb678 

    def encode_domain(self, domain: str):
        if domain == "":
            return [0]
        
        t = []

        for e in domain.replace(".stark", "").split("."):
            t.append(buff(e))
        return t
            
    async def has_domain(self, sender: StarkNativeAccount):
        contract = Contract(self.contract_address3, self.abi3, sender)
        has = len((await handle_dangerous_request(
            contract.functions["address_to_domain"].call, 
            "Can't get domain, trying again", 
            "0x"+ (66-len(hex(sender.address)))*"0" + hex(sender.address)[2::], 
            sender.address)).domain)
        if has == 0:
            return False
        else:
            return True



    async def create_txn(self, eth: StarkToken, sender: BaseAccount):
        
                
        domain = ""
        with open(f"{SETTINGS_PATH}wordlist.txt", "r") as f:
            words = f.read().lower().split("\n")

        wl = get_random_value_int([1,3])
        for i in range(wl):
            domain += choice(words)
        while len(domain) < 5:
            domain += choice(words)
        
        logger.info(f"[{sender.stark_address}] going to mint domain({domain})")
        list_domain = self.encode_domain(domain)
        int_domain = ""
        for i in list_domain:
            int_domain += str(i)
        int_domain = int(int_domain)
        contract1 = Contract(self.contract_address1, self.abi1, sender.stark_native_account)
        
        contract3 = Contract(self.contract_address3, self.abi3, sender.stark_native_account)
        id = randint(0, 1e12)
        сall1 = contract1.functions["mint"].prepare(
                id
            )
        call2 = eth.get_approve_call_wei(get_random_value_int([599178082191783, 699178082191783]), 0x6ac597f8116f886fa1c97a23fa4e08299975ecaf6b598873ca6792b9bbfb678, sender)
        call3 = contract3.functions["buy_discounted"].prepare(
            id,
            int_domain,
            81,
            0,
            sender.stark_native_account.address,
            1,
            randint(0, 3618502788666131213697322783095070105623107215331596699973092056135872020481)
        )
        call4 = contract3.functions["set_address_to_domain"].prepare(
            list_domain
        )

        return [сall1, call2, call3, call4]
        