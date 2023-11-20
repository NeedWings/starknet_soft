from .DEXes.avnu import *
from .DEXes.fibrous import *
from .DEXes.jediswap import *
from .DEXes.myswap import *
from .DEXes.sithswap import *
from .DEXes.tenkswap import *
from .DEXes.zklend import *
from .braavos_shit import *
from .DEXes.domain import *
from .DEXes.okx_sender import *
from .DEXes.bids import *
from .DEXes.dmail import *
from .own_tasks import *
from .DEXes.starkstars import *
from .stats import stat


eth = Token("ETH", 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 18)
usdc = Token("USDC", 0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8, 6, stable=True)
usdt = Token("USDT", 0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8, 6, stable=True)
dai = Token("DAI", 0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3, 18, stable=True)
wbtc = Token("WBTC", 0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac, 8)
wsteth = Token("WSTETH", 0x042b8f0484674ca266ac5d08e4ac6a3fe65bd3129795def2dca5c34ecc5f96d2, 18)
lords = Token("LORDS", 0x0124aeb495b947201f5fac96fd1138e326ad86195b98df6dec9009158a533b49, 18)

domain_hand = StarkId()
sender_hand = Sender()
stars_hand = StarkStars()

tokens = {
    "ETH": eth,
    "USDT": usdt,
    "USDC": usdc,
    "DAI": dai,
    "WBTC": wbtc,
    "WSTETH": wsteth,
    "LORDS": lords
    }

swap_dexes = {
    'Avnu': Avnu(),
    'Fibrous': Fibrous(),
    'JediSwap': JediSwap(),
    'MySwap': MySwap(),
    'SithSwap': SithSwap(),
    'TenKSwap': TenKSwap()
    }

liq_dexes = {
    'JediSwap': JediSwap(),
    'MySwap': MySwap(),
    'SithSwap': SithSwap(),
    'TenKSwap': TenKSwap()
    }

lends = {
    'ZkLend': ZkLend()
    }


