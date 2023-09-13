from BaseClasses import *


class MySwap(BaseDex):
    name = "MySwap"
    POOLS = {
        "ETH:USDC": 1,
        "USDC:ETH": 1,
        "DAI:ETH": 2,
        "ETH:DAI": 2,
        "WBTC:USDC": 3,
        "USDC:WBTC": 3,
        "ETH:USDT": 4,
        "USDT:ETH": 4,
        "USDT:USDC": 5,
        "USDC:USDT": 5,
        "USDC:DAI": 6,
        "DAI:USDC": 6,
        "WSTETH:ETH": 7,
        "ETH:WSTETH": 7,
        "ETH:LORDS": 8,
        "LORDS:ETH": 8,

    }
    ABI = [{"name":"Uint256","size":2,"type":"struct","members":[{"name":"low","type":"felt","offset":0},{"name":"high","type":"felt","offset":1}]},{"name":"Pool","size":10,"type":"struct","members":[{"name":"name","type":"felt","offset":0},{"name":"token_a_address","type":"felt","offset":1},{"name":"token_a_reserves","type":"Uint256","offset":2},{"name":"token_b_address","type":"felt","offset":4},{"name":"token_b_reserves","type":"Uint256","offset":5},{"name":"fee_percentage","type":"felt","offset":7},{"name":"cfmm_type","type":"felt","offset":8},{"name":"liq_token","type":"felt","offset":9}]},{"data":[{"name":"implementation","type":"felt"}],"keys":[],"name":"Upgraded","type":"event"},{"data":[{"name":"previousAdmin","type":"felt"},{"name":"newAdmin","type":"felt"}],"keys":[],"name":"AdminChanged","type":"event"},{"name":"swap","type":"function","inputs":[{"name":"pool_id","type":"felt"},{"name":"token_from_addr","type":"felt"},{"name":"amount_from","type":"Uint256"},{"name":"amount_to_min","type":"Uint256"}],"outputs":[{"name":"amount_to","type":"Uint256"}]},{"name":"withdraw_liquidity","type":"function","inputs":[{"name":"pool_id","type":"felt"},{"name":"shares_amount","type":"Uint256"},{"name":"amount_min_a","type":"Uint256"},{"name":"amount_min_b","type":"Uint256"}],"outputs":[{"name":"actual1","type":"Uint256"},{"name":"actual2","type":"Uint256"},{"name":"res1","type":"Uint256"},{"name":"res2","type":"Uint256"}]},{"name":"add_liquidity","type":"function","inputs":[{"name":"a_address","type":"felt"},{"name":"a_amount","type":"Uint256"},{"name":"a_min_amount","type":"Uint256"},{"name":"b_address","type":"felt"},{"name":"b_amount","type":"Uint256"},{"name":"b_min_amount","type":"Uint256"}],"outputs":[{"name":"actual1","type":"Uint256"},{"name":"actual2","type":"Uint256"}]},{"name":"create_new_pool","type":"function","inputs":[{"name":"pool_name","type":"felt"},{"name":"a_address","type":"felt"},{"name":"a_initial_liquidity","type":"Uint256"},{"name":"b_address","type":"felt"},{"name":"b_initial_liquidity","type":"Uint256"},{"name":"a_times_b_sqrt_value","type":"Uint256"}],"outputs":[{"name":"pool_id","type":"felt"}]},{"name":"get_version","type":"function","inputs":[],"outputs":[{"name":"ver","type":"felt"}],"stateMutability":"view"},{"name":"get_total_number_of_pools","type":"function","inputs":[],"outputs":[{"name":"num","type":"felt"}],"stateMutability":"view"},{"name":"get_pool","type":"function","inputs":[{"name":"pool_id","type":"felt"}],"outputs":[{"name":"pool","type":"Pool"}],"stateMutability":"view"},{"name":"get_lp_balance","type":"function","inputs":[{"name":"pool_id","type":"felt"},{"name":"lp_address","type":"felt"}],"outputs":[{"name":"shares","type":"Uint256"}],"stateMutability":"view"},{"name":"get_total_shares","type":"function","inputs":[{"name":"pool_id","type":"felt"}],"outputs":[{"name":"total_shares","type":"Uint256"}],"stateMutability":"view"},{"name":"upgrade","type":"function","inputs":[{"name":"new_implementation","type":"felt"}],"outputs":[]}]
    contract_address = 0x10884171baf1914edc28d7afb619b40a4051cfae78a094a55d230f19e944a28
    supported_tokens = ["ETH", "USDT", "USDC", "DAI", "WBTC", "WSTETH", "LORDS"]
    
    lpts = [
        LPToken("ETH:USDC", 0x022b05f9396d2c48183f6deaf138a57522bcc8b35b67dee919f76403d1783136, 12),
        LPToken("DAI:ETH", 0x07c662b10f409d7a0a69c8da79b397fd91187ca5f6230ed30effef2dceddc5b3, 18),
        LPToken("WBTC:USDC", 0x025b392609604c75d62dde3d6ae98e124a31b49123b8366d7ce0066ccb94f696, 7),
        LPToken("ETH:USDT", 0x041f9a1e9a4d924273f5a5c0c138d52d66d2e6a8bee17412c6b0f48fe059ae04, 12),
        LPToken("USDT:USDC", 0x01ea237607b7d9d2e9997aa373795929807552503683e35d8739f4dc46652de1, 6),
        LPToken("USDC:DAI", 0x0611e8f4f3badf1737b9e8f0ca77dd2f6b46a1d33ce4eed951c6b18ac497d505, 12),
        LPToken("WSTETH:ETH", 0x014e644c20bd5f9888033d2093c8ba3334caa0c7d15ed142962a9bebf36cc7e0, 18),
        LPToken("ETH:LORDS", 0x02699b69786cb08b4c83c1c02e943eca3eba00234d80a564ebe00c40226ea70b, 18)
    ]
    
    pool_id_from_lpt = {
        lpts[0]: 1,
        lpts[1]: 2,
        lpts[2]: 3,
        lpts[3]: 4,
        lpts[4]: 5,
        lpts[5]: 6,
        lpts[6]: 7,
        lpts[7]: 8,
    }

    def __init__(self) -> None:
        new_supported_tokens = []
        for token in self.supported_tokens:
            if token in SETTINGS["Supported_tokens"]:
                new_supported_tokens.append(token)
        self.supported_tokens = new_supported_tokens



    async def create_txn_for_swap(self, amount_in: float, token1: Token, amount_out: float, token2: Token, sender: BaseStarkAccount):
        try:
            a = self.POOLS[f"{token1.symbol}:{token2.symbol}"]
        except:
            logger.error(f"[{sender.formatted_hex_address} got unsupported pool on myswap. Skip")
            return -1
        
        call1 = token1.get_approve_call(amount_in, self.contract_address, sender)
        contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)
        call2 = contract.functions["swap"].prepare(
            self.POOLS[f"{token1.symbol}:{token2.symbol}"],
            token1.contract_address,
            int(amount_in*10**token1.decimals),
            int(amount_out*10**token2.decimals*(1-slippage))
        )

        return [call1, call2]

    async def create_txn_for_liq(self, amount1: float, token1: Token, amount2: float, token2: Token, sender: BaseStarkAccount):
        try:
            a = self.POOLS[f"{token1.symbol}:{token2.symbol}"]
        except:
            logger.error(f"[{sender.formatted_hex_address} got unsupported pool on myswap. Skip")
            return -1
        call1 = token1.get_approve_call(amount1, self.contract_address, sender)
        call2 = token2.get_approve_call(amount2, self.contract_address, sender)
        contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)

        call3 = contract.functions["add_liquidity"].prepare(
            token1.contract_address,
            int(amount1*10**token1.decimals),
            int(amount1*10**token1.decimals * (1-slippage)),
            token2.contract_address,
            int(amount2*10**token2.decimals),
            int(amount2*10**token2.decimals * (1-slippage)),
        )

        return [call1, call2, call3]


    async def create_txn_for_remove_liq(self, lptoken: Token, sender: BaseStarkAccount):
        amount = await sender.get_balance(lptoken.contract_address, lptoken.symbol)
        contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)
        total_liq_amount = await handle_dangerous_request(contract.functions["get_total_shares"].call, "Can't get myswap total pool value. Error:", sender.formatted_hex_address, self.pool_id_from_lpt[lptoken])
        multiplier = amount/total_liq_amount
        pool_info = json.loads(await handle_dangerous_request(contract.functions["get_pool"].call, "Can't get pool info. Error:", sender.formatted_hex_address, self.pool_id_from_lpt[lptoken]))
        token1_val = 0
        token2_val = 0
        for data in pool_info:
            name = data["name"]
            if name == "token_a_reserves":
                token1_val = data["value"]*multiplier
            if name == "token_b_reserves":
                token2_val = data["value"]*multiplier
        if amount <= 0:
            return -1
        
        call1 = lptoken.get_approve_call(amount, self.contract_address, sender)

        call2 = contract.functions["withdraw_liquidity"].prepare(
            self.pool_id_from_lpt[lptoken],
            amount,
            int(token1_val * (1-slippage)),
            int(token2_val * (1-slippage))
        )
        
        return [call1, call2]