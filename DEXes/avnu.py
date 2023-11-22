from ..BaseClasses import *
from .myswap import MySwap

class Avnu(BaseDex):
    name = "Avnu"
    #ABI = [{"name":"ExchangeLocker","type":"impl","interface_name":"avnu::interfaces::locker::ILocker"},{"name":"avnu::interfaces::locker::ILocker","type":"interface","items":[{"name":"locked","type":"function","inputs":[{"name":"id","type":"core::integer::u32"},{"name":"data","type":"core::array::Array::<core::felt252>"}],"outputs":[{"type":"core::array::Array::<core::felt252>"}],"state_mutability":"external"}]},{"name":"Exchange","type":"impl","interface_name":"avnu::exchange::IExchange"},{"name":"core::integer::u256","type":"struct","members":[{"name":"low","type":"core::integer::u128"},{"name":"high","type":"core::integer::u128"}]},{"name":"avnu::models::Route","type":"struct","members":[{"name":"token_from","type":"core::starknet::contract_address::ContractAddress"},{"name":"token_to","type":"core::starknet::contract_address::ContractAddress"},{"name":"exchange_address","type":"core::starknet::contract_address::ContractAddress"},{"name":"percent","type":"core::integer::u128"},{"name":"additional_swap_params","type":"core::array::Array::<core::felt252>"}]},{"name":"core::bool","type":"enum","variants":[{"name":"False","type":"()"},{"name":"True","type":"()"}]},{"name":"avnu::exchange::IExchange","type":"interface","items":[{"name":"get_adapter_class_hash","type":"function","inputs":[{"name":"exchange_address","type":"core::starknet::contract_address::ContractAddress"}],"outputs":[{"type":"core::starknet::class_hash::ClassHash"}],"state_mutability":"view"},{"name":"get_fee_collector_address","type":"function","inputs":[],"outputs":[{"type":"core::starknet::contract_address::ContractAddress"}],"state_mutability":"view"},{"name":"get_owner","type":"function","inputs":[],"outputs":[{"type":"core::starknet::contract_address::ContractAddress"}],"state_mutability":"view"},{"name":"multi_route_swap","type":"function","inputs":[{"name":"token_from_address","type":"core::starknet::contract_address::ContractAddress"},{"name":"token_from_amount","type":"core::integer::u256"},{"name":"token_to_address","type":"core::starknet::contract_address::ContractAddress"},{"name":"token_to_amount","type":"core::integer::u256"},{"name":"token_to_min_amount","type":"core::integer::u256"},{"name":"beneficiary","type":"core::starknet::contract_address::ContractAddress"},{"name":"integrator_fee_amount_bps","type":"core::integer::u128"},{"name":"integrator_fee_recipient","type":"core::starknet::contract_address::ContractAddress"},{"name":"routes","type":"core::array::Array::<avnu::models::Route>"}],"outputs":[{"type":"core::bool"}],"state_mutability":"external"},{"name":"set_adapter_class_hash","type":"function","inputs":[{"name":"exchange_address","type":"core::starknet::contract_address::ContractAddress"},{"name":"adapter_class_hash","type":"core::starknet::class_hash::ClassHash"}],"outputs":[{"type":"core::bool"}],"state_mutability":"external"},{"name":"set_fee_collector_address","type":"function","inputs":[{"name":"new_fee_collector_address","type":"core::starknet::contract_address::ContractAddress"}],"outputs":[{"type":"core::bool"}],"state_mutability":"external"},{"name":"transfer_ownership","type":"function","inputs":[{"name":"new_owner","type":"core::starknet::contract_address::ContractAddress"}],"outputs":[{"type":"core::bool"}],"state_mutability":"external"},{"name":"upgrade_class","type":"function","inputs":[{"name":"new_class_hash","type":"core::starknet::class_hash::ClassHash"}],"outputs":[{"type":"core::bool"}],"state_mutability":"external"}]},{"name":"constructor","type":"constructor","inputs":[{"name":"owner","type":"core::starknet::contract_address::ContractAddress"},{"name":"fee_collector_address","type":"core::starknet::contract_address::ContractAddress"}]},{"kind":"struct","name":"avnu::exchange::Exchange::Swap","type":"event","members":[{"kind":"data","name":"taker_address","type":"core::starknet::contract_address::ContractAddress"},{"kind":"data","name":"sell_address","type":"core::starknet::contract_address::ContractAddress"},{"kind":"data","name":"sell_amount","type":"core::integer::u256"},{"kind":"data","name":"buy_address","type":"core::starknet::contract_address::ContractAddress"},{"kind":"data","name":"buy_amount","type":"core::integer::u256"},{"kind":"data","name":"beneficiary","type":"core::starknet::contract_address::ContractAddress"}]},{"kind":"struct","name":"avnu::exchange::Exchange::OwnershipTransferred","type":"event","members":[{"kind":"data","name":"previous_owner","type":"core::starknet::contract_address::ContractAddress"},{"kind":"data","name":"new_owner","type":"core::starknet::contract_address::ContractAddress"}]},{"kind":"enum","name":"avnu::exchange::Exchange::Event","type":"event","variants":[{"kind":"nested","name":"Swap","type":"avnu::exchange::Exchange::Swap"},{"kind":"nested","name":"OwnershipTransferred","type":"avnu::exchange::Exchange::OwnershipTransferred"}]}]
    contract_address = 0x04270219d365d6b017231b52e92b3fb5d7c8378b05e9abc97724537a80e93b0f
    supported_tokens = ["ETH", "USDT", "USDC", "DAI", "WBTC", "LORDS", "WSTETH"]
    
    lpts = []
    
    tokens_from_lpt = {}

    stables = ["USDT", "USDC", "DAI"]

    def get_avnu_call(self, token1, token2, amount_in, sender, proxy=None):
        proxies = {'https': sender.proxy, 'http': sender.proxy} if sender.proxy else None
        resp = req(f'https://starknet.api.avnu.fi/swap/v1/quotes?sellTokenAddress={hex(token1.contract_address)}&buyTokenAddress={hex(token2.contract_address)}&sellAmount={hex(amount_in)}&takerAddress={hex(sender.stark_native_account.address)}&size=3&integratorName=AVNU%20Portal', proxies=proxies)
        quoteId = resp[0]['quoteId']
        usd_in = resp[0]["sellAmountInUsd"]
        usd_out = resp[0]["buyAmountInUsd"]
        json_body = {
            "quoteId": quoteId,
            "takerAddress": f'{hex(sender.stark_native_account.address)}',
            "slippage": 0.01}
        result = requests.post('https://starknet.api.avnu.fi/swap/v1/build', json=json_body, proxies=proxies)
        r = result.json()
        calldata = r['calldata']
        calldata = [int(call, 16) for call in calldata]
        call = Call(
            to_addr=self.contract_address,
            selector=get_selector_from_name(r['entrypoint']),
            calldata=calldata
            )
        relation = usd_out / usd_in
        return relation, call

    def __init__(self) -> None:
        new_supported_tokens = []
        for token in self.supported_tokens:
            if token in SETTINGS["Supported_tokens"]:
                new_supported_tokens.append(token)
        self.supported_tokens = new_supported_tokens

    
    async def create_txn_for_swap(self, amount_in: int, token1: Token, amount_out: int, token2: Token, sender: BaseStarkAccount, slippage=0.001):
        call1 = token1.get_approve_call_wei(amount_in, self.contract_address, sender)
        relation, call2 = self.get_avnu_call(token1, token2, amount_in, sender)
        if relation < (1-slippage):
            return -1, 'Slippage too high (avnu)'
        return 0, [call1, call2]

    async def create_txn_for_liq(self, amount1: float, token1: Token, amount2: float, token2: Token, sender: BaseStarkAccount):
        return -1, 'Avnu Liquidity not implemented'


    async def create_txn_for_remove_liq(self, lptoken: Token, sender: BaseStarkAccount):
        return -1, 'Avnu Liquidity not implemented'