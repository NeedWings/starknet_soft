from DEXes.avnu import *
from DEXes.fibrous import *
from DEXes.jediswap import *
from DEXes.myswap import *
from DEXes.sithswap import *
from DEXes.tenkswap import *
from DEXes.zklend import *
from braavos_shit import *
from DEXes.domain import *
from DEXes.okx_sender import *
from DEXes.bids import *
from DEXes.dmail import *
from own_tasks import *
from stats import stat
eth = Token("ETH", 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 18)
usdc = Token("USDC", 0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8, 6, stable=True)
usdt = Token("USDT", 0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8, 6, stable=True)
dai = Token("DAI", 0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3, 18, stable=True)
wbtc = Token("WBTC", 0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac, 8)
wsteth = Token("WSTETH", 0x042b8f0484674ca266ac5d08e4ac6a3fe65bd3129795def2dca5c34ecc5f96d2, 18)
lords = Token("LORDS", 0x0124aeb495b947201f5fac96fd1138e326ad86195b98df6dec9009158a533b49, 18)

domain_hand = StarkId()
sender_hand = Sender()
tokens = [
    eth,
    usdt,
    usdc,
    dai,
    wbtc,
    wsteth,
    lords
]

tokens_dict = {
    "ETH": eth,
    "USDT": usdt,
    "USDC": usdc,
    "DAI": dai,
    "WBTC": wbtc,
    "WSTETH": wsteth,
    "LORDS": lords
}

swap_dexes = [
    Avnu(),
    Fibrous(),
    JediSwap(),
    MySwap(),
    SithSwap(),
    TenKSwap()
]


liq_dexes = [
    JediSwap(),
    MySwap(),
    SithSwap(),
    TenKSwap()
]

lends = [
    ZkLend()
]

supported_dexes_for_swaps = []
supported_dexes_for_liq = []
supported_lends = []
suppotred_tokens = []

for name in SETTINGS["SwapDEXs"]:
    for dex in swap_dexes:
        if dex.name == name:
            supported_dexes_for_swaps.append(dex)


for name in SETTINGS["LiqDEXs"]:
    for dex in liq_dexes:
        if dex.name == name:
            supported_dexes_for_liq.append(dex)


for name in SETTINGS["Lends"]:
    for dex in lends:
        if dex.name == name:
            supported_lends.append(dex)
        
for name in SETTINGS["Supported_tokens"]:
    for token in tokens:
        if token.symbol == name:
            suppotred_tokens.append(token)


