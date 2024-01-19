from time import time

from starknet_py.contract import Contract

from modules.base_classes.base_defi import BaseDEX
from modules.utils.utils import get_random_value, handle_dangerous_request
from modules.config import SETTINGS, SLIPPAGE
from modules.utils.token import StarkToken, STARK_TOKEN_ABI
from modules.utils.logger import logger
from modules.base_classes.base_account import BaseAccount


class TenKSwap(BaseDEX):
    name = "10kSwap"
    ABI = [{"name":"Uint256","size":2,"type":"struct","members":[{"name":"low","type":"felt","offset":0},{"name":"high","type":"felt","offset":1}]},{"name":"constructor","type":"constructor","inputs":[{"name":"factory","type":"felt"},{"name":"pairClass","type":"felt"}],"outputs":[]},{"name":"factory","type":"function","inputs":[],"outputs":[{"name":"factory","type":"felt"}],"stateMutability":"view"},{"name":"quote","type":"function","inputs":[{"name":"amountA","type":"Uint256"},{"name":"reserveA","type":"felt"},{"name":"reserveB","type":"felt"}],"outputs":[{"name":"amountB","type":"Uint256"}],"stateMutability":"view"},{"name":"getAmountOut","type":"function","inputs":[{"name":"amountIn","type":"Uint256"},{"name":"reserveIn","type":"felt"},{"name":"reserveOut","type":"felt"}],"outputs":[{"name":"amountOut","type":"Uint256"}],"stateMutability":"view"},{"name":"getAmountIn","type":"function","inputs":[{"name":"amountOut","type":"Uint256"},{"name":"reserveIn","type":"felt"},{"name":"reserveOut","type":"felt"}],"outputs":[{"name":"amountIn","type":"Uint256"}],"stateMutability":"view"},{"name":"getAmountsOut","type":"function","inputs":[{"name":"amountIn","type":"Uint256"},{"name":"path_len","type":"felt"},{"name":"path","type":"felt*"}],"outputs":[{"name":"amounts_len","type":"felt"},{"name":"amounts","type":"Uint256*"}],"stateMutability":"view"},{"name":"getAmountsIn","type":"function","inputs":[{"name":"amountOut","type":"Uint256"},{"name":"path_len","type":"felt"},{"name":"path","type":"felt*"}],"outputs":[{"name":"amounts_len","type":"felt"},{"name":"amounts","type":"Uint256*"}],"stateMutability":"view"},{"name":"addLiquidity","type":"function","inputs":[{"name":"tokenA","type":"felt"},{"name":"tokenB","type":"felt"},{"name":"amountADesired","type":"Uint256"},{"name":"amountBDesired","type":"Uint256"},{"name":"amountAMin","type":"Uint256"},{"name":"amountBMin","type":"Uint256"},{"name":"to","type":"felt"},{"name":"deadline","type":"felt"}],"outputs":[{"name":"amountA","type":"Uint256"},{"name":"amountB","type":"Uint256"},{"name":"liquidity","type":"Uint256"}]},{"name":"removeLiquidity","type":"function","inputs":[{"name":"tokenA","type":"felt"},{"name":"tokenB","type":"felt"},{"name":"liquidity","type":"Uint256"},{"name":"amountAMin","type":"Uint256"},{"name":"amountBMin","type":"Uint256"},{"name":"to","type":"felt"},{"name":"deadline","type":"felt"}],"outputs":[{"name":"amountA","type":"Uint256"},{"name":"amountB","type":"Uint256"}]},{"name":"swapExactTokensForTokens","type":"function","inputs":[{"name":"amountIn","type":"Uint256"},{"name":"amountOutMin","type":"Uint256"},{"name":"path_len","type":"felt"},{"name":"path","type":"felt*"},{"name":"to","type":"felt"},{"name":"deadline","type":"felt"}],"outputs":[{"name":"amounts_len","type":"felt"},{"name":"amounts","type":"Uint256*"}]},{"name":"swapTokensForExactTokens","type":"function","inputs":[{"name":"amountOut","type":"Uint256"},{"name":"amountInMax","type":"Uint256"},{"name":"path_len","type":"felt"},{"name":"path","type":"felt*"},{"name":"to","type":"felt"},{"name":"deadline","type":"felt"}],"outputs":[{"name":"amounts_len","type":"felt"},{"name":"amounts","type":"Uint256*"}]},{"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","type":"function","inputs":[{"name":"amountIn","type":"Uint256"},{"name":"amountOutMin","type":"Uint256"},{"name":"path_len","type":"felt"},{"name":"path","type":"felt*"},{"name":"to","type":"felt"},{"name":"deadline","type":"felt"}],"outputs":[]}]
    contract_address = 0x07a6f98c03379b9513ca84cca1373ff452a7462a3b61598f0af5bb27ad7f76d1
    supported_tokens = ["ETH", "USDT", "USDC", "DAI", "WBTC", "SHIT_COIN"]
    
    lpts = [
        StarkToken("ETH:USDT", 0x5900cfa2b50d53b097cb305d54e249e31f24f881885aae5639b0cd6af4ed298, 18),
        StarkToken("ETH:USDC", 0x23c72abdf49dffc85ae3ede714f2168ad384cc67d08524732acea90df325, 18),
        StarkToken("ETH:DAI", 0x17e9e62c04b50800d7c59454754fe31a2193c9c3c6c92c093f2ab0faadf8c87, 18),
        StarkToken("ETH:WBTC", 0x2a6e0ecda844736c4803a385fb1372eff458c365d2325c7d4e08032c7a908f3, 18),
        StarkToken("USDT:USDC", 0x41a708cf109737a50baa6cbeb9adf0bf8d97112dc6cc80c7a458cbad35328b0, 18),
        StarkToken("USDT:DAI", 0x41d52e15e82b003bf0ad52ca58393c87abef3e00f1bf69682fd4162d5773f8f, 18),
        StarkToken("USDT:WBTC", 0x50031010bcee2f43575b3afe197878e064e1a03c12f2ff437f29a2710e0b6ef, 18),
        StarkToken("USDC:DAI", 0x2e767b996c8d4594c73317bb102c2018b9036aee8eed08ace5f45b3568b94e5, 18),
        StarkToken("USDC:WBTC", 0x22e45d94d5c6c477d9efd440aad71b2c02a5cd5bed9a4d6da10bb7c19fd93ba, 18),
        StarkToken("DAI:WBTC", 0xf9d8f827734f5fd54571f0e78398033a3c1f1074a471cd4623f2aa45163718, 18)
    ]
    
    tokens_from_lpt = {
        "0x5900cfa2b50d53b097cb305d54e249e31f24f881885aae5639b0cd6af4ed298":[0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8],
        "0x23c72abdf49dffc85ae3ede714f2168ad384cc67d08524732acea90df325":[0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8],
        "0x17e9e62c04b50800d7c59454754fe31a2193c9c3c6c92c093f2ab0faadf8c87":[0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3],
        "0x2a6e0ecda844736c4803a385fb1372eff458c365d2325c7d4e08032c7a908f3":[0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac],
        "0x41a708cf109737a50baa6cbeb9adf0bf8d97112dc6cc80c7a458cbad35328b0":[0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8, 0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8],
        "0x41d52e15e82b003bf0ad52ca58393c87abef3e00f1bf69682fd4162d5773f8f":[0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8, 0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3],
        "0x50031010bcee2f43575b3afe197878e064e1a03c12f2ff437f29a2710e0b6ef":[0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8, 0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac],
        "0x2e767b996c8d4594c73317bb102c2018b9036aee8eed08ace5f45b3568b94e5":[0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8, 0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3],
        "0x22e45d94d5c6c477d9efd440aad71b2c02a5cd5bed9a4d6da10bb7c19fd93ba":[0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8, 0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac],
        "0xf9d8f827734f5fd54571f0e78398033a3c1f1074a471cd4623f2aa45163718":[0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3, 0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac]
    }

    
    def __init__(self) -> None:
        new_supported_tokens = []
        for token in self.supported_tokens:
            if token in SETTINGS["Supported_tokens"]:
                new_supported_tokens.append(token)
        self.supported_tokens = new_supported_tokens

    async def get_token1_for_token2_price(self, token1: StarkToken, token2: StarkToken, amount_in: float, sender: BaseAccount):
        contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)

        info = (await handle_dangerous_request(
            contract.functions["getAmountsOut"].call,
            "can't get pool info",
            sender.stark_address,
            int(amount_in*10**token1.decimals),
            (
                token1.contract_address,
                token2.contract_address
            )
        )).amounts
        amount_out = int(info[1])/10**token2.decimals
        return amount_in/amount_out

    async def create_txn_for_swap(self, amount_in: float, token1: StarkToken, amount_out: float, token2: StarkToken, sender: BaseAccount, full: bool = False):
        
        if not full:
            call1 = token1.get_approve_call(amount_in, self.contract_address, sender)
            contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)
            
            call2 = contract.functions["swapExactTokensForTokens"].prepare(
                int(amount_in*10**token1.decimals),
                int(amount_out*10**token2.decimals*(1-SLIPPAGE)),
                [
                    token1.contract_address,
                    token2.contract_address
                ],
                sender.stark_native_account.address,
                int(time()+(3600*24))
            )
        else:
            bal = (await sender.get_balance_starknet(token1))[0] - 1
            if token1.symbol == "ETH":
                bal -= int(get_random_value(SETTINGS["SaveEthOnBalance"])*1e18)
            call1 = token1.get_approve_call_wei(bal, self.contract_address, sender)
            contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)
            
            call2 = contract.functions["swapExactTokensForTokens"].prepare(
                bal,
                int(amount_out*10**token2.decimals*(1-SLIPPAGE)),
                [
                    token1.contract_address,
                    token2.contract_address
                ],
                sender.stark_native_account.address,
                int(time()+(3600*24))
            )

        return [call1, call2]

    async def create_txn_for_liq(self, amount1: float, token1: StarkToken, amount2: float, token2: StarkToken, sender: BaseAccount):
        
        call1 = token1.get_approve_call(amount1, self.contract_address, sender)
        call2 = token2.get_approve_call(amount2, self.contract_address, sender)
        contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)

        call3 = contract.functions["addLiquidity"].prepare(
            token1.contract_address,
            token2.contract_address,
            int(amount1*10**token1.decimals),
            int(amount2*10**token2.decimals),
            int(amount1*10**token1.decimals * (1-SLIPPAGE)),
            int(amount2*10**token2.decimals * (1-SLIPPAGE)),
            sender.stark_native_account.address,
            int(time())+3600
        )

        return [call1, call2, call3]


    async def create_txn_for_remove_liq(self, lptoken: StarkToken, sender: BaseAccount):
        amount = (await sender.get_balance_starknet(lptoken))[0]

        token1_address = self.tokens_from_lpt[hex(lptoken.contract_address)][0]
        token2_address = self.tokens_from_lpt[hex(lptoken.contract_address)][1]

        contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)
        token_contract = Contract(lptoken.contract_address, STARK_TOKEN_ABI, sender.stark_native_account)
        token1_contract = Contract(token1_address, STARK_TOKEN_ABI, sender.stark_native_account)
        token2_contract = Contract(token2_address, STARK_TOKEN_ABI, sender.stark_native_account)
        
        
        total_liq_amount = (await handle_dangerous_request(
            token_contract.functions["totalSupply"].call, 
            "Can't get 10kswap total pool value. Error:", 
            sender.stark_address
        )).totalSupply
        multiplier = amount/total_liq_amount
        
        token1_val = (await handle_dangerous_request(
            token1_contract.functions["balanceOf"].call, 
            "Can't get pool info. Error:", 
            sender.stark_address, 
            lptoken.contract_address
        )).balance
        token1_val = int(token1_val*multiplier)
        
        token2_val = (await handle_dangerous_request(
            token2_contract.functions["balanceOf"].call, 
            "Can't get pool info. Error:", 
            sender.stark_address, 
            lptoken.contract_address
        )).balance
        token2_val = int(token2_val*multiplier)
        

        if amount <= 0:
            return -1
        
        call1 = lptoken.get_approve_call(amount, self.contract_address, sender)

        call2 = contract.functions["removeLiquidity"].prepare(
            token1_address,
            token2_address,
            amount,
            int(token1_val*(1-SLIPPAGE)),
            int(token2_val*(1-SLIPPAGE)),
            sender.stark_native_account.address,
            int(time())+3600
        )
        
        return [call1, call2]