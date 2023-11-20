from ..BaseClasses import *


class JediSwap(BaseDex):
    name = "JediSwap"
    ABI = [{"name":"Uint256","size":2,"type":"struct","members":[{"name":"low","type":"felt","offset":0},{"name":"high","type":"felt","offset":1}]},{"data":[{"name":"implementation","type":"felt"}],"keys":[],"name":"Upgraded","type":"event"},{"data":[{"name":"previousAdmin","type":"felt"},{"name":"newAdmin","type":"felt"}],"keys":[],"name":"AdminChanged","type":"event"},{"name":"initializer","type":"function","inputs":[{"name":"factory","type":"felt"},{"name":"proxy_admin","type":"felt"}],"outputs":[]},{"name":"factory","type":"function","inputs":[],"outputs":[{"name":"address","type":"felt"}],"stateMutability":"view"},{"name":"sort_tokens","type":"function","inputs":[{"name":"tokenA","type":"felt"},{"name":"tokenB","type":"felt"}],"outputs":[{"name":"token0","type":"felt"},{"name":"token1","type":"felt"}],"stateMutability":"view"},{"name":"quote","type":"function","inputs":[{"name":"amountA","type":"Uint256"},{"name":"reserveA","type":"Uint256"},{"name":"reserveB","type":"Uint256"}],"outputs":[{"name":"amountB","type":"Uint256"}],"stateMutability":"view"},{"name":"get_amount_out","type":"function","inputs":[{"name":"amountIn","type":"Uint256"},{"name":"reserveIn","type":"Uint256"},{"name":"reserveOut","type":"Uint256"}],"outputs":[{"name":"amountOut","type":"Uint256"}],"stateMutability":"view"},{"name":"get_amount_in","type":"function","inputs":[{"name":"amountOut","type":"Uint256"},{"name":"reserveIn","type":"Uint256"},{"name":"reserveOut","type":"Uint256"}],"outputs":[{"name":"amountIn","type":"Uint256"}],"stateMutability":"view"},{"name":"get_amounts_out","type":"function","inputs":[{"name":"amountIn","type":"Uint256"},{"name":"path_len","type":"felt"},{"name":"path","type":"felt*"}],"outputs":[{"name":"amounts_len","type":"felt"},{"name":"amounts","type":"Uint256*"}],"stateMutability":"view"},{"name":"get_amounts_in","type":"function","inputs":[{"name":"amountOut","type":"Uint256"},{"name":"path_len","type":"felt"},{"name":"path","type":"felt*"}],"outputs":[{"name":"amounts_len","type":"felt"},{"name":"amounts","type":"Uint256*"}],"stateMutability":"view"},{"name":"add_liquidity","type":"function","inputs":[{"name":"tokenA","type":"felt"},{"name":"tokenB","type":"felt"},{"name":"amountADesired","type":"Uint256"},{"name":"amountBDesired","type":"Uint256"},{"name":"amountAMin","type":"Uint256"},{"name":"amountBMin","type":"Uint256"},{"name":"to","type":"felt"},{"name":"deadline","type":"felt"}],"outputs":[{"name":"amountA","type":"Uint256"},{"name":"amountB","type":"Uint256"},{"name":"liquidity","type":"Uint256"}]},{"name":"remove_liquidity","type":"function","inputs":[{"name":"tokenA","type":"felt"},{"name":"tokenB","type":"felt"},{"name":"liquidity","type":"Uint256"},{"name":"amountAMin","type":"Uint256"},{"name":"amountBMin","type":"Uint256"},{"name":"to","type":"felt"},{"name":"deadline","type":"felt"}],"outputs":[{"name":"amountA","type":"Uint256"},{"name":"amountB","type":"Uint256"}]},{"name":"swap_exact_tokens_for_tokens","type":"function","inputs":[{"name":"amountIn","type":"Uint256"},{"name":"amountOutMin","type":"Uint256"},{"name":"path_len","type":"felt"},{"name":"path","type":"felt*"},{"name":"to","type":"felt"},{"name":"deadline","type":"felt"}],"outputs":[{"name":"amounts_len","type":"felt"},{"name":"amounts","type":"Uint256*"}]},{"name":"swap_tokens_for_exact_tokens","type":"function","inputs":[{"name":"amountOut","type":"Uint256"},{"name":"amountInMax","type":"Uint256"},{"name":"path_len","type":"felt"},{"name":"path","type":"felt*"},{"name":"to","type":"felt"},{"name":"deadline","type":"felt"}],"outputs":[{"name":"amounts_len","type":"felt"},{"name":"amounts","type":"Uint256*"}]}]
    contract_address = 0x041fd22b238fa21cfcf5dd45a8548974d8263b3a531a60388411c5e230f97023
    supported_tokens = ["ETH", "USDT", "USDC", "DAI", "WBTC", "WSTETH", "LORDS"]
    
    lpts = [
        LPToken("ETH:USDT", 0x45e7131d776dddc137e30bdd490b431c7144677e97bf9369f629ed8d3fb7dd6, 18),
        LPToken("ETH:USDC", 0x4d0390b777b424e43839cd1e744799f3de6c176c7e32c1812a41dbd9c19db6a, 18),
        LPToken("ETH:DAI", 0x7e2a13b40fc1119ec55e0bcf9428eedaa581ab3c924561ad4e955f95da63138, 18),
        LPToken("ETH:WBTC", 0x260e98362e0949fefff8b4de85367c035e44f734c9f8069b6ce2075ae86b45c, 18),
        LPToken("ETH:LORDS", 0x2b3030c04e9c920bd66c6a8dc209717bbefa1ea5f8bc8ebabd639e5a4766502, 18),
        LPToken("ETH:WSTETH", 0x70cda8400d7b1ee9e21f7194d320b9ad9c7a2b27e0d15a5a9967b9fefe10c76, 18),
        LPToken("USDT:USDC", 0x5801bdad32f343035fb242e98d1e9371ae85bc1543962fedea16c59b35bd19b, 18),
        LPToken("USDT:DAI", 0xf0f5b3eed258344152e1f17baf84a2e1b621cd754b625bec169e8595aea767, 18),
        LPToken("USDT:WBTC", 0x44d13ad98a46fd2322ef2637e5e4c292ce8822f47b7cb9a1d581176a801c1a0, 18),
        LPToken("USDT:LORDS", 0x51184e312f09abcbf28132d6ef58259a6ebe9b5e7e32b5200427fdc96973f94, 18),
        LPToken("USDT:WSTETH", 0x33863afb8968fc40bc588a7c839faea1d47bb43d034b8ba19f0b8acb7191522, 18),
        LPToken("USDC:DAI", 0xcfd39f5244f7b617418c018204a8a9f9a7f72e71f0ef38f968eeb2a9ca302b, 18),
        LPToken("USDC:WBTC", 0x5a8054e5ca0b277b295a830e53bd71a6a6943b42d0dbb22329437522bc80c8, 18),
        LPToken("USDC:LORDS", 0x7f409bd2e266e00486566dd3cb72bacc6996f49c0b19f04c0a8b5bd7bf991d1, 18),
        LPToken("USDC:WSTETH", 0x74855288dbb974584593acf7bd738572cce3d8f90a7076722d0a624a97d2620, 18),
        LPToken("DAI:WBTC", 0x39c183c8e5a2df130eefa6fbaa3b8aad89b29891f6272cb0c90deaa93ec6315, 18),
        LPToken("DAI:LORDS", 0x56dc2aa83379f195de35ee699a270c76f1c2840b8b97385689d9137b38d9f44, 18),
        LPToken("DAI:WSTETH", 0x73ffa5c873e39a2e8ea21494133081f4202b0dd583e50383a231b1f6f136a85, 18),
        LPToken("WBTC:LORDS", 0x54a6698d6ac927713cf66c2f595948991e0a27e1b1ac04956c32026d94a8f99, 18),
        LPToken("WBTC:WSTETH", 0x16220c67cdff746f2afd4178524a2dc9e49ff15567694277fa2302130576678, 18),
        LPToken("LORDS:WSTETH", 0x781694f7f5f4dc9d7273e669ab0f9c8a0bd2d2279cc238e53522cd2e028c69c, 18)
    ]
    
    tokens_from_lpt = {
        "0x45e7131d776dddc137e30bdd490b431c7144677e97bf9369f629ed8d3fb7dd6" : [0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8],
        "0x4d0390b777b424e43839cd1e744799f3de6c176c7e32c1812a41dbd9c19db6a" : [0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8],
        "0x7e2a13b40fc1119ec55e0bcf9428eedaa581ab3c924561ad4e955f95da63138" : [0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3],
        "0x260e98362e0949fefff8b4de85367c035e44f734c9f8069b6ce2075ae86b45c" : [0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac],
        "0x2b3030c04e9c920bd66c6a8dc209717bbefa1ea5f8bc8ebabd639e5a4766502" : [0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 0x0124aeb495b947201f5fac96fd1138e326ad86195b98df6dec9009158a533b49],
        "0x70cda8400d7b1ee9e21f7194d320b9ad9c7a2b27e0d15a5a9967b9fefe10c76" : [0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 0x042b8f0484674ca266ac5d08e4ac6a3fe65bd3129795def2dca5c34ecc5f96d2],
        "0x5801bdad32f343035fb242e98d1e9371ae85bc1543962fedea16c59b35bd19b" : [0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8, 0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8],
        "0xf0f5b3eed258344152e1f17baf84a2e1b621cd754b625bec169e8595aea767" : [0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8, 0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3],
        "0x44d13ad98a46fd2322ef2637e5e4c292ce8822f47b7cb9a1d581176a801c1a0" : [0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8, 0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac],
        "0x51184e312f09abcbf28132d6ef58259a6ebe9b5e7e32b5200427fdc96973f94" : [0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8, 0x0124aeb495b947201f5fac96fd1138e326ad86195b98df6dec9009158a533b49],
        "0x33863afb8968fc40bc588a7c839faea1d47bb43d034b8ba19f0b8acb7191522" : [0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8, 0x042b8f0484674ca266ac5d08e4ac6a3fe65bd3129795def2dca5c34ecc5f96d2],
        "0xcfd39f5244f7b617418c018204a8a9f9a7f72e71f0ef38f968eeb2a9ca302b" : [0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8, 0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3],
        "0x5a8054e5ca0b277b295a830e53bd71a6a6943b42d0dbb22329437522bc80c8" : [0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8, 0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac],
        "0x7f409bd2e266e00486566dd3cb72bacc6996f49c0b19f04c0a8b5bd7bf991d1" : [0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8, 0x0124aeb495b947201f5fac96fd1138e326ad86195b98df6dec9009158a533b49],
        "0x74855288dbb974584593acf7bd738572cce3d8f90a7076722d0a624a97d2620" : [0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8, 0x042b8f0484674ca266ac5d08e4ac6a3fe65bd3129795def2dca5c34ecc5f96d2],
        "0x39c183c8e5a2df130eefa6fbaa3b8aad89b29891f6272cb0c90deaa93ec6315" : [0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3, 0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac],
        "0x56dc2aa83379f195de35ee699a270c76f1c2840b8b97385689d9137b38d9f44" : [0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3, 0x0124aeb495b947201f5fac96fd1138e326ad86195b98df6dec9009158a533b49],
        "0x73ffa5c873e39a2e8ea21494133081f4202b0dd583e50383a231b1f6f136a85" : [0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3, 0x042b8f0484674ca266ac5d08e4ac6a3fe65bd3129795def2dca5c34ecc5f96d2],
        "0x54a6698d6ac927713cf66c2f595948991e0a27e1b1ac04956c32026d94a8f99" : [0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac, 0x0124aeb495b947201f5fac96fd1138e326ad86195b98df6dec9009158a533b49],
        "0x16220c67cdff746f2afd4178524a2dc9e49ff15567694277fa2302130576678" : [0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac, 0x042b8f0484674ca266ac5d08e4ac6a3fe65bd3129795def2dca5c34ecc5f96d2],
        "0x781694f7f5f4dc9d7273e669ab0f9c8a0bd2d2279cc238e53522cd2e028c69c" : [0x0124aeb495b947201f5fac96fd1138e326ad86195b98df6dec9009158a533b49, 0x042b8f0484674ca266ac5d08e4ac6a3fe65bd3129795def2dca5c34ecc5f96d2]
    }

    
    def __init__(self) -> None:
        new_supported_tokens = []
        for token in self.supported_tokens:
            if token in SETTINGS["Supported_tokens"]:
                new_supported_tokens.append(token)
        self.supported_tokens = new_supported_tokens



    async def create_txn_for_swap(self, amount_in: int, token1: Token, amount_out: int, token2: Token, sender: BaseStarkAccount, full: bool = False, SaveEthOnBalance=None):
        call1 = token1.get_approve_call_wei(amount_in, self.contract_address, sender)
        contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)
        call2 = contract.functions["swap_exact_tokens_for_tokens"].prepare(
            int(amount_in),
            int(amount_out*(1-slippage)),
            (
                token1.contract_address,
                token2.contract_address
            ),
            sender.stark_native_account.address,
            int(time.time())+3600
        )
        return 0, [call1, call2]

    async def create_txn_for_liq(self, amount1: float, token1: Token, amount2: float, token2: Token, sender: BaseStarkAccount):
        
        call1 = token1.get_approve_call(amount1, self.contract_address, sender)
        call2 = token2.get_approve_call(amount2, self.contract_address, sender)
        contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)

        call3 = contract.functions["add_liquidity"].prepare(
            token1.contract_address,
            token2.contract_address,
            int(amount1*10**token1.decimals),
            int(amount2*10**token2.decimals),
            int(amount1*10**token1.decimals * (1-slippage)),
            int(amount2*10**token2.decimals * (1-slippage)),
            sender.stark_native_account.address,
            int(time.time())+3600
        )

        return [call1, call2, call3]


    async def create_txn_for_remove_liq(self, lptoken: Token, sender: BaseStarkAccount):
        amount = await sender.get_balance(lptoken.contract_address, lptoken.symbol)

        token1_address = self.tokens_from_lpt[hex(lptoken.contract_address)][0]
        token2_address = self.tokens_from_lpt[hex(lptoken.contract_address)][1]

        contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)
        token_contract = Contract(lptoken.contract_address, STARK_TOKEN_ABI, sender.stark_native_account)
        token1_contract = Contract(token1_address, STARK_TOKEN_ABI, sender.stark_native_account)
        token2_contract = Contract(token2_address, STARK_TOKEN_ABI, sender.stark_native_account)
        
        
        total_liq_amount = (await handle_dangerous_request(token_contract.functions["totalSupply"].call, "Can't get jediswap total pool value. Error:", sender.formatted_hex_address)).totalSupply
        multiplier = amount/total_liq_amount
        token1_val = (await handle_dangerous_request(token1_contract.functions["balanceOf"].call, "Can't get pool info. Error:", sender.formatted_hex_address, lptoken.contract_address)).balance
        token1_val = int(token1_val*multiplier)
        token2_val = (await handle_dangerous_request(token2_contract.functions["balanceOf"].call, "Can't get pool info. Error:", sender.formatted_hex_address, lptoken.contract_address)).balance
        token2_val = int(token2_val*multiplier)
        

        if amount <= 0:
            return -1, 'Jediswap\tLiquidity is 0'
        
        call1 = lptoken.get_approve_call(amount, self.contract_address, sender)

        call2 = contract.functions["remove_liquidity"].prepare(
            token1_address,
            token2_address,
            amount,
            int(token1_val*(1-slippage)),
            int(token2_val*(1-slippage)),
            sender.stark_native_account.address,
            int(time.time())+3600
        )
        
        return 0, [call1, call2]