from utils import *
from task2 import *

def jediswap_liq_call(amount: float, amount_out:float, sender: int, token1: int, token2: int, contract: Contract):
    token1_dec = DECIMALS[token1]

    call = contract.functions["add_liquidity"].prepare(
            token1,
            token2,
            int(amount*(10**token1_dec)),
            int(amount_out - slippage*amount_out),
            int(amount*(10**token1_dec)- slippage*amount*(10**token1_dec)),
            int(amount_out - 2*amount_out*slippage),
            sender,
            int(time.time())+3600
            )
    return call

async def jediswap_liq(amount: float, amount_out: float, token1: int, token2: int, provider: Account):
    token1_dec = DECIMALS[token1]
    token2_dec = DECIMALS[token2]
    if token1_dec == 18:
        amount_out = amount*(get_eth_price())
    elif token1_dec == 6:
        amount_out =  (amount/(get_eth_price()))

    jediswap_contract = Contract(JEDISWAP_CONTRACT, JEDISWAP_ABI, provider)
    token1_contract = Contract(token1, ABIs[token1], provider)
    token2_contract = Contract(token2, ABIs[token2], provider)
    calldata = [
        approve_token_call(amount, JEDISWAP_CONTRACT, token1_contract),
        approve_token_call(amount_out, JEDISWAP_CONTRACT, token2_contract),
        jediswap_liq_call(amount, amount_out*(10**token2_dec), provider.address, token1, token2, jediswap_contract)
    ]
    return await execute_function(provider, calldata)

def myswap_liq_call(amount: float, amount_out:float, sender: int, token1: int, token2: int, contract: Contract):
    token1_dec = DECIMALS[token1]

    call = contract.functions["add_liquidity"].prepare(
            token1,
            int(amount*(10**token1_dec)),
            int(amount*(10**token1_dec) - slippage*amount*(10**token1_dec)),
            token2,
            int(amount_out),
            int(amount_out- amount_out*slippage),
            )
    return call

async def myswap_liq(amount: float, amount_out: float, token1: int, token2: int, provider: Account):
    token1_dec = DECIMALS[token1]
    token2_dec = DECIMALS[token2]


    myswap_contract = Contract(MYSWAP_CONTRACT, MYSWAP_ABI, provider)
    token1_contract = Contract(token1, ABIs[token1], provider)
    token2_contract = Contract(token2, ABIs[token2], provider)
    calldata = [
        approve_token_call(amount, MYSWAP_CONTRACT, token1_contract),
        approve_token_call(amount_out, MYSWAP_CONTRACT, token2_contract),
        myswap_liq_call(amount, amount_out*(10**token2_dec), provider.address, token1, token2, myswap_contract)
    ]
    return await execute_function(provider, calldata)


def ten_k_swap_liq_call(amount: float, amount_out: float, sender: int, token1: int, token2: int, contract: Contract):
    token1_dec = DECIMALS[token1]

    call = contract.functions["addLiquidity"].prepare(
            token1,
            token2,
            int(amount*(10**token1_dec)),
            int(amount_out - amount_out*slippage),
            int(amount*(10**token1_dec) - slippage*amount*(10**token1_dec)),
            int(amount_out - 2*amount_out*slippage),
            sender,
            int(time.time())+3600
            )
    return call

async def ten_k_swap_liq(amount: float, amount_out: float, token1: int, token2: int, provider: Account):
    token1_dec = DECIMALS[token1]
    token2_dec = DECIMALS[token2]
    if token1_dec == 18:
        amount_out = amount*(get_eth_price())
    elif token1_dec == 6:
        amount_out =  amount/(get_eth_price())

    ten_k_swap_contract = Contract(TEN_K_SWAP_CONTRACT, TEN_K_SWAP_ABI, provider)
    token1_contract = Contract(token1, ABIs[token1], provider)
    token2_contract = Contract(token2, ABIs[token2], provider)
    calldata = [
        approve_token_call(amount, TEN_K_SWAP_CONTRACT, token1_contract),
        approve_token_call(amount_out, TEN_K_SWAP_CONTRACT, token2_contract),
        ten_k_swap_liq_call(amount, amount_out*(10**token2_dec), provider.address, token1, token2, ten_k_swap_contract)
    ]
    return await execute_function(provider, calldata)




