from ..BaseClasses import *
from .myswap import MySwap

class Avnu(BaseDex):
    name = "Avnu"
    ABI = [{"name":"ExchangeLocker","type":"impl","interface_name":"avnu::interfaces::locker::ILocker"},{"name":"avnu::interfaces::locker::ILocker","type":"interface","items":[{"name":"locked","type":"function","inputs":[{"name":"id","type":"core::integer::u32"},{"name":"data","type":"core::array::Array::<core::felt252>"}],"outputs":[{"type":"core::array::Array::<core::felt252>"}],"state_mutability":"external"}]},{"name":"Exchange","type":"impl","interface_name":"avnu::exchange::IExchange"},{"name":"core::integer::u256","type":"struct","members":[{"name":"low","type":"core::integer::u128"},{"name":"high","type":"core::integer::u128"}]},{"name":"avnu::models::Route","type":"struct","members":[{"name":"token_from","type":"core::starknet::contract_address::ContractAddress"},{"name":"token_to","type":"core::starknet::contract_address::ContractAddress"},{"name":"exchange_address","type":"core::starknet::contract_address::ContractAddress"},{"name":"percent","type":"core::integer::u128"},{"name":"additional_swap_params","type":"core::array::Array::<core::felt252>"}]},{"name":"core::bool","type":"enum","variants":[{"name":"False","type":"()"},{"name":"True","type":"()"}]},{"name":"avnu::exchange::IExchange","type":"interface","items":[{"name":"get_adapter_class_hash","type":"function","inputs":[{"name":"exchange_address","type":"core::starknet::contract_address::ContractAddress"}],"outputs":[{"type":"core::starknet::class_hash::ClassHash"}],"state_mutability":"view"},{"name":"get_fee_collector_address","type":"function","inputs":[],"outputs":[{"type":"core::starknet::contract_address::ContractAddress"}],"state_mutability":"view"},{"name":"get_owner","type":"function","inputs":[],"outputs":[{"type":"core::starknet::contract_address::ContractAddress"}],"state_mutability":"view"},{"name":"multi_route_swap","type":"function","inputs":[{"name":"token_from_address","type":"core::starknet::contract_address::ContractAddress"},{"name":"token_from_amount","type":"core::integer::u256"},{"name":"token_to_address","type":"core::starknet::contract_address::ContractAddress"},{"name":"token_to_amount","type":"core::integer::u256"},{"name":"token_to_min_amount","type":"core::integer::u256"},{"name":"beneficiary","type":"core::starknet::contract_address::ContractAddress"},{"name":"integrator_fee_amount_bps","type":"core::integer::u128"},{"name":"integrator_fee_recipient","type":"core::starknet::contract_address::ContractAddress"},{"name":"routes","type":"core::array::Array::<avnu::models::Route>"}],"outputs":[{"type":"core::bool"}],"state_mutability":"external"},{"name":"set_adapter_class_hash","type":"function","inputs":[{"name":"exchange_address","type":"core::starknet::contract_address::ContractAddress"},{"name":"adapter_class_hash","type":"core::starknet::class_hash::ClassHash"}],"outputs":[{"type":"core::bool"}],"state_mutability":"external"},{"name":"set_fee_collector_address","type":"function","inputs":[{"name":"new_fee_collector_address","type":"core::starknet::contract_address::ContractAddress"}],"outputs":[{"type":"core::bool"}],"state_mutability":"external"},{"name":"transfer_ownership","type":"function","inputs":[{"name":"new_owner","type":"core::starknet::contract_address::ContractAddress"}],"outputs":[{"type":"core::bool"}],"state_mutability":"external"},{"name":"upgrade_class","type":"function","inputs":[{"name":"new_class_hash","type":"core::starknet::class_hash::ClassHash"}],"outputs":[{"type":"core::bool"}],"state_mutability":"external"}]},{"name":"constructor","type":"constructor","inputs":[{"name":"owner","type":"core::starknet::contract_address::ContractAddress"},{"name":"fee_collector_address","type":"core::starknet::contract_address::ContractAddress"}]},{"kind":"struct","name":"avnu::exchange::Exchange::Swap","type":"event","members":[{"kind":"data","name":"taker_address","type":"core::starknet::contract_address::ContractAddress"},{"kind":"data","name":"sell_address","type":"core::starknet::contract_address::ContractAddress"},{"kind":"data","name":"sell_amount","type":"core::integer::u256"},{"kind":"data","name":"buy_address","type":"core::starknet::contract_address::ContractAddress"},{"kind":"data","name":"buy_amount","type":"core::integer::u256"},{"kind":"data","name":"beneficiary","type":"core::starknet::contract_address::ContractAddress"}]},{"kind":"struct","name":"avnu::exchange::Exchange::OwnershipTransferred","type":"event","members":[{"kind":"data","name":"previous_owner","type":"core::starknet::contract_address::ContractAddress"},{"kind":"data","name":"new_owner","type":"core::starknet::contract_address::ContractAddress"}]},{"kind":"enum","name":"avnu::exchange::Exchange::Event","type":"event","variants":[{"kind":"nested","name":"Swap","type":"avnu::exchange::Exchange::Swap"},{"kind":"nested","name":"OwnershipTransferred","type":"avnu::exchange::Exchange::OwnershipTransferred"}]}]
    contract_address = 0x04270219d365d6b017231b52e92b3fb5d7c8378b05e9abc97724537a80e93b0f
    supported_tokens = ["ETH", "USDT", "USDC", "DAI", "WBTC", "LORDS", "WSTETH"]
    
    lpts = []
    
    tokens_from_lpt = {}

    stables = ["USDT", "USDC", "DAI"]
    
    def create_additional_payload_for_dex(self, dex, token1: Token, token2: Token):
        if dex == 0x041fd22b238fa21cfcf5dd45a8548974d8263b3a531a60388411c5e230f97023:
            return []
        elif dex == 0x10884171baf1914edc28d7afb619b40a4051cfae78a094a55d230f19e944a28:
            pool = MySwap().POOLS[f"{token1.symbol}:{token2.symbol}"]
            return [pool]
        elif dex == 0x28c858a586fa12123a1ccb337a0a3b369281f91ea00544d0c086524b759f627:
            if token1.stable and token2.stable:
                return [1]
            else:
                return [0]
        elif dex == 0x07a6f98c03379b9513ca84cca1373ff452a7462a3b61598f0af5bb27ad7f76d1:
            return []
        

    async def get_best_dex(self, token1, token2, amount_in, sender, proxy=None):
        proxies = {'https': proxy, 'http': proxy} if proxy else None
        resp = req(f"https://starknet.api.avnu.fi/swap/v1/prices?sellTokenAddress={hex(token1.contract_address)}&buyTokenAddress={hex(token2.contract_address)}&sellAmount={hex(int(amount_in*10**token1.decimals))}&takerAddress={hex(sender.stark_native_account.address)}&size=3&integratorName=AVNU%20Portal", proxies=proxies)

        dex_name = resp[0]["sourceName"]

        DEXes = {
            "JediSwap":0x041fd22b238fa21cfcf5dd45a8548974d8263b3a531a60388411c5e230f97023,
            "MySwap": 0x10884171baf1914edc28d7afb619b40a4051cfae78a094a55d230f19e944a28,
            "SithSwap": 0x28c858a586fa12123a1ccb337a0a3b369281f91ea00544d0c086524b759f627,
            "10kSwap" : 0x07a6f98c03379b9513ca84cca1373ff452a7462a3b61598f0af5bb27ad7f76d1
        }
        try:
            return DEXes[dex_name], int(resp[0]["buyAmount"], 16)
        except:
            try:
                dex_name = resp[2]["sourceName"]
                return DEXes[dex_name], int(resp[1]["buyAmount"], 16)
            except:
                dex_name = resp[2]["sourceName"]
                return DEXes[dex_name], int(resp[1]["buyAmount"], 16)

    def __init__(self) -> None:
        new_supported_tokens = []
        for token in self.supported_tokens:
            if token in SETTINGS["Supported_tokens"]:
                new_supported_tokens.append(token)
        self.supported_tokens = new_supported_tokens

    
    async def create_txn_for_swap(self, amount_in: float, token1: Token, amount_out: float, token2: Token, sender: BaseStarkAccount, full: bool = False, SaveEthOnBalance=None):
        
        
        if not full:
            dex, amount_out_avnu = await handle_dangerous_request(self.get_best_dex, "Can't get best dex for avnu: ", sender.formatted_hex_address, token1, token2, amount_in, sender)
            if amount_out_avnu < (1-slippage)*amount_out*10**token2.decimals:
                logger.error(f"[{sender.formatted_hex_address}] AVNU MIN VALUE TOO LOW. SKIP")
                return -1, 'AVNU MIN VALUE TOO LOW. SKIP'
            amount_out = amount_out_avnu
            call1 = token1.get_approve_call(amount_in, self.contract_address, sender)
            contract = Contract(self.contract_address, self.ABI, sender.stark_native_account, cairo_version=1)
            call2 = contract.functions["multi_route_swap"].prepare(
                token1.contract_address,
                int(amount_in*10**token1.decimals),
                token2.contract_address,
                int(amount_out),
                int(amount_out*(1-slippage)),
                sender.stark_native_account.address,
                0,
                0,
                [
                    {
                        "token_from":token1.contract_address,
                        "token_to":token2.contract_address,
                        "exchange_address":dex,
                        "percent":100,
                        "additional_swap_params":self.create_additional_payload_for_dex(dex, token1, token2)
                    }
                ]
            )
        else:
            bal = await sender.get_balance(token1.contract_address, token1.symbol)
            
            if token1.symbol == "ETH":
                bal -= int(get_random_value(SaveEthOnBalance if SaveEthOnBalance else SETTINGS["SaveEthOnBalance"])*1e18)
            dex, amount_out_avnu = await handle_dangerous_request(self.get_best_dex, "Can't get best dex for avnu: ", sender.formatted_hex_address, token1, token2, bal/10**token1.decimals, sender)
            if amount_out_avnu < (1-slippage)*amount_out*10**token2.decimals:
                logger.error(f"[{sender.formatted_hex_address}] AVNU MIN VALUE TOO LOW. SKIP")
                return -1, 'AVNU MIN VALUE TOO LOW. SKIP'
            amount_out = amount_out_avnu
            call1 = token1.get_approve_call_wei(bal, self.contract_address, sender)
            contract = Contract(self.contract_address, self.ABI, sender.stark_native_account, cairo_version=1)
            call2 = contract.functions["multi_route_swap"].prepare(
                token1.contract_address,
                bal,
                token2.contract_address,
                int(amount_out),
                int(amount_out*(1-slippage)),
                sender.stark_native_account.address,
                0,
                0,
                [
                    {
                        "token_from":token1.contract_address,
                        "token_to":token2.contract_address,
                        "exchange_address":dex,
                        "percent":100,
                        "additional_swap_params":self.create_additional_payload_for_dex(dex, token1, token2)
                    }
                ]
            )

        return 0, [call1, call2]

    async def create_txn_for_liq(self, amount1: float, token1: Token, amount2: float, token2: Token, sender: BaseStarkAccount):
        return -1, 'Avnu Liquidity not implemented'


    async def create_txn_for_remove_liq(self, lptoken: Token, sender: BaseStarkAccount):
        return -1, 'Avnu Liquidity not implemented'