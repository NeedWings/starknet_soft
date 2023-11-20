from ..BaseClasses import *

class ZkLend(BaseLend):
    name = "ZkLend"
    ABI = [{"name":"ReserveData","size":16,"type":"struct","members":[{"name":"enabled","type":"felt","offset":0},{"name":"decimals","type":"felt","offset":1},{"name":"z_token_address","type":"felt","offset":2},{"name":"interest_rate_model","type":"felt","offset":3},{"name":"collateral_factor","type":"felt","offset":4},{"name":"borrow_factor","type":"felt","offset":5},{"name":"reserve_factor","type":"felt","offset":6},{"name":"last_update_timestamp","type":"felt","offset":7},{"name":"lending_accumulator","type":"felt","offset":8},{"name":"debt_accumulator","type":"felt","offset":9},{"name":"current_lending_rate","type":"felt","offset":10},{"name":"current_borrowing_rate","type":"felt","offset":11},{"name":"raw_total_debt","type":"felt","offset":12},{"name":"flash_loan_fee","type":"felt","offset":13},{"name":"liquidation_bonus","type":"felt","offset":14},{"name":"debt_limit","type":"felt","offset":15}]},{"data":[{"name":"token","type":"felt"},{"name":"z_token","type":"felt"},{"name":"decimals","type":"felt"},{"name":"interest_rate_model","type":"felt"},{"name":"collateral_factor","type":"felt"},{"name":"borrow_factor","type":"felt"},{"name":"reserve_factor","type":"felt"},{"name":"flash_loan_fee","type":"felt"},{"name":"liquidation_bonus","type":"felt"}],"keys":[],"name":"NewReserve","type":"event"},{"data":[{"name":"new_treasury","type":"felt"}],"keys":[],"name":"TreasuryUpdate","type":"event"},{"data":[{"name":"token","type":"felt"},{"name":"lending_accumulator","type":"felt"},{"name":"debt_accumulator","type":"felt"}],"keys":[],"name":"AccumulatorsSync","type":"event"},{"data":[{"name":"token","type":"felt"},{"name":"lending_rate","type":"felt"},{"name":"borrowing_rate","type":"felt"}],"keys":[],"name":"InterestRatesSync","type":"event"},{"data":[{"name":"token","type":"felt"},{"name":"limit","type":"felt"}],"keys":[],"name":"DebtLimitUpdate","type":"event"},{"data":[{"name":"user","type":"felt"},{"name":"token","type":"felt"},{"name":"face_amount","type":"felt"}],"keys":[],"name":"Deposit","type":"event"},{"data":[{"name":"user","type":"felt"},{"name":"token","type":"felt"},{"name":"face_amount","type":"felt"}],"keys":[],"name":"Withdrawal","type":"event"},{"data":[{"name":"user","type":"felt"},{"name":"token","type":"felt"},{"name":"raw_amount","type":"felt"},{"name":"face_amount","type":"felt"}],"keys":[],"name":"Borrowing","type":"event"},{"data":[{"name":"repayer","type":"felt"},{"name":"beneficiary","type":"felt"},{"name":"token","type":"felt"},{"name":"raw_amount","type":"felt"},{"name":"face_amount","type":"felt"}],"keys":[],"name":"Repayment","type":"event"},{"data":[{"name":"liquidator","type":"felt"},{"name":"user","type":"felt"},{"name":"debt_token","type":"felt"},{"name":"debt_raw_amount","type":"felt"},{"name":"debt_face_amount","type":"felt"},{"name":"collateral_token","type":"felt"},{"name":"collateral_amount","type":"felt"}],"keys":[],"name":"Liquidation","type":"event"},{"data":[{"name":"initiator","type":"felt"},{"name":"receiver","type":"felt"},{"name":"token","type":"felt"},{"name":"amount","type":"felt"},{"name":"fee","type":"felt"}],"keys":[],"name":"FlashLoan","type":"event"},{"data":[{"name":"user","type":"felt"},{"name":"token","type":"felt"}],"keys":[],"name":"CollateralEnabled","type":"event"},{"data":[{"name":"user","type":"felt"},{"name":"token","type":"felt"}],"keys":[],"name":"CollateralDisabled","type":"event"},{"data":[{"name":"new_class_hash","type":"felt"}],"keys":[],"name":"ContractUpgraded","type":"event"},{"data":[{"name":"previousOwner","type":"felt"},{"name":"newOwner","type":"felt"}],"keys":[],"name":"OwnershipTransferred","type":"event"},{"name":"constructor","type":"constructor","inputs":[{"name":"owner","type":"felt"},{"name":"_oracle","type":"felt"}],"outputs":[]},{"name":"upgrade","type":"function","inputs":[{"name":"new_implementation","type":"felt"}],"outputs":[]},{"name":"get_reserve_data","type":"function","inputs":[{"name":"token","type":"felt"}],"outputs":[{"name":"data","type":"ReserveData"}],"stateMutability":"view"},{"name":"get_lending_accumulator","type":"function","inputs":[{"name":"token","type":"felt"}],"outputs":[{"name":"res","type":"felt"}],"stateMutability":"view"},{"name":"get_debt_accumulator","type":"function","inputs":[{"name":"token","type":"felt"}],"outputs":[{"name":"res","type":"felt"}],"stateMutability":"view"},{"name":"get_pending_treasury_amount","type":"function","inputs":[{"name":"token","type":"felt"}],"outputs":[{"name":"res","type":"felt"}],"stateMutability":"view"},{"name":"get_total_debt_for_token","type":"function","inputs":[{"name":"token","type":"felt"}],"outputs":[{"name":"debt","type":"felt"}],"stateMutability":"view"},{"name":"get_user_debt_for_token","type":"function","inputs":[{"name":"user","type":"felt"},{"name":"token","type":"felt"}],"outputs":[{"name":"debt","type":"felt"}],"stateMutability":"view"},{"name":"get_user_flags","type":"function","inputs":[{"name":"user","type":"felt"}],"outputs":[{"name":"map","type":"felt"}],"stateMutability":"view"},{"name":"is_user_undercollateralized","type":"function","inputs":[{"name":"user","type":"felt"},{"name":"apply_borrow_factor","type":"felt"}],"outputs":[{"name":"is_undercollateralized","type":"felt"}],"stateMutability":"view"},{"name":"is_collateral_enabled","type":"function","inputs":[{"name":"user","type":"felt"},{"name":"token","type":"felt"}],"outputs":[{"name":"enabled","type":"felt"}],"stateMutability":"view"},{"name":"user_has_debt","type":"function","inputs":[{"name":"user","type":"felt"}],"outputs":[{"name":"has_debt","type":"felt"}],"stateMutability":"view"},{"name":"deposit","type":"function","inputs":[{"name":"token","type":"felt"},{"name":"amount","type":"felt"}],"outputs":[]},{"name":"withdraw","type":"function","inputs":[{"name":"token","type":"felt"},{"name":"amount","type":"felt"}],"outputs":[]},{"name":"withdraw_all","type":"function","inputs":[{"name":"token","type":"felt"}],"outputs":[]},{"name":"borrow","type":"function","inputs":[{"name":"token","type":"felt"},{"name":"amount","type":"felt"}],"outputs":[]},{"name":"repay","type":"function","inputs":[{"name":"token","type":"felt"},{"name":"amount","type":"felt"}],"outputs":[]},{"name":"repay_for","type":"function","inputs":[{"name":"token","type":"felt"},{"name":"amount","type":"felt"},{"name":"beneficiary","type":"felt"}],"outputs":[]},{"name":"repay_all","type":"function","inputs":[{"name":"token","type":"felt"}],"outputs":[]},{"name":"enable_collateral","type":"function","inputs":[{"name":"token","type":"felt"}],"outputs":[]},{"name":"disable_collateral","type":"function","inputs":[{"name":"token","type":"felt"}],"outputs":[]},{"name":"liquidate","type":"function","inputs":[{"name":"user","type":"felt"},{"name":"debt_token","type":"felt"},{"name":"amount","type":"felt"},{"name":"collateral_token","type":"felt"}],"outputs":[]},{"name":"flash_loan","type":"function","inputs":[{"name":"receiver","type":"felt"},{"name":"token","type":"felt"},{"name":"amount","type":"felt"},{"name":"calldata_len","type":"felt"},{"name":"calldata","type":"felt*"}],"outputs":[]},{"name":"add_reserve","type":"function","inputs":[{"name":"token","type":"felt"},{"name":"z_token","type":"felt"},{"name":"interest_rate_model","type":"felt"},{"name":"collateral_factor","type":"felt"},{"name":"borrow_factor","type":"felt"},{"name":"reserve_factor","type":"felt"},{"name":"flash_loan_fee","type":"felt"},{"name":"liquidation_bonus","type":"felt"}],"outputs":[]},{"name":"set_treasury","type":"function","inputs":[{"name":"new_treasury","type":"felt"}],"outputs":[]},{"name":"set_debt_limit","type":"function","inputs":[{"name":"token","type":"felt"},{"name":"limit","type":"felt"}],"outputs":[]},{"name":"transfer_ownership","type":"function","inputs":[{"name":"new_owner","type":"felt"}],"outputs":[]},{"name":"renounce_ownership","type":"function","inputs":[],"outputs":[]}]
    contract_address = 0x04c0a5193d58f74fbace4b74dcf65481e734ed1714121bdc571da345540efa05
    supported_tokens = ["ETH", "USDC", "USDT", "DAI", "WBTC"]
    token_from_name = {
        "ETH" : Token("ETH", 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 18),
        "USDC": Token("USDC", 0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8, 6, stable=True),
        "USDT": Token("USDT", 0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8, 6, stable=True),
        "DAI": Token("DAI", 0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3, 18, stable=True),
        "WBTC": Token("WBTC", 0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac, 8)
    }

    lend_tokens = [
        Token("ETH-SUPPLIED", 0x01b5bd713e72fdc5d63ffd83762f81297f6175a5e0a4771cdadbc1dd5fe72cb1, 18),
        Token("WBTC-SUPPLIED", 0x02b9ea3acdb23da566cee8e8beae3125a1458e720dea68c4a9a7a2d8eb5bbb4a, 8),
        Token("USDT-SUPPLIED", 0x00811d8da5dc8a2206ea7fd0b28627c2d77280a515126e62baa4d78e22714c4a, 6),
        Token("USDC-SUPPLIED", 0x047ad51726d891f972e74e4ad858a261b43869f7126ce7436ee0b2529a98f486, 6),
        Token("DAI-SUPPLIED", 0x062fa7afe1ca2992f8d8015385a279f49fad36299754fb1e9866f4f052289376, 18)
    ]

    lend_token_from_token_name = {
        "ETH": lend_tokens[0],
        "WBTC": lend_tokens[1],
        "USDT": lend_tokens[2],
        "USDC": lend_tokens[3],
        "DAI": lend_tokens[4],
    }
    coeffs_for_supply = {
        "ETH": 0.8,
        "WBTC": 0.7,
        "USDT": 0.7,
        "USDC": 0.8,
        "DAI": 0.7,
    }

    coeffs_for_borrow = {
        "ETH": 1,
        "WBTC": 0.91,
        "USDT": 0.91,
        "USDC": 1,
        "DAI": 0.91,
    }

    async def get_prices(self, sender: BaseStarkAccount, proxy=None):
        proxies = {'https': proxy, 'http': proxy} if proxy else None
        while True:
            try:
                r = req("https://data.app.zklend.com/pools", proxies=proxies)
                break
            except Exception as e:
                logger.error(f"[{sender.formatted_hex_address}] can't get zklend prices: {e} trying again")
        res = {}
        for info in r:
            res[info["token"]["symbol"].upper()] = int(info["price"]["price"], 16)/1e8
        return res

    async def get_total_borrowed(self, sender: BaseStarkAccount):
        prices = await self.get_prices(sender)
        val = 0
        contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)
        for token_name in self.supported_tokens:
            token = self.token_from_name[token_name]
            val_in_token_wei = (await handle_dangerous_request(contract.functions["get_user_debt_for_token"].call, f"can't get borrowed {token_name}", sender.formatted_hex_address, sender.stark_native_account.address, token.contract_address)).debt

            val_in_token = val_in_token_wei/10**token.decimals

            val += (prices[token_name]*val_in_token)/self.coeffs_for_borrow[token.symbol]
        
        return val

    async def get_total_supplied(self, sender: BaseStarkAccount):
        prices = await self.get_prices(sender)
        val = 0

        for token_name in self.supported_tokens:
            token = self.token_from_name[token_name]
            lend_token = self.lend_token_from_token_name[token_name]

            lend_token_val_wei = await handle_dangerous_request(sender.stark_native_account.get_balance, f"can't get balance of {lend_token.symbol} Error:", sender.formatted_hex_address, lend_token.contract_address)

            val_in_token = lend_token_val_wei/10**lend_token.decimals

            usd_val = (prices[token_name]*val_in_token) * self.coeffs_for_supply[token.symbol]
            
            val += usd_val

        return val
    
    async def create_txn_for_adding_token(self, token: Token, amount: int, sender: BaseStarkAccount):
        contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)

        call1 = token.get_approve_call(amount, self.contract_address, sender)
        call2 = contract.functions["deposit"].prepare(
            token.contract_address,
            amount
        )

        coll_enabled = (await handle_dangerous_request(contract.functions["is_collateral_enabled"].call, "can't check for collateral Error", sender.formatted_hex_address, sender.stark_native_account.address, token.contract_address)).enabled

        if coll_enabled == 0:
            call3 = contract.functions["enable_collateral"].prepare(
                token.contract_address
            )
            return 0, [call1, call3, call2]
        return 0, [call1, call2]

    async def create_txn_for_removing_token(self, amount: int, token: Token, sender: BaseStarkAccount):
        prices = await self.get_prices(sender)
        contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)
        stark_token: Token = self.token_from_name[token.symbol.split("-")[0]]
        usd_val = (amount/10**stark_token.decimals)*prices[stark_token.symbol]
        total_borroved = await self.get_total_borrowed(sender)
        total_supplied = await self.get_total_supplied(sender)
        usd_delta = total_supplied-total_borroved

        if usd_val > usd_delta:
            usd_val = usd_delta
            usd_val = usd_val/self.coeffs_for_supply[stark_token.symbol]
        
        price = prices[stark_token.symbol]

        token_val = int((usd_val/price)*10**stark_token.decimals)
        token_val = int(token_val*0.99988)
        token_bal = await sender.get_balance(token.contract_address, token.symbol) - 1
        if token_val > token_bal:
            token_val = token_bal
        if token_val <= 1:
            return -1, 'Zklend\tLiquidity is 1'
        call1 = contract.functions["withdraw"].prepare(
            stark_token.contract_address,
            token_val
        )

        return 0, [call1]
        
    async def create_txn_for_borrow(self, amount: float, token: Token, sender: BaseStarkAccount):
        contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)

        call = contract.functions["borrow"].prepare(
            token.contract_address,
            int(amount*10**token.decimals)
        )

        return 0, [call]

    async def create_txn_for_return(self, token: Token, sender: BaseStarkAccount):
        contract = Contract(self.contract_address, self.ABI, sender.stark_native_account)
        val_in_token_wei = (await handle_dangerous_request(contract.functions["get_user_debt_for_token"].call, f"can't get borrowed {token.symbol}", sender.formatted_hex_address, sender.stark_native_account.address, token.contract_address)).debt
        
        bal = await sender.get_balance(token.contract_address, token.symbol)
        if val_in_token_wei >= bal:
            val_in_token_wei = bal
        if val_in_token_wei <= 1:
            return -1, 'Sithswap\tReturn is 0'
        call1 = token.get_approve_call_wei(val_in_token_wei, self.contract_address, sender)

        call2 = contract.functions["repay"].prepare(
            token.contract_address,
            val_in_token_wei
        )

        return 0, [call1, call2]
        
