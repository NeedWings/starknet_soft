from ..BaseClasses import *


class SithSwap(BaseDex):
    name = "SithSwap"
    ABI = [{"name":"Uint256","size":2,"type":"struct","members":[{"name":"low","type":"felt","offset":0},{"name":"high","type":"felt","offset":1}]},{"name":"Route","size":3,"type":"struct","members":[{"name":"from_address","type":"felt","offset":0},{"name":"to_address","type":"felt","offset":1},{"name":"stable","type":"felt","offset":2}]},{"name":"constructor","type":"constructor","inputs":[{"name":"factory","type":"felt"}],"outputs":[]},{"name":"factory","type":"function","inputs":[],"outputs":[{"name":"res","type":"felt"}],"stateMutability":"view"},{"name":"sortTokens","type":"function","inputs":[{"name":"token_a","type":"felt"},{"name":"token_b","type":"felt"}],"outputs":[{"name":"token0","type":"felt"},{"name":"token1","type":"felt"}],"stateMutability":"view"},{"name":"pairFor","type":"function","inputs":[{"name":"token_a","type":"felt"},{"name":"token_b","type":"felt"},{"name":"stable","type":"felt"}],"outputs":[{"name":"res","type":"felt"}],"stateMutability":"view"},{"name":"isPair","type":"function","inputs":[{"name":"pair","type":"felt"}],"outputs":[{"name":"res","type":"felt"}],"stateMutability":"view"},{"name":"getReserves","type":"function","inputs":[{"name":"token_a","type":"felt"},{"name":"token_b","type":"felt"},{"name":"stable","type":"felt"}],"outputs":[{"name":"reserve_a","type":"Uint256"},{"name":"reserve_b","type":"Uint256"}],"stateMutability":"view"},{"name":"getAmountOut","type":"function","inputs":[{"name":"amount_in","type":"Uint256"},{"name":"token_in","type":"felt"},{"name":"token_out","type":"felt"}],"outputs":[{"name":"amount","type":"Uint256"},{"name":"stable","type":"felt"}],"stateMutability":"view"},{"name":"getAmountsOut","type":"function","inputs":[{"name":"amount_in","type":"Uint256"},{"name":"routes_len","type":"felt"},{"name":"routes","type":"Route*"}],"outputs":[{"name":"amounts_len","type":"felt"},{"name":"amounts","type":"Uint256*"}],"stateMutability":"view"},{"name":"getTradeDiff","type":"function","inputs":[{"name":"amount_in","type":"Uint256"},{"name":"token_in","type":"felt"},{"name":"token_out","type":"felt"},{"name":"stable","type":"felt"}],"outputs":[{"name":"rate_a","type":"Uint256"},{"name":"rate_b","type":"Uint256"}],"stateMutability":"view"},{"name":"quoteAddLiquidity","type":"function","inputs":[{"name":"token_a","type":"felt"},{"name":"token_b","type":"felt"},{"name":"stable","type":"felt"},{"name":"amount_a_desired","type":"Uint256"},{"name":"amount_b_desired","type":"Uint256"}],"outputs":[{"name":"amount_a","type":"Uint256"},{"name":"amount_b","type":"Uint256"},{"name":"liquidity","type":"Uint256"}],"stateMutability":"view"},{"name":"quoteRemoveLiquidity","type":"function","inputs":[{"name":"token_a","type":"felt"},{"name":"token_b","type":"felt"},{"name":"stable","type":"felt"},{"name":"liquidity","type":"Uint256"}],"outputs":[{"name":"amount_a","type":"Uint256"},{"name":"amount_b","type":"Uint256"}],"stateMutability":"view"},{"name":"addLiquidity","type":"function","inputs":[{"name":"token_a","type":"felt"},{"name":"token_b","type":"felt"},{"name":"stable","type":"felt"},{"name":"amount_a_desired","type":"Uint256"},{"name":"amount_b_desired","type":"Uint256"},{"name":"amount_a_min","type":"Uint256"},{"name":"amount_b_min","type":"Uint256"},{"name":"to","type":"felt"},{"name":"deadline","type":"felt"}],"outputs":[{"name":"amount_a","type":"Uint256"},{"name":"amount_b","type":"Uint256"},{"name":"liquidity","type":"Uint256"}]},{"name":"removeLiquidity","type":"function","inputs":[{"name":"token_a","type":"felt"},{"name":"token_b","type":"felt"},{"name":"stable","type":"felt"},{"name":"liquidity","type":"Uint256"},{"name":"amount_a_min","type":"Uint256"},{"name":"amount_b_min","type":"Uint256"},{"name":"to","type":"felt"},{"name":"deadline","type":"felt"}],"outputs":[{"name":"amount_a","type":"Uint256"},{"name":"amount_b","type":"Uint256"}]},{"name":"swapExactTokensForTokensSimple","type":"function","inputs":[{"name":"amount_in","type":"Uint256"},{"name":"amount_out_min","type":"Uint256"},{"name":"token_from","type":"felt"},{"name":"token_to","type":"felt"},{"name":"to","type":"felt"},{"name":"deadline","type":"felt"}],"outputs":[{"name":"amounts_len","type":"felt"},{"name":"amounts","type":"Uint256*"}]},{"name":"swapExactTokensForTokens","type":"function","inputs":[{"name":"amount_in","type":"Uint256"},{"name":"amount_out_min","type":"Uint256"},{"name":"routes_len","type":"felt"},{"name":"routes","type":"Route*"},{"name":"to","type":"felt"},{"name":"deadline","type":"felt"}],"outputs":[{"name":"amounts_len","type":"felt"},{"name":"amounts","type":"Uint256*"}]},{"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","type":"function","inputs":[{"name":"amount_in","type":"Uint256"},{"name":"amount_out_min","type":"Uint256"},{"name":"routes_len","type":"felt"},{"name":"routes","type":"Route*"},{"name":"to","type":"felt"},{"name":"deadline","type":"felt"}],"outputs":[]}]
    contract_address = 0x028c858a586fa12123a1ccb337a0a3b369281f91ea00544d0c086524b759f627
    supported_tokens = ["ETH", "USDT", "USDC", "DAI", "WBTC", "LORDS", "WSTETH"]
    
    lpts = [
        LPToken("ETH:USDT", 0x691fa7f66d63dc8c89ff4e77732fff5133f282e7dbd41813273692cc595516, 18),
        LPToken("ETH:USDC", 0x30615bec9c1506bfac97d9dbd3c546307987d467a7f95d5533c2e861eb81f3f, 18),
        LPToken("ETH:DAI", 0x32ebb8e68553620b97b308684babf606d9556d5c0a652450c32e85f40d000d, 18),
        LPToken("ETH:WBTC", 0x106ff0f48fba1274b1f4f65e6d847fa58ac455e95318754fec20eb221b660ed, 18),
        LPToken("ETH:WSTETH", 0xa20410b97dcbfb44f370b67f877c669d859ff85c536d5e8e8336b6d565e1f8, 18),
        LPToken("ETH:LORDS", 0x2718bbc0176cff083b5c95ac22691bd1c16d55d37ae153d3ba347ce2292417e, 18),
        LPToken("USDT:USDC", 0x601f72228f73704e827de5bcd8dadaad52c652bb1e42bf492d90bbe22df2cec, 18),
        LPToken("USDT:DAI", 0x7500d8ba71b0a0c587fa431753dbb01a4595a434f27b296358c2c4cb7f83585, 18),
        LPToken("USDT:LORDS", 0x351d125294ae90c5ac53405ebc491d5d910e4f903cdc5d8c0d342dfa71fd0e9, 18),
        LPToken("USDC:DAI", 0x15e9cd2d4d6b4bb9f1124688b1e6bc19b4ff877a01011d28c25c9ee918e83e5, 18),
        LPToken("USDC:WBTC", 0x24bd1600bbe18593e983f858f2e7a69148e6b973f43b6304b2b8cf110059595, 18),
        LPToken("USDC:WSTETH", 0x1f410986ac70a3d2f945bedc47133abe0d20d95e0cb65cd16e9e77e03bcd9d9, 18),
        LPToken("USDC:LORDS", 0x1283d9f872498556e11b48ec440d66ebe55c6624bc34b737ffb3939fc08203e, 18),
        LPToken("DAI:WBTC", 0x68fa77586bc98d71125e342660ebdfb17a1c26027002af1dd8a620d93ea3ba3, 18),
        LPToken("DAI:LORDS", 0x1eb8805c2f3cc4a7ac8ddde3f8b3e1d7d197053fa6050e318de2100e4eb2d18, 18)
    ]
    
    tokens_from_lpt = {
        "0x691fa7f66d63dc8c89ff4e77732fff5133f282e7dbd41813273692cc595516": [0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8],
        "0x30615bec9c1506bfac97d9dbd3c546307987d467a7f95d5533c2e861eb81f3f": [0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8],
        "0x32ebb8e68553620b97b308684babf606d9556d5c0a652450c32e85f40d000d": [0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3],
        "0x106ff0f48fba1274b1f4f65e6d847fa58ac455e95318754fec20eb221b660ed": [0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac],
        "0xa20410b97dcbfb44f370b67f877c669d859ff85c536d5e8e8336b6d565e1f8": [0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 0x042b8f0484674ca266ac5d08e4ac6a3fe65bd3129795def2dca5c34ecc5f96d2],
        "0x2718bbc0176cff083b5c95ac22691bd1c16d55d37ae153d3ba347ce2292417e": [0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 0x0124aeb495b947201f5fac96fd1138e326ad86195b98df6dec9009158a533b49],
        "0x601f72228f73704e827de5bcd8dadaad52c652bb1e42bf492d90bbe22df2cec": [0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8, 0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8],
        "0x7500d8ba71b0a0c587fa431753dbb01a4595a434f27b296358c2c4cb7f83585": [0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8, 0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3],
        "0x351d125294ae90c5ac53405ebc491d5d910e4f903cdc5d8c0d342dfa71fd0e9": [0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8, 0x0124aeb495b947201f5fac96fd1138e326ad86195b98df6dec9009158a533b49],
        "0x15e9cd2d4d6b4bb9f1124688b1e6bc19b4ff877a01011d28c25c9ee918e83e5": [0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8, 0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3],
        "0x24bd1600bbe18593e983f858f2e7a69148e6b973f43b6304b2b8cf110059595": [0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8, 0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac],
        "0x1f410986ac70a3d2f945bedc47133abe0d20d95e0cb65cd16e9e77e03bcd9d9": [0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8, 0x042b8f0484674ca266ac5d08e4ac6a3fe65bd3129795def2dca5c34ecc5f96d2],
        "0x1283d9f872498556e11b48ec440d66ebe55c6624bc34b737ffb3939fc08203e": [0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8, 0x0124aeb495b947201f5fac96fd1138e326ad86195b98df6dec9009158a533b49],
        "0x68fa77586bc98d71125e342660ebdfb17a1c26027002af1dd8a620d93ea3ba3": [0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3, 0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac],
        "0x1eb8805c2f3cc4a7ac8ddde3f8b3e1d7d197053fa6050e318de2100e4eb2d18": [0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3, 0x0124aeb495b947201f5fac96fd1138e326ad86195b98df6dec9009158a533b49],
            }

    stables = ["USDT", "USDC", "DAI"]
    
    def __init__(self) -> None:
        new_supported_tokens = []
        for token in self.supported_tokens:
            if token in SETTINGS["Supported_tokens"]:
                new_supported_tokens.append(token)
        self.supported_tokens = new_supported_tokens

    async def check_existance(self, token1, token2, stable, sender):
        contract = Contract(0xeaf728d8e09bfbe5f11881f848ca647ba41593502347ed2ec5881e46b57a32, [{
        "name": "pairFor",
        "type": "function",
        "inputs": [
        {
            "name": "token0",
            "type": "felt"
        },
        {
            "name": "token1",
            "type": "felt"
        },
        {
            "name": "stable",
            "type": "felt"
        }
        ],
        "outputs": [
        {
            "name": "pair",
            "type": "felt"
        }
        ],
        "stateMutability": "view"
    }], sender.stark_native_account)

        res = hex((await contract.functions["pairFor"].call(token1, token2, stable)).pair)
        if res != "0x0":
            return True
        else:
            return False

    async def create_txn_for_swap(self, amount_in: float, token1: Token, amount_out: float, token2: Token, sender: BaseStarkAccount, full: bool = False):
        if token1.stable and token2.stable:
            stable = 1
        else:
            stable = 0

        if not await handle_dangerous_request(self.check_existance, "can't get pool info on sithswap", sender.formatted_hex_address, token1.contract_address, token2.contract_address, stable, sender):
            logger.error(f"[{sender.formatted_hex_address} got unsupported pool on sithswap. Skip")
            return -1
        
        if not full:
            call1 = token1.get_approve_call(amount_in, self.contract_address, sender)
            contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)
            call2 = contract.functions["swapExactTokensForTokensSupportingFeeOnTransferTokens"].prepare(
                int(amount_in*10**token1.decimals),
                int(amount_out*10**token2.decimals*(1-slippage)),
                [{
                    "from_address":token1.contract_address,
                    "to_address":token2.contract_address,
                    "stable":stable
                }],
                sender.stark_native_account.address,
                int(time.time())+3600
            )
        else:
            bal = await sender.get_balance(token1.contract_address, token1.symbol)
            if token1.symbol == "ETH":
                bal -= int(get_random_value(SETTINGS["SaveEthOnBalance"])*1e18)
            call1 = token1.get_approve_call_wei(bal, self.contract_address, sender)
            contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)
            call2 = contract.functions["swapExactTokensForTokensSupportingFeeOnTransferTokens"].prepare(
                bal,
                int(amount_out*10**token2.decimals*(1-slippage)),
                [{
                    "from_address":token1.contract_address,
                    "to_address":token2.contract_address,
                    "stable":stable
                }],
                sender.stark_native_account.address,
                int(time.time())+3600
            )

        return [call1, call2]

    async def create_txn_for_liq(self, amount1: float, token1: Token, amount2: float, token2: Token, sender: BaseStarkAccount):
        if token1.stable and token2.stable:
            stable = 1
        else:
            stable = 0
        call1 = token1.get_approve_call(amount1, self.contract_address, sender)
        call2 = token2.get_approve_call(amount2, self.contract_address, sender)
        contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)

        call3 = contract.functions["addLiquidity"].prepare(
            token1.contract_address,
            token2.contract_address,
            stable,
            int(amount1*10**token1.decimals),
            int(amount2*10**token2.decimals),
            int(amount1*10**token1.decimals * (1-slippage)),
            int(amount2*10**token2.decimals * (1-slippage)),
            sender.stark_native_account.address,
            int(time.time())+3600
        )

        return [call1, call2, call3]


    async def create_txn_for_remove_liq(self, lptoken: Token, sender: BaseStarkAccount):
        if lptoken.symbol.split(":")[0] in self.stables and lptoken.symbol.split(":")[1] in self.stables:
            stable = 1
        else:
            stable = 0
        amount = await sender.get_balance(lptoken.contract_address, lptoken.symbol)

        token1_address = self.tokens_from_lpt[hex(lptoken.contract_address)][0]
        token2_address = self.tokens_from_lpt[hex(lptoken.contract_address)][1]

        contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)
        token_contract = Contract(lptoken.contract_address, STARK_TOKEN_ABI, sender.stark_native_account)
        token1_contract = Contract(token1_address, STARK_TOKEN_ABI, sender.stark_native_account)
        token2_contract = Contract(token2_address, STARK_TOKEN_ABI, sender.stark_native_account)
        
        
        total_liq_amount = (await handle_dangerous_request(token_contract.functions["totalSupply"].call, "Can't get sithswap total pool value. Error:", sender.formatted_hex_address)).totalSupply
        multiplier = amount/total_liq_amount
        token1_val = (await handle_dangerous_request(token1_contract.functions["balanceOf"].call, "Can't get pool info. Error:", sender.formatted_hex_address, lptoken.contract_address)).balance
        token1_val = int(token1_val*multiplier)
        token2_val = (await handle_dangerous_request(token2_contract.functions["balanceOf"].call, "Can't get pool info. Error:", sender.formatted_hex_address, lptoken.contract_address)).balance
        token2_val = int(token2_val*multiplier)
        

        if amount <= 0:
            return -1
        
        call1 = lptoken.get_approve_call(amount, self.contract_address, sender)

        call2 = contract.functions["removeLiquidity"].prepare(
            token1_address,
            token2_address,
            stable,
            amount,
            int(token1_val*(1-slippage)),
            int(token2_val*(1-slippage)),
            sender.stark_native_account.address,
            int(time.time())+3600
        )
        
        return [call1, call2]