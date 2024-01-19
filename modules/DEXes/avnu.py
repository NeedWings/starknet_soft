from starknet_py.contract import Contract
from starknet_py.net.client_models import Call
from starknet_py.hash.selector import get_selector_from_name

from modules.DEXes.myswap import MySwap, BaseDEX
from modules.utils.utils import req, req_post, get_random_value, handle_dangerous_request
from modules.config import SETTINGS, SLIPPAGE
from modules.utils.token import StarkToken
from modules.utils.logger import logger
from modules.base_classes.base_account import BaseAccount
from modules.utils.token_storage import tokens_from_contracts

class Avnu(BaseDEX):
    name = "Avnu"
    ABI = [{"name":"ExchangeLocker","type":"impl","interface_name":"avnu::interfaces::locker::ILocker"},{"name":"avnu::interfaces::locker::ILocker","type":"interface","items":[{"name":"locked","type":"function","inputs":[{"name":"id","type":"core::integer::u32"},{"name":"data","type":"core::array::Array::<core::felt252>"}],"outputs":[{"type":"core::array::Array::<core::felt252>"}],"state_mutability":"external"}]},{"name":"Exchange","type":"impl","interface_name":"avnu::exchange::IExchange"},{"name":"core::integer::u256","type":"struct","members":[{"name":"low","type":"core::integer::u128"},{"name":"high","type":"core::integer::u128"}]},{"name":"avnu::models::Route","type":"struct","members":[{"name":"token_from","type":"core::starknet::contract_address::ContractAddress"},{"name":"token_to","type":"core::starknet::contract_address::ContractAddress"},{"name":"exchange_address","type":"core::starknet::contract_address::ContractAddress"},{"name":"percent","type":"core::integer::u128"},{"name":"additional_swap_params","type":"core::array::Array::<core::felt252>"}]},{"name":"core::bool","type":"enum","variants":[{"name":"False","type":"()"},{"name":"True","type":"()"}]},{"name":"avnu::exchange::IExchange","type":"interface","items":[{"name":"get_adapter_class_hash","type":"function","inputs":[{"name":"exchange_address","type":"core::starknet::contract_address::ContractAddress"}],"outputs":[{"type":"core::starknet::class_hash::ClassHash"}],"state_mutability":"view"},{"name":"get_fee_collector_address","type":"function","inputs":[],"outputs":[{"type":"core::starknet::contract_address::ContractAddress"}],"state_mutability":"view"},{"name":"get_owner","type":"function","inputs":[],"outputs":[{"type":"core::starknet::contract_address::ContractAddress"}],"state_mutability":"view"},{"name":"multi_route_swap","type":"function","inputs":[{"name":"token_from_address","type":"core::starknet::contract_address::ContractAddress"},{"name":"token_from_amount","type":"core::integer::u256"},{"name":"token_to_address","type":"core::starknet::contract_address::ContractAddress"},{"name":"token_to_amount","type":"core::integer::u256"},{"name":"token_to_min_amount","type":"core::integer::u256"},{"name":"beneficiary","type":"core::starknet::contract_address::ContractAddress"},{"name":"integrator_fee_amount_bps","type":"core::integer::u128"},{"name":"integrator_fee_recipient","type":"core::starknet::contract_address::ContractAddress"},{"name":"routes","type":"core::array::Array::<avnu::models::Route>"}],"outputs":[{"type":"core::bool"}],"state_mutability":"external"},{"name":"set_adapter_class_hash","type":"function","inputs":[{"name":"exchange_address","type":"core::starknet::contract_address::ContractAddress"},{"name":"adapter_class_hash","type":"core::starknet::class_hash::ClassHash"}],"outputs":[{"type":"core::bool"}],"state_mutability":"external"},{"name":"set_fee_collector_address","type":"function","inputs":[{"name":"new_fee_collector_address","type":"core::starknet::contract_address::ContractAddress"}],"outputs":[{"type":"core::bool"}],"state_mutability":"external"},{"name":"transfer_ownership","type":"function","inputs":[{"name":"new_owner","type":"core::starknet::contract_address::ContractAddress"}],"outputs":[{"type":"core::bool"}],"state_mutability":"external"},{"name":"upgrade_class","type":"function","inputs":[{"name":"new_class_hash","type":"core::starknet::class_hash::ClassHash"}],"outputs":[{"type":"core::bool"}],"state_mutability":"external"}]},{"name":"constructor","type":"constructor","inputs":[{"name":"owner","type":"core::starknet::contract_address::ContractAddress"},{"name":"fee_collector_address","type":"core::starknet::contract_address::ContractAddress"}]},{"kind":"struct","name":"avnu::exchange::Exchange::Swap","type":"event","members":[{"kind":"data","name":"taker_address","type":"core::starknet::contract_address::ContractAddress"},{"kind":"data","name":"sell_address","type":"core::starknet::contract_address::ContractAddress"},{"kind":"data","name":"sell_amount","type":"core::integer::u256"},{"kind":"data","name":"buy_address","type":"core::starknet::contract_address::ContractAddress"},{"kind":"data","name":"buy_amount","type":"core::integer::u256"},{"kind":"data","name":"beneficiary","type":"core::starknet::contract_address::ContractAddress"}]},{"kind":"struct","name":"avnu::exchange::Exchange::OwnershipTransferred","type":"event","members":[{"kind":"data","name":"previous_owner","type":"core::starknet::contract_address::ContractAddress"},{"kind":"data","name":"new_owner","type":"core::starknet::contract_address::ContractAddress"}]},{"kind":"enum","name":"avnu::exchange::Exchange::Event","type":"event","variants":[{"kind":"nested","name":"Swap","type":"avnu::exchange::Exchange::Swap"},{"kind":"nested","name":"OwnershipTransferred","type":"avnu::exchange::Exchange::OwnershipTransferred"}]}]
    contract_address = 0x04270219d365d6b017231b52e92b3fb5d7c8378b05e9abc97724537a80e93b0f
    supported_tokens = ["ETH", "USDT", "USDC", "DAI", "WBTC", "LORDS", "WSTETH"]
    
    lpts = []
    
    tokens_from_lpt = {}
    
    
    async def get_token1_for_token2_price(self, token1: StarkToken, token2: StarkToken, amount_in: float, sender: BaseAccount):

        _, amount_out_avnu = await handle_dangerous_request(
            self.get_quotes, 
            "Can't get pool info: ", 
            sender.stark_address, 
            token1,
            token2, 
            amount_in, 
            sender
            )
        
        return amount_in/(amount_out_avnu/10**token2.decimals)

            
    async def get_quotes(self, token1, token2, amount_in, sender):
        resp = await req(f"https://starknet.api.avnu.fi/swap/v1/quotes?sellTokenAddress={hex(token1.contract_address)}&buyTokenAddress={hex(token2.contract_address)}&sellAmount={hex(int(amount_in*10**token1.decimals))}&takerAddress={hex(sender.stark_native_account.address)}&size=3&integratorName=AVNU%20Portal")

        return resp[0]["quoteId"], int(resp[0]["buyAmount"], 16)
    
    async def build_transaction(self, quote_id: str, sender: BaseAccount):

        data = {
            "quoteId": quote_id,
            "takerAddress": sender.stark_address,
            "slippage": SLIPPAGE,
        }

        resp = await req_post("https://starknet.api.avnu.fi/swap/v1/build", json=data)

        return resp


    def __init__(self) -> None:
        new_supported_tokens = []
        for token in self.supported_tokens:
            if token in SETTINGS["Supported_tokens"]:
                new_supported_tokens.append(token)
        self.supported_tokens = new_supported_tokens

    
    async def create_txn_for_swap(self, amount_in: float, token1: StarkToken, amount_out: float, token2: StarkToken, sender: BaseAccount, full: bool = False):
        
        
        if not full:
            quote, amount_out_avnu = await handle_dangerous_request(self.get_quotes, "Can't get best dex for avnu: ", sender.stark_address, token1, token2, amount_in, sender)
            if amount_out_avnu < (1-SLIPPAGE)*amount_out*10**token2.decimals:
                logger.error(f"[{sender.stark_address}] AVNU MIN VALUE TOO LOW. SKIP")
                return -1
            amount_out = amount_out_avnu
            call1 = token1.get_approve_call(amount_in, self.contract_address, sender)
            contract = Contract(self.contract_address, self.ABI, sender.stark_native_account, cairo_version=1)
            txn_data = await self.build_transaction(quote, sender)
            calldata = list(map(lambda x: int(x, 16), txn_data["calldata"]))
            call2 =  Call(
                to_addr=self.contract_address,
                selector=get_selector_from_name(txn_data["entrypoint"]),
                calldata=calldata,
            ) 

            
        else:
            bal = (await sender.get_balance_starknet(token1))[0] - 20
            
            if token1.symbol == "ETH":
                bal -= int(get_random_value(SETTINGS["SaveEthOnBalance"])*1e18)
        
            quote, amount_out_avnu = await handle_dangerous_request(
                self.get_quotes, "Can't get best dex for avnu: ", 
                sender.stark_address, 
                token1, 
                token2, 
                bal/10**token1.decimals, 
                sender
            
            )
            if amount_out_avnu < (1-SLIPPAGE)*amount_out*10**token2.decimals:
                logger.error(f"[{sender.stark_address}] AVNU MIN VALUE TOO LOW. SKIP")
                return -1
            amount_out = amount_out_avnu
            call1 = token1.get_approve_call_wei(bal, self.contract_address, sender)
            contract = Contract(self.contract_address, self.ABI, sender.stark_native_account, cairo_version=1)
            txn_data = await self.build_transaction(quote, sender)
            calldata = list(map(lambda x: int(x, 16), txn_data["calldata"]))
            
            call2 =  Call(
                to_addr=self.contract_address,
                selector=get_selector_from_name(txn_data["entrypoint"]),
                calldata=calldata,
            ) 


        return [call1, call2]

    async def create_txn_for_liq(self, amount1: float, token1: StarkToken, amount2: float, token2: StarkToken, sender: BaseAccount):
        return -1


    async def create_txn_for_remove_liq(self, lptoken: StarkToken, sender: BaseAccount):
        return -1