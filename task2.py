from utils import *


def jediswap_call(amount: float, sender: int, token1: int, token2: int, contract: Contract):
    token1_dec = DECIMALS[token1]
    token2_dec = DECIMALS[token2]
    if token1_dec == 18:
        amount_out = int(amount*(get_eth_price()-40)*(10**token2_dec) - amount*get_eth_price()*(10**token2_dec)*slippage)
    elif token1_dec == 6:
        amount_out =  int((amount/(get_eth_price()+40))*(10**token2_dec) - (amount/get_eth_price())*(10**token2_dec)*slippage)
    else:
        return INVALID_DECIMALS
    call = contract.functions["swap_exact_tokens_for_tokens"].prepare(
            int(amount*(10**token1_dec)), 
            amount_out, 
            (token1, 
            token2),
            sender, 
            int(time.time())+3600
            )
    return call


def myswap_call(amount: float, token1: int, token2: int, contract: Contract):
    token1_dec = DECIMALS[token1]
    token2_dec = DECIMALS[token2]
    if token1_dec == 18:
        amount_out = int(amount*(get_eth_price()-40)*(10**token2_dec) - amount*get_eth_price()*(10**token2_dec)*slippage)
    elif token1_dec == 6:
        amount_out =  int((amount/(get_eth_price()+40))*(10**token2_dec) - (amount/get_eth_price())*(10**token2_dec)*slippage)
    else:
        return INVALID_DECIMALS
    call = contract.functions["swap"].prepare(
            MYSWAP_POOLS[f"{token1}:{token2}"],
            token1,
            int(amount*(10**token1_dec)), 
            amount_out
            )
    return call

def ten_k_swap_call(amount: float, sender: int, token1: int, token2: int, contract: Contract):
    token1_dec = DECIMALS[token1]
    token2_dec = DECIMALS[token2]
    if token1_dec == 18:
        amount_out = int(amount*(get_eth_price()-40)*(10**token2_dec) - amount*get_eth_price()*(10**token2_dec)*slippage)
    elif token1_dec == 6:
        amount_out =  int((amount/(get_eth_price()+40))*(10**token2_dec) - (amount/get_eth_price())*(10**token2_dec)*slippage)
    else:
        return INVALID_DECIMALS
    call = contract.functions["swapExactTokensForTokens"].prepare(
            int(amount*(10**token1_dec)),
            amount_out,
            (token1, 
            token2),
            sender,
            int(time.time())+3600
            )
    return call

def sithswap_call(amount: float, sender: int, token1: int, token2: int, contract: Contract):
    token1_dec = DECIMALS[token1]
    token2_dec = DECIMALS[token2]
    if token1_dec == 18:
        amount_out = int(amount*(get_eth_price()-40)*(10**token2_dec) - amount*get_eth_price()*(10**token2_dec)*slippage)
    elif token1_dec == 6:
        amount_out =  int((amount/(get_eth_price()+40))*(10**token2_dec) - (amount/get_eth_price())*(10**token2_dec)*slippage)
    else:
        return INVALID_DECIMALS
    call = contract.functions["swapExactTokensForTokensSupportingFeeOnTransferTokens"].prepare(
            int(amount*(10**token1_dec)),
            amount_out,
            [
                {"from_address":token1,
                "to_address":token2,
                "stable":0}
            ],
            sender,
            int(time.time())+3600
            )
    return call

def anvu_call(amount: float, sender: int, token1: int, token2: int, contract: Contract):
    token1_dec = DECIMALS[token1]
    token2_dec = DECIMALS[token2]
    if token2 == ETH_TOKEN_CONTRACT:
        route = ROUTE_FOR_ANVU[token1]
    else:
        route = ROUTE_FOR_ANVU[token2]
    if token1_dec == 18:
        amount_out = int(amount*(get_eth_price()-40)*(10**token2_dec))
    elif token1_dec == 6:
        amount_out =  int((amount/(get_eth_price()+40))*(10**token2_dec))
    else:
        return INVALID_DECIMALS
    call = contract.functions["multi_route_swap"].prepare(
            token1,
            int(amount*(10**token1_dec)),
            token2,
            amount_out,
            int(amount_out - amount_out*slippage),
            sender,
            0,
            0,
            [
                {"token_from":token1,
                "token_to":token2,
                "exchange_address": route,
                "percent":100}
            ],
            )
    return call