async def add_liq(amount: float, dex: str, token1: int, token2: int, provider: Account):
    token1_dec = DECIMALS[token1]
    token2_dec = DECIMALS[token2]
    
    while True:
        try:
            token1_balance = await provider.get_balance(token1)/10**token1_dec
            break
        except:
            logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] can't get balance. Too many attempts ")
            await sleeping('0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::], True)
    if token1_balance < amount:
        logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] not enough token for adding to pool: balance {token1_balance}, required {amount}")
        await sleeping('0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::], True)
        return NOT_ENOUGH_NATIVE, ""
    
    
    while True:
        try:
            token2_balance = await provider.get_balance(token2)/10**token2_dec
            break
        except:
            logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] can't get balance. Too many attempts ")
            await sleeping('0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::], True)
    if token1_dec == 18:
        amount_out = amount*(get_eth_price())
    elif token1_dec == 6:
        amount_out =  (amount/(get_eth_price()))

    if amount_out > token2_balance:
        logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] not enough token for adding to pool: balance {token2_balance}, required {amount_out}")
        await sleeping('0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::], True)
        return NOT_ENOUGH_NATIVE, ""
    
    
    if dex == "jedi":
        res = await jediswap_liq(amount, amount_out, token1, token2, provider)
    elif dex == "my":
        res = await myswap_liq(amount, amount_out-amount_out*0.05, token1, token2, provider)
    elif dex == "10k":
        res = await ten_k_swap_liq(amount, amount_out, token1, token2, provider)
    else:
        logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] chosen wrong dex for swap: {dex}; supported: jedi, my, 10k")
        await sleeping('0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::], True)
        return WRONG_CHOICE, ""
    return res

async def add_liq_task(account: Account, delay: int):
    await asyncio.sleep(delay)
    limit = get_random_value_int(SETTINGS["AddLiqAmount"])
    while limit > 0:
        limit -= 1
        dex = random.choice(SETTINGS["LiqDEXs"])
        
        while True:
            try:
                eth_balacne = await account.get_balance()
                break
            except Exception as e:
                logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got error while trying to get balance: {e}")
                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
        swap_amount_eth = ((eth_balacne * get_random_value(SETTINGS["LiqWorkPercent"]))/1e18)/2
        
        
        token = random.choice(SETTINGS["LiqTokens"])


        try:
            token_contract = TOKENS[token]
        except:
            logger.error(f"Selected unsupported token ({token}), please choose one from this (USDT, USDC)")
            input("Please restart soft with correct settings")

        token_amount = get_eth_price()*swap_amount_eth
        while True:
            try:
                token_balance = await account.get_balance(token_contract)/1e6
                break
            except Exception as e:
                logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got error while trying to get balance: {e}")
                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
        if dex not in SUPPORTED_FOR_LIQ:
            logger.error(f"Selected unsupported DEX ({dex}), please choose one from this (jedi, my, 10k, sith)")
            input("Please restart soft with correct settings")
        
        logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] going to add liquidity in ETH/{token} pair on {dex}swap for {swap_amount_eth} ETH and {token_amount} {token}")
        
        if token_amount > token_balance:
            need_usd = (token_amount-token_balance) + 0.1*(token_amount-token_balance)
            need_eth = need_usd/get_eth_price()
            logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] not enough stables for adding liquidity, going to make swap")
            if (await swap(need_eth, dex, ETH_TOKEN_CONTRACT, token_contract, account))[0] == SUCCESS:
                out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] = out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] + f"swap {need_eth} ETH for {token} on {dex}swap\n"
                
            await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])
        await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])

        if (await add_liq(swap_amount_eth, dex, ETH_TOKEN_CONTRACT, token_contract, account))[0] == SUCCESS:
            out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] = out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] + f"add liquidity in ETH/{token} pair on {dex}swap for {swap_amount_eth} ETH and {token_amount} {token}\n"

        
        await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])


def task_4(stark_keys):
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
        tasks.append(loop.create_task(add_liq_task(account, delay)))
        delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])

    
    loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

    res = ""

    for i in out_wallets_result:
        res += f"{i}:\n{out_wallets_result[i]}\n"
        
    with open("log.txt", "w") as f:
        f.write(res)

