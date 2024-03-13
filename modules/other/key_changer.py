from random import choice

from starknet_py.contract import Contract
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.hash.utils import message_signature, compute_hash_on_elements
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.models import StarknetChainId 

from modules.base_classes.base_account import BaseAccount
from modules.utils.token import StarkToken
from modules.utils.utils import handle_dangerous_request

class KeyChanger:
    ABI = [{"name": "change_owner","type": "function","inputs": [{"name": "new_owner","type": "core::felt252"},{"name": "signature_r","type": "core::felt252"},{"name": "signature_s","type": "core::felt252"}],"outputs": [],"state_mutability": "external"}]
    
    async def create_txn_for_changing_key(self, new_key: int, sender: BaseAccount):
        print(1)
        new_key_pair = KeyPair.from_private_key(new_key)
        print(2)

        msg = compute_hash_on_elements(
            [
                get_selector_from_name("change_owner"),
                StarknetChainId.MAINNET,
                sender.stark_native_account.address,
                sender.stark_native_account.signer.public_key
            ]
        )
        print(3)
        r, s = message_signature(msg, new_key)
        print(4)
        contract = Contract(sender.stark_native_account.address, self.ABI, sender.stark_native_account, cairo_version=1)
        print(5)
        call = contract.functions["change_owner"].prepare_call(
                new_key_pair.public_key,
                r,
                s
        )
        print(6)
        return [call]
    
key_changer = KeyChanger()