def fibrous_call(amount: float, sender: int, token1: int, token2: int, contract: Contract):
    token1_dec = DECIMALS[token1]
    token2_dec = DECIMALS[token2]
    if token1_dec == 18:
        amount_out = int(amount*(get_eth_price()-40)*(10**token2_dec))
    elif token1_dec == 6:
        amount_out =  int((amount/(get_eth_price()+40))*(10**token2_dec))
    else:
        return INVALID_DECIMALS
    call = contract.functions["swap"].prepare(
            [
                {"token_in":token1,
                "token_out":token2,
                "rate": 1000000,
                "protocol":2,
                "pool_address": 0x45e7131d776dddc137e30bdd490b431c7144677e97bf9369f629ed8d3fb7dd6}
            ],
            
                {"token_in":token1,
                "token_out":token2,
                "amount":  int(amount*(10**token1_dec)),
                "min_received": int(amount_out - amount_out*slippage),
                "destination": sender}
                  
            )
    return call

async def fibrous(amount: float, token1: int, token2: int, provider: Account):
    fibrous_contract = Contract(0x01b23ed400b210766111ba5b1e63e33922c6ba0c45e6ad56ce112e5f4c578e62, FIBROUS_ABI, provider)
    token_contract = Contract(token1, ABIs[token1], provider)
    calldata = [
        approve_token_call(amount, 0x01b23ed400b210766111ba5b1e63e33922c6ba0c45e6ad56ce112e5f4c578e62, token_contract),
        fibrous_call(amount, provider.address, token1, token2, fibrous_contract)
    ]

    return await execute_function(provider, calldata)

async def jediswap(amount: float, token1: int, token2: int, provider: Account):
    jediswap_contract = Contract(JEDISWAP_CONTRACT, JEDISWAP_ABI, provider)
    token_contract = Contract(token1, ABIs[token1], provider)
    calldata = [
        approve_token_call(amount, JEDISWAP_CONTRACT, token_contract),
        jediswap_call(amount, provider.address, token1, token2, jediswap_contract)
    ]

    return await execute_function(provider, calldata)

async def myswap(amount: float, token1: int, token2: int, provider: Account):
    myswap_contract = Contract(MYSWAP_CONTRACT, MYSWAP_ABI, provider)
    token_contract = Contract(token1, ABIs[token1], provider)
    calldata = [
        approve_token_call(amount, MYSWAP_CONTRACT, token_contract),
        myswap_call(amount, token1, token2, myswap_contract)
    ]

    return await execute_function(provider, calldata)

async def anvu(amount: float, token1: int, token2: int, provider: Account):
    anvu_contract = Contract(ANVU_CONTRACT, ANVU_ABI, provider)
    token_contract = Contract(token1, ABIs[token1], provider)
    calldata = [
        approve_token_call(amount, ANVU_CONTRACT, token_contract),
        anvu_call(amount, provider.address, token1, token2, anvu_contract)
    ]

    return await execute_function(provider, calldata)

async def ten_k_swap(amount: float, token1: int, token2: int, provider: Account):
    ten_k_swap_contract = Contract(TEN_K_SWAP_CONTRACT, TEN_K_SWAP_ABI, provider)
    token_contract = Contract(token1, ABIs[token1], provider)
    calldata = [
        approve_token_call(amount, TEN_K_SWAP_CONTRACT, token_contract),
        ten_k_swap_call(amount, provider.address, token1, token2, ten_k_swap_contract)
    ]

    return await execute_function(provider, calldata)

async def sithswap(amount: float, token1: int, token2: int, provider: Account):
    sithswap_contract = Contract(SITHSWAP_CONTRACT, SITHSWAP_ABI, provider)
    token_contract = Contract(token1, ABIs[token1], provider)
    calldata = [
        approve_token_call(amount, SITHSWAP_CONTRACT, token_contract),
        sithswap_call(amount, provider.address, token1, token2, sithswap_contract)
    ]

    return await execute_function(provider, calldata)