class MainRouter():
    def __init__(self, stark_key: int, delay: int, task_number: int, client) -> None:
        self.task_number = task_number
        stark_native_account, call_data, salt, class_hash = import_argent_account(stark_key, client)

        self.account = StarkAccount(stark_native_account, call_data, salt, class_hash)
        self.delay = delay
        indexes.append(self.account.formatted_hex_address)

    
    async def start(self):
        global gas_high
        if self.delay != 0 or True:
            for i in range(100):
                await asyncio.sleep(self.delay/100)
                while gas_high.is_set():
                    await asyncio.sleep(10)
        task_number = self.task_number
        
        if task_number == 1:
            pass
        elif task_number == 2:
            await self.swaps_handler()
        elif task_number == 0:
            await own_tasks(self)
        elif task_number == 3:
            await self.swap_to_one_token()
        elif task_number == 4:
            await self.liq_handler()
        elif task_number == 5:
            await self.remove_liq()
        elif task_number == 7:
            await self.full()
        elif task_number == 8:
            await self.withdraw()
        elif task_number == 9:
            pass
        elif task_number == 13:
            await self.deployer()
        elif task_number == 16:
            await self.stats()
        elif task_number == 17:
            await self.lend_router()
        elif task_number == 18:
            await self.remove_from_lend()
        elif task_number == 22:
            await self.withdraw(addr_dict[self.account.formatted_hex_address])
        elif task_number == 23:
            await self.dmail()
        elif task_number == 24:
            await self.stark_id()
        elif task_number == 26:
            await self.full_withdraw()
        elif task_number == 27:
            await self.full_withdraw(addr_dict[self.account.formatted_hex_address])
        elif task_number == 28:
            await self.collateral()
        elif task_number == 29:
            await self.braavos_upgrader()
        elif task_number == 30:
            await self.return_borrowed()
        elif task_number == 31:
            await self.argent_upgrader()
        elif task_number == 32:
            await self.new_id()
        elif task_number == 33:
            await self.okx()
        elif task_number == 34:
            await self.bids(1)
        elif task_number == 35:
            await self.bids(2)
        elif task_number == 36:
            await self.bids(3)

    async def bids(self, flex):
        for i in range(get_random_value_int(SETTINGS["bids_amount"])):
            if flex == 1:
                await self.account.send_txn(await bidder.create_txn_for_flex(eth, self.account))
            elif flex == 2:
                await self.account.send_txn(await bidder.create_txn_for_unframed(eth, self.account))
            elif flex == 3:
                await self.account.send_txn(await bidder.create_txn_for_element(eth, self.account))
            await sleeping(self.account.formatted_hex_address)

    async def okx(self):
        rec = ""
        with open(f"{SETTINGS_PATH}pairs.txt", "r") as f:
            pairs = f.read().lower().split("\n")
        for pair in pairs:
            try:
                if self.account.formatted_hex_address == "0x" + "0"*(66-len(hex(int(pair.split("\t")[0], 16)))) + hex(int(pair.split("\t")[0], 16))[2::]:
                    rec = pair.split("\t")[1]   
            except:
                if self.account.formatted_hex_address == "0x" + "0"*(66-len(hex(int(pair.split("    ")[0], 16)))) + hex(int(pair.split("    ")[0], 16))[2::]:
                    rec = pair.split("    ")[1]   
        
        if rec == "":
            return
        
        txn = await sender_hand.create_txn(eth, rec, self.account)
        if txn == -1:
            return
        logger.info(f"[{self.account.formatted_hex_address}] going to send eth to {rec}")
        await self.account.send_txn(txn)
    

    async def new_id(self):
        await self.account.send_txn(await domain_hand.create_txn(eth, self.account))


    async def argent_upgrader(self):
        new_impl = int(SETTINGS["new_implementation_for_upgrade"], 16)

        contract = Contract(self.account.stark_native_account.address, UPGRADE_ARGENT, self.account.stark_native_account)
        
        call = contract.functions["upgrade"].prepare(
                new_impl,
                [0]
        )

        calldata = [call]

        logger.info(f"[{self.account.formatted_hex_address}] going to upgrade")

        await self.account.send_txn(calldata)


    async def full_withdraw(self, wallet = None):
        await self.return_borrowed()
        await self.remove_from_lend()
        await self.remove_liq()
        await self.swap_to_one_token()
        await self.withdraw(wallet)

    async def withdraw(self, wallet = None):
        account = self.account.stark_native_account
        web3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))
        private_key = "0x" + "0"*(66-len(hex(account.signer.private_key))) + hex(account.signer.private_key)[2::]
        if wallet == None:
            wallet = web3.eth.account.from_key(private_key).address


        amount = get_random_value(SETTINGS["EtherToWithdraw"])

        balance = await self.account.get_balance()/1e18

        balance = balance - get_random_value(SETTINGS["WithdrawSaving"])

        if amount > balance:
            amount = balance

        if amount < 0.006:
            logger.error(f"[{self.account.formatted_hex_address}] amount to bridge less than minimal amount")
            return
        distNet = SETTINGS["DistNet"].lower()
        if distNet == "arbitrum":
            amount = int((get_orbiter_value(amount) * decimal.Decimal(1e18)) - 2)
        elif distNet == "zksync":
            amount = int((get_orbiter_value(amount) * decimal.Decimal(1e18)) + 10)
        elif distNet == "ethereum":
            amount = int((get_orbiter_value(amount) * decimal.Decimal(1e18)) - 3)
        elif distNet == "linea":
            amount = int((get_orbiter_value(amount) * decimal.Decimal(1e18)) + 19)
        else:
            logger.error(f"[{self.account.formatted_hex_address}] wrong value in DistNet")
            input()
            exit()
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

        logger.info(f"[{self.account.formatted_hex_address}] going to bridge {amount/1e18} ETH to {wallet}")
        calldata = [approve_call, call]

        await self.account.send_txn(calldata)

    async def stats(self):
        await stat(self)
       
    async def stark_id(self):
        amount = get_random_value_int(SETTINGS["starknet_id_amount"])
        account = self.account.stark_native_account
        for i in range(amount):
            id_contract = Contract(0x05dbdedc203e92749e2e746e2d40a768d966bd243df04a6b712e222bc040a9af, [{"name":"mint","type":"function","inputs":[{"name":"starknet_id","type":"felt"}],"outputs":[]}], account)
            logger.info(f"[{self.account.formatted_hex_address}] going to mint starknet id")
            call = id_contract.functions["mint"].prepare(
                random.randint(0, 999999999999)
            )
            calldata = [call]

            await self.account.send_txn(calldata)
            await sleeping(self.account.formatted_hex_address)


    async def dmail(self):
        amount = get_random_value_int(SETTINGS["dmail_messages_amount"])
        for qawe in range(amount):
            
            calldata = await dmail_hand.create_txn_for_dmail(self.account)

            await self.account.send_txn(calldata)

            await sleeping(self.account.formatted_hex_address)


    async def collateral(self):
        account = self.account.stark_native_account
        for i in range(get_random_value_int(SETTINGS["zklend_collateral_amount"])):
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


    async def braavos_upgrader(self):
        new_impl = int(SETTINGS["new_implementation_for_upgrade"], 16)

        contract = Contract(self.account.stark_native_account.address, BRAAVOS_UPGRADE, self.account.stark_native_account)
        
        call = contract.functions["upgrade"].prepare(
                new_impl
        )

        calldata = [call]

        logger.info(f"[{self.account.formatted_hex_address}] going to upgrade")

        await self.account.send_txn(calldata)


    async def deployer(self):
        call_data = self.account.call_data
        class_hash = self.account.class_hash
        salt = self.account.salt
        account = self.account.stark_native_account
        balance = 0
        while True:
            try:
                nonce = await account.get_nonce()
                if nonce > 0:
                    logger.info(f"[{self.account.formatted_hex_address}] already deployed. Skip")
                    return
                else:
                    break
            except Exception as e:
                if "contract not found" in (str(e)).lower():
                    nonce = 0
                    break
                logger.error(f"[{self.account.formatted_hex_address}] got error while trying to get nonce: {e}")
                await sleeping(self.account.formatted_hex_address, True)
        while True:
            
            logger.info(f"[{self.account.formatted_hex_address}] checking balance.")
            balance = await self.account.get_balance()
            logger.info(f"[{self.account.formatted_hex_address}] got balance: {balance/1e18} ETH")
            if balance >= 1e14:
                break
            await sleeping(self.account.formatted_hex_address)
        logger.success(f"[{self.account.formatted_hex_address}] found balance. Going to deploy")
        i = 0
        while i < retries_limit:
            i += 1
            try:
                provider = SETTINGS["Provider"].lower()
                if provider == "argent_newest" or provider == "argent":
                    account_deployment_result = await StarkNativeAccount.deploy_account(
                        address=account.address,
                        class_hash=class_hash,
                        salt=salt,
                        key_pair=account.signer.key_pair,
                        client=account.client,
                        chain=chain,
                        constructor_calldata=call_data,
                        auto_estimate=True,
                    )
                elif provider == "braavos_newest":
                    account_deployment_result = await deploy_account_braavos(
                        address=account.address,
                        class_hash=class_hash,
                        salt=salt,
                        key_pair=account.signer.key_pair,
                        client=account.client,
                        chain=chain,
                        constructor_calldata=call_data,
                        auto_estimate=True,
                        )
                else:
                    logger.error(f"Selected unsupported wallet provider: {SETTINGS['Provider'].lower()}. Please select one of this: argen_newest, braavos_newest")
                    return

                # Wait for deployment transaction to be accepted

                await account_deployment_result.wait_for_acceptance()
                # From now on, account can be used as usual
                account = account_deployment_result.account
                logger.success(f"[{self.account.formatted_hex_address}] deployed successfully, txn hash: {hex(account_deployment_result.hash)}")
                return 1

            except Exception as e:
                logger.error(f"[{self.account.formatted_hex_address}] got error, while deploying account, {e}")
                await sleeping(self.account.formatted_hex_address, True)
        logger.error(f"[{self.account.formatted_hex_address}] got error")
        return -1

    async def get_max_valued_token(self, tokens: List[Token]):
        max_valued = None
        max_value = 0
        for token in tokens:
            balance = await self.account.get_balance(token.contract_address, token.symbol)
            if token.symbol == "ETH":
                balance = balance - get_random_value(SETTINGS["SaveEthOnBalance"])*1e18
                logger.info(f"[{self.account.formatted_hex_address}] {token.symbol} balance: {balance/10**token.decimals}")
            else:
                if balance/10**token.decimals < SETTINGS["MINIMAL_SWAP_AMOUNTS"][token.symbol]:
                    balance = 0
                    logger.info(f"[{self.account.formatted_hex_address}] {token.symbol} balance below MINIMAL_SWAP_AMOUNTS, will count as 0")
                else:
                    logger.info(f"[{self.account.formatted_hex_address}] {token.symbol} balance: {balance/10**token.decimals}")
            usd_value = token.get_usd_value(balance/10**token.decimals)
            if usd_value>max_value:
                max_valued = token
                max_value = usd_value
        return max_valued, max_value

    def supported_tokens_str_to_token(self, tokens):
        res = []
        for token in tokens:
            res.append(tokens_dict[token])

        return res
    
    async def full(self):
        ways = [1,2,3,4,5]
        shuffle(ways)
        for way in ways:
            print(way)
            if way == 1:
                await self.swaps_handler()
            elif way == 2:
                await self.liq_handler()
                if random.choice(SETTINGS["RemoveOnFullMode"]):
                    await self.remove_liq()
            elif way == 3:
                await self.lend_router()
                if random.choice(SETTINGS["RemoveOnFullMode"]):
                    await self.return_borrowed()
                    await self.remove_from_lend()
            elif way == 4:
                await self.dmail()
            elif way == 5:
                await self.collateral()
            
        if random.choice(SETTINGS["SwapAtTheEnd"]):
            await self.swap_to_one_token(random.choice(SETTINGS["toSaveFunds"]))

    async def swaps_handler(self):
        swap_amount = get_random_value_int(SETTINGS["swapAmounts"])
        if swap_amount < 1:
            return
        s = list(range(swap_amount))
        for i in s:
            try:
                dex: BaseDex = random.choice(supported_dexes_for_swaps)
                token1, usd_value =  await self.get_max_valued_token(self.supported_tokens_str_to_token(dex.supported_tokens))
                if token1 == None:
                    logger.error(f"[{self.account.formatted_hex_address}] all balances is 0")
                    continue
                token1: Token = token1
                token2 = tokens_dict[dex.get_pair_for_token(token1.symbol)]
                
                amount_to_swap = usd_value * get_random_value(SETTINGS["WorkPercent"])
                
                token1_val = amount_to_swap/token1.get_price()
                token2_val = amount_to_swap/token2.get_price()
                logger.info(f"[{self.account.formatted_hex_address}] going to swap {token1_val} {token1.symbol} for {token2.symbol} in {dex.name}")

                swap_txn = await dex.create_txn_for_swap(token1_val, token1, token2_val, token2, self.account)
                if swap_txn == -1:
                    s.append(len(s))
                    await sleeping(self.account.formatted_hex_address, True)
                    continue

                await self.account.send_txn(swap_txn)
                await sleeping(self.account.formatted_hex_address)

            except Exception as e:
                logger.error(f"[{self.account.formatted_hex_address}] got erroor: {e}")
                await sleeping(self.account.formatted_hex_address, True)
    
    async def liq_handler(self):
        liq_amount = get_random_value_int(SETTINGS["AddLiqAmount"])
        if liq_amount < 1:
            return
        
        for i in range(liq_amount):
            try:
                dex: BaseDex = random.choice(supported_dexes_for_liq)
                token1, usd_value = await self.get_max_valued_token(self.supported_tokens_str_to_token(dex.supported_tokens))
                if token1 == None:
                    logger.error(f"[{self.account.formatted_hex_address}] all balances is 0")
                    continue
                token1: Token = token1
                token2 = dex.get_pair_for_token(token1.symbol)

                if token2 == -5:
                    continue
                token2: Token = tokens_dict[token2]
                amount_to_add = usd_value * get_random_value(SETTINGS["LiqWorkPercent"])/2
                token2_usd_value = token2.get_usd_value(await self.account.get_balance(token2.contract_address, token2.symbol) / 10**token2.decimals)
                amount1 = amount_to_add/token1.get_price()
                amount2 = amount_to_add/token2.get_price()
                logger.info(f"[{self.account.formatted_hex_address}] going to add liquidity in {dex.name} in {token1.symbol}/{token2.symbol} pair for {amount1} {token1.symbol} and {amount2} {token2.symbol}")
                
                if token2_usd_value < amount_to_add*(1+ SETTINGS["Slippage"]+0.01):
                    logger.info(f"[{self.account.formatted_hex_address}] not enough second token for adding, will make swap")
                    
                    amount_to_swap = amount_to_add*(1+ SETTINGS["Slippage"]+0.01) - token2_usd_value
                    token1_amount_to_swap = amount_to_swap/token1.get_price()
                    amount_out = amount_to_swap/token2.get_price()
                    
                    logger.info(f"[{self.account.formatted_hex_address}] going to swap {token1_amount_to_swap} {token1.symbol} for {token2.symbol} in {dex.name}")
                    
                    swap_txn = await dex.create_txn_for_swap(token1_amount_to_swap, token1, amount_out, token2, self.account)

                    if swap_txn == -1:
                        logger.error(f"[{self.account.formatted_hex_address}] can't create txn for swap")
                        await sleeping(self.account.formatted_hex_address, True)
                        continue

                    if (await self.account.send_txn(swap_txn))[0] != 1:
                        continue
                    await sleeping(self.account.formatted_hex_address)
                liq_txn = await dex.create_txn_for_liq(amount1, token1, amount2, token2, self.account)
                if liq_txn == -1:
                    await sleeping(self.account.formatted_hex_address, True)
                    continue

                await self.account.send_txn(liq_txn)
                await sleeping(self.account.formatted_hex_address)

            except Exception as e:
                logger.error(f"[{self.account.formatted_hex_address}] got erroor: {e}")
                await sleeping(self.account.formatted_hex_address, True)

    async def lend_router(self):
        add_amount = get_random_value_int(SETTINGS["AddLendAmount"])

        for i in range(add_amount):
            try:
                lend: BaseLend = random.choice(supported_lends)
                token, usd_value = await self.get_max_valued_token(self.supported_tokens_str_to_token(lend.supported_tokens))
                if token == None:
                    logger.error(f"[{self.account.formatted_hex_address}] all balances is 0")
                    continue
                token: Token
                amount_to_add = usd_value * get_random_value(SETTINGS["LendWorkPercent"])
                amount_to_add_in_token = amount_to_add/token.get_price()
                
                logger.info(f"[{self.account.formatted_hex_address}] going to add {amount_to_add_in_token} {token.symbol} in {lend.name}")

                txn = await lend.create_txn_for_adding_token(token, amount_to_add_in_token, self.account)

                await self.account.send_txn(txn)

                await sleeping(self.account.formatted_hex_address)
            except Exception as e:
                logger.error(f"[{self.account.formatted_hex_address}] got erroor: {e}")
                await sleeping(self.account.formatted_hex_address, True)

        borrow_return_amount = get_random_value_int(SETTINGS["BorrowAddAmount"])
        for i in range(borrow_return_amount):
            try:
                lend: BaseLend = random.choice(supported_lends)
                token = random.choice(self.supported_tokens_str_to_token(lend.supported_tokens))

                
                total_borroved = await lend.get_total_borrowed(self.account)
                total_supplied = await lend.get_total_supplied(self.account)
                usd_val = total_supplied-total_borroved

                
                to_borrow_usd = (usd_val)*get_random_value(SETTINGS["BorrowWorkPercent"])*lend.coeffs_for_borrow[token.symbol]
                if to_borrow_usd == 0:
                    logger.error(f"[{self.account.formatted_hex_address}] to borrow is zero")
                    await sleeping(self.account.formatted_hex_address, True)
                    continue
                
                amount = to_borrow_usd/token.get_price()
                logger.info(f"[{self.account.formatted_hex_address}] going to borrow {amount} {token.symbol} in {lend.name}")

                txn = await lend.create_txn_for_borrow(amount, token, self.account)

                if (await self.account.send_txn(txn))[0] != 1:
                    continue

                await sleeping(self.account.formatted_hex_address)
                logger.info(f"[{self.account.formatted_hex_address}] going to return {amount} {token.symbol} in {lend.name}")
                txn = await lend.create_txn_for_return(token, self.account)

                await self.account.send_txn(txn)

                await sleeping(self.account.formatted_hex_address)

            except Exception as e:
                logger.error(f"[{self.account.formatted_hex_address}] got erroor: {e}")
                await sleeping(self.account.formatted_hex_address, True)

    async def swap_to_one_token(self, token = "ETH"):
        token = tokens_dict[token]
        tokens = suppotred_tokens.copy() 
        shuffle(tokens)
        for token_to_swap in tokens:
            try:
                token_to_swap: Token
                if token == token_to_swap:
                    continue

                balance = await self.account.get_balance(token_to_swap.contract_address, token_to_swap.symbol)

                if token_to_swap.symbol == "ETH":
                    balance -= int(get_random_value(SETTINGS["SaveEthOnBalance"])*1e18)
                else:
                    if balance/10**token_to_swap.decimals < SETTINGS["MINIMAL_SWAP_AMOUNTS"][token_to_swap.symbol]:
                        balance = 0

                if balance <=0:
                    logger.info(f"[{self.account.formatted_hex_address}] {token_to_swap.symbol} balance 0 or less MINIMAL_SWAP_AMOUNTS. skip")
                    continue
                selected = False
                for i in range(SETTINGS["retries_limit"]):
                    dex: BaseDex = random.choice(supported_dexes_for_swaps)
                    if token_to_swap.symbol in dex.supported_tokens:
                        selected = True
                        break
                
                if not selected:
                    logger.error(f"[{self.account.formatted_hex_address}] can't find dex for {token_to_swap.symbol}")
                    continue

                usd_val = token_to_swap.get_usd_value(balance/10**token_to_swap.decimals)

                amount_out = usd_val/token.get_price()
                logger.info(f"[{self.account.formatted_hex_address}] going to swap {balance/10**token_to_swap.decimals} {token_to_swap.symbol} for {token.symbol} in {dex.name}")


                swap_txn = await dex.create_txn_for_swap(balance/10**token_to_swap.decimals, token_to_swap, amount_out, token, self.account, full = True)
                if swap_txn != -1:
                    await self.account.send_txn(swap_txn)
                    await sleeping(self.account.formatted_hex_address)

            except Exception as e:
                logger.error(f"[{self.account.formatted_hex_address}] got error: {e}")
                await sleeping(self.account.formatted_hex_address, True)

    async def remove_liq(self):
        dexes = supported_dexes_for_liq.copy()
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

    async def remove_from_lend(self):
        lends = supported_lends.copy()
        shuffle(lends)
        for lend in lends:
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
                if txn == -1:
                    logger.info(f"[{self.account.formatted_hex_address}] not enough repayed for removing. Skip")
                    continue
                await self.account.send_txn(txn)

                await sleeping(self.account.formatted_hex_address)

    async def return_borrowed(self):
        for lend in lends:
            tokens = self.supported_tokens_str_to_token(lend.supported_tokens).copy()
            shuffle(tokens)
            for token in tokens:
                try:
                    txn = await lend.create_txn_for_return(token, self.account)
                    if txn == -1:
                        continue
                    logger.info(f"[{self.account.formatted_hex_address}] going to return borroved {token.symbol}")
                    await self.account.send_txn(txn)

                    await sleeping(self.account.formatted_hex_address)

                except Exception as e:
                    logger.error(f"[{self.account.formatted_hex_address}] got erroor: {e}")
                    await sleeping(self.account.formatted_hex_address, True)