class AccRouter():
    def __init__(self, wallet, starknet_rpc, proxy=None) -> None:
        self.proxy = proxy
        self.wallet = wallet
        acc_init = {
            'stark_key': wallet.argent_key,
            'provider': wallet.argent_provider,
            'stark_rpc': starknet_rpc,
            'proxy': proxy
            }
        self.account = StarkAccount(**acc_init)
        self.address = self.account.formatted_hex_address

    def tokens_to_list(self, token_list):
        return [tokens[token] for token in token_list]
    
    async def starkstars(self):
        calldata = await stars_hand.create_tnx_for_mint(self.account, eth)
        status, tx = await self.account.send_txn(calldata)
        return status, tx

    async def bids(self, flex):
        calldata = await bidder.create_bid_tx(eth, self.account, flex)
        status, tx = await self.account.send_txn(calldata)
        return status, tx

    async def okx(self, WithdrawShare=None, okx_starknet_address=None):
        okx_starknet_address = okx_starknet_address if okx_starknet_address else self.wallet.okx_starknet_address
        if not okx_starknet_address:
            return -1, 'No okx address for this wallet'
        status, txn = await sender_hand.create_txn(eth, okx_starknet_address, self.account, WithdrawShare)
        if status < 0:
            return status, txn
        status, tx_result = await self.account.send_txn(txn)
        if status < 0:
            return status, tx_result
        return 0, tx_result
    
    async def new_id(self):
        status, tx = await self.account.send_txn(await domain_hand.create_txn(eth, self.account))
        return status, tx

    async def bridge_to_evm(
        self,
        WithdrawShare=None,
        distNet="ethereum"
        ):
        account = self.account.stark_native_account
        wallet = self.wallet.eth_address

        balance = await self.account.get_balance()/1e18
        amount = balance * WithdrawShare

        if amount < 0.006:
            return -1, 'amount to bridge less than minimal amount'

        match distNet:
            case "ethereum":
                amount = int((get_orbiter_value(amount) * decimal.Decimal(1e18)) - 3)
            case "arbitrum":
                amount = int((get_orbiter_value(amount) * decimal.Decimal(1e18)) - 2)
            case "zksync":
                amount = int((get_orbiter_value(amount) * decimal.Decimal(1e18)) + 10)
            case "linea":
                amount = int((get_orbiter_value(amount) * decimal.Decimal(1e18)) + 19)
            case _:
                return -1, 'Uknown distNet'
        contract = Contract(eth.contract_address, STARK_TOKEN_ABI, account)
        approve_call = contract.functions["approve"].prepare(
            ORBITER_STARK_CONTRACT, int(amount)
        )
        contract = Contract(ORBITER_STARK_CONTRACT, ORBITER_STARK_ABI, account)
        call = contract.functions["transferERC20"].prepare(
                eth.contract_address,
                0x64a24243f2aabae8d2148fa878276e6e6e452e3941b417f3c33b1649ea83e11,
                int(amount),
                int(wallet, 16)
                )

        calldata = [approve_call, call]

        status, result = await self.account.send_txn(calldata)
        return status, result

    async def stark_id(self):
        id_contract = Contract(0x05dbdedc203e92749e2e746e2d40a768d966bd243df04a6b712e222bc040a9af, [{"name":"mint","type":"function","inputs":[{"name":"starknet_id","type":"felt"}],"outputs":[]}], self.account.stark_native_account)
        #logger.info(f"[{self.account.formatted_hex_address}] going to mint starknet id")
        call = id_contract.functions["mint"].prepare(
            random.randint(0, 999999999999)
        )
        calldata = [call]
        status, tx = await self.account.send_txn(calldata)
        return status, tx

    async def dmail(self):
        calldata = await dmail_hand.create_txn_for_dmail(self.account)
        status, tx = await self.account.send_txn(calldata)
        return status, tx

    async def collateral(
        self,
        zklend_collateral_amount=None
        ):
        account = self.account.stark_native_account
        for i in range(get_random_value_int(zklend_collateral_amount if zklend_collateral_amount else SETTINGS["zklend_collateral_amount"])):
            lend_contract = Contract(ZkLend().contract_address, ZkLend().ABI, self.account.stark_native_account)
            call3 = lend_contract.functions["enable_collateral"].prepare(
                    eth.contract_address
                )
            calldata = [call3]
            logger.info(f"[{self.account.formatted_hex_address}] enabling collateral")
            await self.account.send_txn(calldata)
            await sleeping(self.account.formatted_hex_address)
            call3 = lend_contract.functions["disable_collateral"].prepare(
                    eth.contract_address
                )
            calldata = [call3]
            logger.info(f"[{self.account.formatted_hex_address}] disabling collateral")
            await self.account.send_txn(calldata)
            await sleeping(self.account.formatted_hex_address)

    async def get_max_valued_token(
        self,
        token_list,
        SaveEthOnBalance=None,
        min_swap_values={}
        ):
        max_valued = None
        max_value = 0
        for token in token_list:
            balance = await self.account.get_balance(token.contract_address, token.symbol)
            if token.symbol == "ETH":
                balance = balance - get_random_value(SaveEthOnBalance if SaveEthOnBalance else SETTINGS["SaveEthOnBalance"])*1e18
                logger.info(f"[{self.account.formatted_hex_address}] {token.symbol} balance: {balance/10**token.decimals}")
            else:
                if balance/10**token.decimals < (min_swap_values if min_swap_values else SETTINGS["min_swap_values"])[token.symbol]:
                    balance = 0
                    logger.info(f"[{self.account.formatted_hex_address}] {token.symbol} balance below min_swap_values, will count as 0")
                else:
                    logger.info(f"[{self.account.formatted_hex_address}] {token.symbol} balance: {balance/10**token.decimals}")
            usd_value = token.get_usd_value(balance/10**token.decimals)
            if usd_value>max_value:
                max_valued = token
                max_value = usd_value
        return max_valued, max_value

    async def get_max_valued_token_unsafe(
        self,
        token_list
        ):
        max_valued = None
        max_value = 0
        for token in token_list:
            balance = await self.account.get_balance(token.contract_address, token.symbol)
            usd_value = token.get_usd_value(balance/10**token.decimals)
            if usd_value>max_value:
                max_valued = token
                max_value = usd_value
        return max_valued, max_value

    async def get_tokens(
        self,
        token_list
        ):
        for token in token_list:
            balance = await self.account.get_balance(token.contract_address, token.symbol)
            usd_value = token.get_usd_value(balance/10**token.decimals)
        return max_valued, max_value

    async def swaps_handler(
        self,
        dex=None,
        token_in=None,
        token_out=None,
        WorkPercent=None,
        SaveEthOnBalance=None,
        min_swap_values={}
        ):
        if not dex:
            return -1, 'No dex specified'
        dex = swap_dexes[dex]
        try:
            if not token_in:
                token_in, usd_value =  await self.get_max_valued_token(self.tokens_to_list(dex.supported_tokens), SaveEthOnBalance, min_swap_values)
                if token_in == None:
                    logger.error(f"[{self.account.formatted_hex_address}] all balances is 0")
                    return -1, 'Not enough balance'
            else:
                token_in = tokens[token_in]
            balance = await self.account.get_balance(token_in.contract_address, token_in.symbol)
            token_out = tokens[token_out] if token_out else tokens[dex.get_pair(token_in.symbol)]
            
            token_in_val = int(balance * get_random_value(WorkPercent if WorkPercent else SETTINGS["WorkPercent"]))
            token_out_val = int((token_in_val * token_in.get_price(self.proxy)) / token_out.get_price(self.proxy))

            #logger.info(f"[{self.account.formatted_hex_address}] going to swap {token1_val} {token1.symbol} for {token2.symbol} in {dex.name}")

            status, swap_txn = await dex.create_txn_for_swap(token_in_val, token_in, token_out_val, token_out, self.account)
            if status < 0:
                return -1, f'Failed to create tx for swap because of: {swap_txn}'
            
            status, swap_result = await self.account.send_txn(swap_txn)
            if status < 0:
                return -1, f'Failed to send tx: {swap_result}'
            
            return 0, swap_result
        except Exception:
            return -1, traceback.format_exc().replace('\n', '\t')
    
    async def liq_add(
        self,
        liq=None,
        LiqWorkPercent=None,
        Slippage=None,
        SaveEthOnBalance=None,
        min_swap_values={}
        ):
        if not liq:
            return -1, 'No liq_dex specified'
        liq = liq_dexes[liq]
        try:
            token1, usd_value = await self.get_max_valued_token(self.tokens_to_list(liq.supported_tokens), SaveEthOnBalance, min_swap_values)
            if token1 == None:
                return -1, 'all balances are 0'

            token2 = tokens[liq.get_pair(token1.symbol)]

            amount_to_add = usd_value * get_random_value(LiqWorkPercent if LiqWorkPercent else SETTINGS["LiqWorkPercent"])/2
            token2_usd_value = token2.get_usd_value(await self.account.get_balance(token2.contract_address, token2.symbol) / 10**token2.decimals)
            amount1 = amount_to_add/token1.get_price(self.proxy)
            amount2 = amount_to_add/token2.get_price(self.proxy)
            logger.info(f"[{self.account.formatted_hex_address}] going to add liquidity in {dex.name} in {token1.symbol}/{token2.symbol} pair for {amount1} {token1.symbol} and {amount2} {token2.symbol}")
                
            if token2_usd_value < amount_to_add*(1+ (Slippage if Slippage else SETTINGS["Slippage"]+0.01)):
                return -1, 'token2_usd_value is less than amount_to_add*(1+Slippage)'

            status, liq_txn = await liq.create_txn_for_liq(amount1, token1, amount2, token2, self.account)
            if status < 0:
                return -1, liq_txn

            status, liq_result = await self.account.send_txn(liq_txn)
            if status < 0:
                return -1, liq_result

            return 0, liq_result
        except Exception:
            return -1, traceback.format_exc().replace('\n', '\t')

    async def lend_add(
        self,
        lend=None,
        token_in=None,
        LendWorkPercent=None
        ):
        if not lend:
            return -1, 'No lend specified'
        if not token_in:
            return -1, 'No token_to_swap specified'
        lend = lends[lend]
        token_in = tokens[token_in]
        try:
            balance = await self.account.get_balance(token_in.contract_address, token_in.symbol)
            
            amount_to_add = int(balance * get_random_value(LendWorkPercent if LendWorkPercent else SETTINGS["LendWorkPercent"]))
            
            logger.info(f"[{self.account.formatted_hex_address}] going to add {amount_to_add/10**token_in.decimals} {token_in.symbol} in {lend.name}")

            status, lend_txn = await lend.create_txn_for_adding_token(token_in, amount_to_add, self.account)
            if status < 0:
                return -1, lend_txn
            status, lend_result = await self.account.send_txn(lend_txn)
            if status < 0:
                return -1, lend_result
            
            return 0, lend_result
        except Exception:
            return -1, traceback.format_exc().replace('\n', '\t')

    async def lend_return(
        self,
        lend=None
        ):
        if not lend:
            return -1, 'No lend specified'
        lend = lends[lend]
        lend_tokens = lend.lend_tokens.copy()
        shuffle(lend_tokens)
        for token in lend_tokens:
            token: Token
            balance = await self.account.get_balance(token.contract_address, token.symbol)
            balance = int(balance)
            if balance <= 0:
                logger.info(f"[{self.account.formatted_hex_address}] Supplied {token.symbol} is 0. Skip")
                continue
            logger.info(f"[{self.account.formatted_hex_address}] going to return {token.symbol} from {lend.name}")
            status, txn = await lend.create_txn_for_removing_token(balance, token, self.account)
            if status < 0:
                logger.info(f"[{self.account.formatted_hex_address}] not enough repayed for removing. Skip")
                continue
                #return -1, 'Not enough repayed for removing. Skip'
            status, lend_result= await self.account.send_txn(txn)
            return status, lend_result

    async def lend_borrow(
        self,
        lend=None,
        LendWorkPercent=None,
        BorrowAddAmount=None,
        BorrowWorkPercent=None,
        SaveEthOnBalance=None,
        min_swap_values=None
        ):
        if not lend:
            return -1, 'No lend specified'
        lend = lends[lend]
        try:
            token = tokens[random.choice(lend.supported_tokens)]

            
            total_borroved = await lend.get_total_borrowed(self.account)
            total_supplied = await lend.get_total_supplied(self.account)
            usd_val = total_supplied - total_borroved

            
            to_borrow_usd = (usd_val)*get_random_value(BorrowWorkPercent if BorrowWorkPercent else SETTINGS["BorrowWorkPercent"])*lend.coeffs_for_borrow[token.symbol]
            if to_borrow_usd == 0:
                return status, 'Amount to borrow is 0'
            
            amount = to_borrow_usd/token.get_price()
            logger.info(f"[{self.account.formatted_hex_address}] going to borrow {amount} {token.symbol} in {lend.name}")

            status, txn = await lend.create_txn_for_borrow(amount, token, self.account)
            if status < 0:
                return -1, txn
            status, lend_result = await self.account.send_txn(txn)
            if status < 0:
                return status, lend_result
        except Exception:
            return -1, traceback.format_exc().replace('\n', '\t')

    async def lend_repay(self, lend=None):
        if not lend:
            return -1, 'No lend specified'
        lend = lends[lend]
        try:
            logger.info(f"[{self.account.formatted_hex_address}] going to repay {amount} {token.symbol} in {lend.name}")
            status, lend_txn = await lend.create_txn_for_return(token, self.account)
            if status < 0:
                return status, lend_txn
            status, lend_result = await self.account.send_txn(lend_txn)
            if status < 0:
                return status, lend_result
            return 0, lend_result
        except Exception:
            return -1, traceback.format_exc().replace('\n', '\t')

    async def swap(
        self,
        dex=None,
        token_in=None,
        token_out="ETH",
        SaveEthOnBalance=None,
        StableShareToSwap=None,
        min_swap_values={},
        ):
        if not dex:
            return -1, 'No dex specified'
        if not token_in:
            return -1, 'No token_to_swap specified'
        if token_out == token_in:
            return -1, 'Token_to_swap and token_out are the same'

        dex = swap_dexes[dex]
        if token_in not in dex.supported_tokens:
            return -1, f'{dex.name} does not support {token_in.symbol}'

        token_out = tokens[token_out]
        token_in = tokens[token_in]
        try:
            balance_total = await self.account.get_balance(token_in.contract_address, token_in.symbol)

            if token_in.symbol == "ETH":
                balance = balance_total - int(get_random_value(SaveEthOnBalance if SaveEthOnBalance else SETTINGS["SaveEthOnBalance"])*1e18)
            else:
                balance = int(balance_total * get_random_value(StableShareToSwap if StableShareToSwap else SETTINGS['StableShareToSwap']))
                if balance/10**token_in.decimals < (min_swap_values if min_swap_values else SETTINGS["min_swap_values"])[token_in.symbol]:
                    balance = 0

            if balance <=0:
                return -1, f'Total balance is {balance_total} which is less than min_swap_values. skip'

            usd_val = token_in.get_usd_value(balance/10**token_in.decimals)
            amount_out = usd_val/token_out.get_price()

            status, swap_txn = await dex.create_txn_for_swap(balance/10**token_in.decimals, token_in, amount_out, token_out, self.account, full = False)
            if status < 0:
                return status, f'Failed to create tx for swap because of: {swap_txn}'
            
            status, swap_result = await self.account.send_txn(swap_txn)
            if status < 0:
                return status, f'Failed to send tx: {swap_result}'

            return 0, swap_result

        except Exception:
            return -1, traceback.format_exc().replace('\n', '\t')

    async def full(
        self,
        RemoveOnFullMode=None,
        SwapAtTheEnd=None,
        toSaveFunds=None
        ):
        ways = [1,2,3,4,5]
        shuffle(ways)
        for way in ways:
            print(way)
            if way == 1:
                await self.swaps_handler()
            elif way == 2:
                await self.liq_handler()
                if random.choice(RemoveOnFullMode if RemoveOnFullMode else SETTINGS["RemoveOnFullMode"]):
                    await self.remove_liq()
            elif way == 3:
                await self.lend_router()
                if random.choice(RemoveOnFullMode if RemoveOnFullMode else SETTINGS["RemoveOnFullMode"]):
                    await self.return_borrowed()
                    await self.remove_from_lend()
            elif way == 4:
                await self.dmail()
            elif way == 5:
                await self.collateral()
            
        if random.choice(SwapAtTheEnd if SwapAtTheEnd else SETTINGS["SwapAtTheEnd"]):
            await self.swap_to_one_token(random.choice(toSaveFunds if toSaveFunds else SETTINGS["toSaveFunds"]))

    async def full_withdraw(self, wallet = None):
        await self.return_all_borrowed()
        await self.remove_all_from_lend()
        await self.remove_all_liq()
        await self.swap_to_one_token()
        await self.withdraw(wallet)

    async def remove_all_liq(self):
        dexes = list(liq_dexes.values())
        shuffle(dexes)
        for dex in dexes:
            dex: BaseDex
            lptokens = dex.lpts.copy()
            shuffle(lptokens)
            for lpt in lptokens:
                lpt: LPToken
                balance = await self.account.get_balance(lpt.contract_address, lpt.symbol)

                if balance <= 0:
                    logger.info(f"[{self.account.formatted_hex_address}] {lpt.symbol} pool value is 0. Skip")
                    continue

                txn = await dex.create_txn_for_remove_liq(lpt, self.account)

                if txn == -1:
                    continue
                logger.info(f"[{self.account.formatted_hex_address}] going to remove {lpt.symbol} in {dex.name}")
                await self.account.send_txn(txn)
                await sleeping(self.account.formatted_hex_address)

    async def remove_all_from_lend(self):
        for lend in lends.values():
            lend: BaseLend
            lend_tokens = lend.lend_tokens.copy()
            shuffle(lend_tokens)
            for token in lend_tokens:
                token: Token
                balance = await self.account.get_balance(token.contract_address, token.symbol)
                balance = int(balance)
                if balance <= 0:
                    logger.info(f"[{self.account.formatted_hex_address}] Supplied {token.symbol} is 0. Skip")
                    continue
                logger.info(f"[{self.account.formatted_hex_address}] going to return {token.symbol} from {lend.name}")
                txn = await lend.create_txn_for_removing_token(balance, token, self.account)
                if txn[0] == -1:
                    logger.info(f"[{self.account.formatted_hex_address}] not enough repayed for removing. Skip")
                    continue
                    #return -1, 'Not enough repayed for removing. Skip'
                await self.account.send_txn(txn)

                await sleeping(self.account.formatted_hex_address)

    async def return_all_borrowed(self):
        for lend in lends.values():
            token_list = self.tokens_to_list(lend.tokens).copy()
            shuffle(token_list)
            for token in token_list:
                try:
                    txn = await lend.create_txn_for_return(token, self.account)
                    if txn[0] == -1:
                        continue
                    logger.info(f"[{self.account.formatted_hex_address}] going to return borroved {token.symbol}")
                    await self.account.send_txn(txn)

                    await sleeping(self.account.formatted_hex_address)

                except Exception as e:
                    logger.error(f"[{self.account.formatted_hex_address}] got erroor: {e}")
                    await sleeping(self.account.formatted_hex_address, True)

    async def stats(self):
        await stat(self)