async def swap(amount: float, dex: str, token1: int, token2: int, provider: Account):
    while True:
        try:
            token1_balance = await provider.get_balance(token1)/10**DECIMALS[token1]
            break
        except Exception as e:
            logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] can't get balance. {e} ")
            await sleeping('0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::], True)
    if token1_balance < amount:
        logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] not enough token for swap: balance {token1_balance}, required {amount}")
        await sleeping('0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::], True)
        return NOT_ENOUGH_NATIVE, ""
    if dex == "jedi":
        res = await jediswap(amount, token1, token2, provider)
    elif dex == "my":
        res = await myswap(amount, token1, token2, provider)
    elif dex == "10k":
        res = await ten_k_swap(amount, token1, token2, provider)
    elif dex == "sith":
        res = await sithswap(amount, token1, token2, provider)
    elif dex == "anvu":
        res = await anvu(amount, token1, token2, provider)
    elif dex == "fibrous":
        res = await fibrous(amount, token1, token2, provider)
    else:
        logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] chosen wrong dex for swap: {dex}; supported: jedi, my, 10k, sith")
        await sleeping('0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::], True)
        return WRONG_CHOICE, ""
    return res

async def random_swaps(account: Account, delay: int):
    await asyncio.sleep(delay)
    limit = get_random_value_int(SETTINGS["SwapAmounts"])
    while limit > 0:
        await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])
        limit -= 1
        dex = random.choice(SETTINGS["SwapDEXs"])
        eth_price = get_eth_price()
        while True:
            try:
                eth_balacne = await account.get_balance()/1e18
                break
            except Exception as e:
                logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got error while trying to get balance: {e}")
                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
        while True:
            try:
                usdt_balacne = await account.get_balance(USDT_TOKEN_CONTRACT)/1e6
                break
            except Exception as e:
                logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got error while trying to get balance: {e}")
                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
        while True:
            try:
                usdc_balacne = await account.get_balance(USDC_TOKEN_CONTRACT)/1e6
                break
            except Exception as e:
                logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got error while trying to get balance: {e}")
                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
        logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got ETH balance: {eth_balacne}")
        logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got USDC balance: {usdc_balacne}")
        logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got USDT balance: {usdt_balacne}")
        eth_usd_value = eth_balacne * eth_price
        to_choose = {
            eth_usd_value : ETH_TOKEN_CONTRACT,
            usdt_balacne : USDT_TOKEN_CONTRACT,
            usdc_balacne : USDC_TOKEN_CONTRACT
        }
        balances = [
            eth_usd_value, usdt_balacne, usdc_balacne
        ]

        token_contract = to_choose[max(balances)]
        if token_contract == ETH_TOKEN_CONTRACT:
            swap_amount_eth = eth_balacne * get_random_value(SETTINGS["WorkPercent"])

            usd_value = swap_amount_eth * eth_price

            token = random.choice(SETTINGS["Supported_tokens"])
            try:
                token_contract = TOKENS[token]
            except:
                logger.error(f"Selected unsupported token ({token}), please choose one from this (USDT, USDC)")
                input("Please restart soft with correct settings")



            if usd_value < SETTINGS["MINIMAL_SWAP_AMOUNTS"][token]:
                logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] Error while trying to swap: want to swap {usd_value} {token}, which is below minimum {SETTINGS['MINIMAL_SWAP_AMOUNTS'][token]}")
                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
                continue

            if dex not in SUPPORTED_FOR_SWAPS:
                logger.error(f"Selected unsupported DEX ({dex}), please choose one from this (jedi, my, 10k, sith, anvu, fibrous)")
                input("Please restart soft with correct settings")

            logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] going to swap {swap_amount_eth} ETH for {token} on {dex}swap")

            if (await swap(swap_amount_eth, dex, ETH_TOKEN_CONTRACT, token_contract, account))[0] == SUCCESS:
                out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] = out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] + f"swap {swap_amount_eth} ETH for {token} on {dex}swap\n"
        else:
            dex = random.choice(SETTINGS["SwapDEXs"])
            if token_contract == USDT_TOKEN_CONTRACT:
                token = "USDT"
            else:
                token = "USDC"
            token_balance = max(balances) * get_random_value(SETTINGS["WorkPercent"])
            if dex not in SUPPORTED_FOR_SWAPS:
                logger.error(f"Selected unsupported DEX ({dex}), please choose one from this (jedi, my, 10k, sith, anvu)")
                input("Please restart soft with correct settings")
            await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])

            logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] going to swap {token_balance} {token} for ETH on {dex}swap")


            if (await swap(token_balance, dex, token_contract, ETH_TOKEN_CONTRACT, account))[0] == SUCCESS:
                out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] = out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] + f"swap {token_balance} {token} for ETH on {dex}swap\n"


        await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])
        


def task_2(stark_keys):
    loop = asyncio.new_event_loop()
    tasks = []
    delay = 0
    for key in stark_keys:
        if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
            client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
        else:
            client = GatewayClient(net=MAINNET)
        account, call_data, salt, class_hash = import_argent_account(key, client)
        out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] = ""
        tasks.append(loop.create_task(random_swaps(account, delay)))
        delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])


    loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

    res = ""

    for i in out_wallets_result:
        res += f"{i}:\n{out_wallets_result[i]}\n"

    with open("log.txt", "w") as f:
        f.write(res)