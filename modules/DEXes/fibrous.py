from starknet_py.contract import Contract

from modules.base_classes.base_defi import BaseDEX
from modules.utils.utils import get_random_value
from modules.config import SETTINGS, SLIPPAGE
from modules.utils.token import StarkToken
from modules.utils.logger import logger
from modules.base_classes.base_account import BaseAccount


class Fibrous(BaseDEX):
    name = "Fibrous"
    ABI = [{"name":"Router","type":"impl","interface_name":"FibrousRouter::interfaces::IROUTER::IRouter"},{"name":"core::integer::u256","type":"struct","members":[{"name":"low","type":"core::integer::u128"},{"name":"high","type":"core::integer::u128"}]},{"name":"FibrousRouter::utils::structs::RouteParam","type":"struct","members":[{"name":"token_in","type":"core::starknet::contract_address::ContractAddress"},{"name":"token_out","type":"core::starknet::contract_address::ContractAddress"},{"name":"amount_in","type":"core::integer::u256"},{"name":"min_received","type":"core::integer::u256"},{"name":"destination","type":"core::starknet::contract_address::ContractAddress"}]},{"name":"FibrousRouter::utils::structs::SwapParams","type":"struct","members":[{"name":"token_in","type":"core::starknet::contract_address::ContractAddress"},{"name":"token_out","type":"core::starknet::contract_address::ContractAddress"},{"name":"rate","type":"core::integer::u32"},{"name":"protocol_id","type":"core::felt252"},{"name":"pool_address","type":"core::starknet::contract_address::ContractAddress"},{"name":"extra_data","type":"core::array::Array::<core::felt252>"}]},{"name":"FibrousRouter::interfaces::IROUTER::IRouter","type":"interface","items":[{"name":"getOwner","type":"function","inputs":[],"outputs":[{"type":"core::starknet::contract_address::ContractAddress"}],"state_mutability":"view"},{"name":"getDirectFee","type":"function","inputs":[],"outputs":[{"type":"core::integer::u32"}],"state_mutability":"view"},{"name":"getRouterFee","type":"function","inputs":[],"outputs":[{"type":"core::integer::u32"}],"state_mutability":"view"},{"name":"getStarkRockAddress","type":"function","inputs":[],"outputs":[{"type":"core::starknet::contract_address::ContractAddress"}],"state_mutability":"view"},{"name":"getSwapHandler","type":"function","inputs":[{"name":"protocol_id","type":"core::felt252"}],"outputs":[{"type":"core::starknet::class_hash::ClassHash"}],"state_mutability":"view"},{"name":"locked","type":"function","inputs":[{"name":"id","type":"core::integer::u32"},{"name":"data","type":"core::array::Array::<core::felt252>"}],"outputs":[{"type":"core::array::Array::<core::felt252>"}],"state_mutability":"external"},{"name":"swap","type":"function","inputs":[{"name":"route","type":"FibrousRouter::utils::structs::RouteParam"},{"name":"swap_parameters","type":"core::array::Array::<FibrousRouter::utils::structs::SwapParams>"}],"outputs":[],"state_mutability":"external"},{"name":"setDirectSwapFee","type":"function","inputs":[{"name":"new_fee","type":"core::integer::u32"}],"outputs":[],"state_mutability":"external"},{"name":"setRouterFee","type":"function","inputs":[{"name":"new_fee","type":"core::integer::u32"}],"outputs":[],"state_mutability":"external"},{"name":"setStarkRockAddress","type":"function","inputs":[{"name":"new_address","type":"core::starknet::contract_address::ContractAddress"}],"outputs":[],"state_mutability":"external"},{"name":"setOwner","type":"function","inputs":[{"name":"new_owner","type":"core::starknet::contract_address::ContractAddress"}],"outputs":[],"state_mutability":"external"},{"name":"setFeeHandler","type":"function","inputs":[{"name":"new_fee_handler","type":"core::starknet::contract_address::ContractAddress"}],"outputs":[],"state_mutability":"external"},{"name":"setSwapHandler","type":"function","inputs":[{"name":"protocol_id","type":"core::felt252"},{"name":"handler","type":"core::starknet::class_hash::ClassHash"}],"outputs":[],"state_mutability":"external"},{"name":"upgrade","type":"function","inputs":[{"name":"new_hash","type":"core::starknet::class_hash::ClassHash"}],"outputs":[],"state_mutability":"external"}]},{"name":"constructor","type":"constructor","inputs":[{"name":"_owner","type":"core::starknet::contract_address::ContractAddress"}]},{"kind":"struct","name":"FibrousRouter::router::Router::Swap","type":"event","members":[{"kind":"data","name":"sender","type":"core::starknet::contract_address::ContractAddress"},{"kind":"data","name":"token_in","type":"core::starknet::contract_address::ContractAddress"},{"kind":"data","name":"token_out","type":"core::starknet::contract_address::ContractAddress"},{"kind":"data","name":"amount_in","type":"core::integer::u256"},{"kind":"data","name":"amount_out","type":"core::integer::u256"},{"kind":"data","name":"to","type":"core::starknet::contract_address::ContractAddress"}]},{"kind":"struct","name":"FibrousRouter::router::Router::AddHandler","type":"event","members":[{"kind":"data","name":"protocol_id","type":"core::felt252"},{"kind":"data","name":"class_hash","type":"core::starknet::class_hash::ClassHash"}]},{"kind":"struct","name":"FibrousRouter::router::Router::OwnerChanged","type":"event","members":[{"kind":"data","name":"old_owner","type":"core::starknet::contract_address::ContractAddress"},{"kind":"data","name":"new_owner","type":"core::starknet::contract_address::ContractAddress"}]},{"kind":"enum","name":"FibrousRouter::router::Router::Event","type":"event","variants":[{"kind":"nested","name":"Swap","type":"FibrousRouter::router::Router::Swap"},{"kind":"nested","name":"AddHandler","type":"FibrousRouter::router::Router::AddHandler"},{"kind":"nested","name":"OwnerChanged","type":"FibrousRouter::router::Router::OwnerChanged"}]}]
    contract_address = 0x00f6f4cf62e3c010e0ac2451cc7807b5eec19a40b0faacd00cca3914280fdf5a
    supported_tokens = ["ETH", "USDT", "USDC", "DAI", "WBTC", "LORDS", "WSTETH"]
    
    lpts = []
    
    tokens_from_lpt = {}

    pool_from_token = {
        "ETH:USDT": 0x45e7131d776dddc137e30bdd490b431c7144677e97bf9369f629ed8d3fb7dd6,
        "ETH:USDC": 0x4d0390b777b424e43839cd1e744799f3de6c176c7e32c1812a41dbd9c19db6a, 
        "ETH:DAI": 0x7e2a13b40fc1119ec55e0bcf9428eedaa581ab3c924561ad4e955f95da63138, 
        "ETH:WBTC": 0x260e98362e0949fefff8b4de85367c035e44f734c9f8069b6ce2075ae86b45c, 
        "ETH:LORDS": 0x2b3030c04e9c920bd66c6a8dc209717bbefa1ea5f8bc8ebabd639e5a4766502,
        "ETH:WSTETH": 0x70cda8400d7b1ee9e21f7194d320b9ad9c7a2b27e0d15a5a9967b9fefe10c76, 
        "USDT:USDC": 0x5801bdad32f343035fb242e98d1e9371ae85bc1543962fedea16c59b35bd19b, 
        "USDT:DAI": 0xf0f5b3eed258344152e1f17baf84a2e1b621cd754b625bec169e8595aea767, 
        "USDT:WBTC": 0x44d13ad98a46fd2322ef2637e5e4c292ce8822f47b7cb9a1d581176a801c1a0, 
        "USDT:LORDS": 0x51184e312f09abcbf28132d6ef58259a6ebe9b5e7e32b5200427fdc96973f94, 
        "USDT:WSTETH": 0x33863afb8968fc40bc588a7c839faea1d47bb43d034b8ba19f0b8acb7191522, 
        "USDC:DAI": 0xcfd39f5244f7b617418c018204a8a9f9a7f72e71f0ef38f968eeb2a9ca302b, 
        "USDC:WBTC": 0x5a8054e5ca0b277b295a830e53bd71a6a6943b42d0dbb22329437522bc80c8, 
        "USDC:LORDS": 0x7f409bd2e266e00486566dd3cb72bacc6996f49c0b19f04c0a8b5bd7bf991d1, 
        "USDC:WSTETH": 0x74855288dbb974584593acf7bd738572cce3d8f90a7076722d0a624a97d2620, 
        "DAI:WBTC": 0x39c183c8e5a2df130eefa6fbaa3b8aad89b29891f6272cb0c90deaa93ec6315, 
        "DAI:LORDS": 0x56dc2aa83379f195de35ee699a270c76f1c2840b8b97385689d9137b38d9f44,
        "DAI:WSTETH": 0x73ffa5c873e39a2e8ea21494133081f4202b0dd583e50383a231b1f6f136a85, 
        "WBTC:LORDS": 0x54a6698d6ac927713cf66c2f595948991e0a27e1b1ac04956c32026d94a8f99, 
        "WBTC:WSTETH": 0x16220c67cdff746f2afd4178524a2dc9e49ff15567694277fa2302130576678,
        "LORDS:WSTETH": 0x781694f7f5f4dc9d7273e669ab0f9c8a0bd2d2279cc238e53522cd2e028c69c
    }

    
    def normalize_tokens(self, token1, token2):
        t1 = self.supported_tokens.index(token1)
        t2 = self.supported_tokens.index(token2)

        if t1 > t2:
            return f"{token2}:{token1}"
        else:
            return f"{token1}:{token2}"

    def __init__(self) -> None:
        new_supported_tokens = []
        for token in self.supported_tokens:
            if token in SETTINGS["Supported_tokens"]:
                new_supported_tokens.append(token)
        self.supported_tokens = new_supported_tokens

    async def get_token1_for_token2_price(self, token1: StarkToken, token2: StarkToken, amount_in: float, sender: BaseAccount):

        amount_out = (await token1.get_usd_value(amount_in) *await token2.get_price()) * 0.96

        return amount_in/amount_out
    
    async def create_txn_for_swap(self, amount_in: float, token1: StarkToken, amount_out: float, token2: StarkToken, sender: BaseAccount, full: bool = False):
        
        pair = self.normalize_tokens(token1.symbol, token2.symbol)
        
        pool = self.pool_from_token[pair]
        if not full:
            call1 = token1.get_approve_call(amount_in, self.contract_address, sender)
            contract = Contract(self.contract_address, self.ABI, sender.stark_native_account, cairo_version=1)
            call2 = contract.functions["swap"].prepare(
                
                {
                    "token_in":token1.contract_address,
                    "token_out":token2.contract_address,
                    "amount_in": int(amount_in*10**token1.decimals),
                    "min_received":int(amount_out*10**token2.decimals*(1-SLIPPAGE)),
                    "destination": sender.stark_native_account.address
                },
                [
                    {
                        "token_in" : token1.contract_address,
                        "token_out": token2.contract_address,
                        "rate": 1000000,
                        "protocol_id": 3,
                        "pool_address": pool,
                        "extra_data": []
                    }
                ]
            )
        else:
            bal = (await sender.get_balance_starknet(token1))[0] - 1
            if token1.symbol == "ETH":
                bal -= int(get_random_value(SETTINGS["SaveEthOnBalance"])*1e18)
            call1 = token1.get_approve_call_wei(bal, self.contract_address, sender)
            contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)
            
            call2 = contract.functions["swap"].prepare(
                [
                    {
                        "token_in" : token1.contract_address,
                        "token_out": token2.contract_address,
                        "rate": 1000000,
                        "protocol": 2,
                        "pool_address": pool
                    }
                ],
                {
                    "token_in":token1.contract_address,
                    "token_out":token2.contract_address,
                    "amount": bal,
                    "min_received":int(amount_out*10**token2.decimals*(1-SLIPPAGE)),
                    "destination": sender.stark_native_account.address
                }
            )
        return [call1, call2]

    async def create_txn_for_liq(self, amount1: float, token1: StarkToken, amount2: float, token2: StarkToken, sender: BaseAccount):
        return -1


    async def create_txn_for_remove_liq(self, lptoken: StarkToken, sender: BaseAccount):
        return -1