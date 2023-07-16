from utils import *


def jediswap_remove_liq_call(amount: int, sender: int, token1: int, token2: int, token1_amount: int, token2_amount: int, contract: Contract):


    call = contract.functions["remove_liquidity"].prepare(
            token1,
            token2,
            amount,
            int(token1_amount*0.8),
            int(token2_amount*0.8),
            sender,
            int(time.time())+3600
            )
    return call

async def jediswap_remove_liq(token: int, provider: Account):
    
    while True:
        try:
            liq_balance = await provider.get_balance(LIQ_CONTRACTS["jedi"][token])
            break
        except Exception as e:
            logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] can't get balance. {e}")
            await sleeping('0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::], True)
    if liq_balance <= 0:
        return NOT_ENOUGH_NATIVE, ""
    usd_bal = liq_balance/LIQ_PRICES["jedi"]
    eth_price = get_eth_price()
    usd_amount = int((10**DECIMALS[token])*usd_bal/2)
    eth_amount = int((10**DECIMALS[ETH_TOKEN_CONTRACT])*((usd_bal/2)/eth_price))

    jediswap_contract = Contract(JEDISWAP_CONTRACT, JEDISWAP_ABI, provider)
    token_contract = Contract(LIQ_CONTRACTS["jedi"][token], ABIs[token], provider)
    calldata = [
        approve_token_call(liq_balance, JEDISWAP_CONTRACT, token_contract),
        jediswap_remove_liq_call(liq_balance, provider.address, ETH_TOKEN_CONTRACT, token, eth_amount, usd_amount, jediswap_contract)
    ]
    return await execute_function(provider, calldata)

def myswap_remove_liq_call(amount: int, sender: int, token1: int, token2: int, token1_amount: int, token2_amount: int, contract: Contract):
    pool_id = MYSWAP_POOLS[f"{token1}:{token2}"]

    call = contract.functions["withdraw_liquidity"].prepare(
            pool_id,
            amount,
            int(token1_amount*0.8),
            int(token2_amount*0.8)
            )
    return call

async def myswap_remove_liq(token: int, provider: Account):
    
    while True:
        try:
            liq_balance = await provider.get_balance(LIQ_CONTRACTS["my"][token])
            break
        except Exception as e:
            logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] can't get balance. {e}")
            await sleeping('0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::], True)
    if liq_balance <= 0:
        return NOT_ENOUGH_NATIVE, ""
    usd_bal = liq_balance/LIQ_PRICES["my"]
    eth_price = get_eth_price()
    usd_amount = int((10**DECIMALS[token])*usd_bal/2)
    eth_amount = int((10**DECIMALS[ETH_TOKEN_CONTRACT])*((usd_bal/2)/eth_price))

    myswap_contract = Contract(MYSWAP_CONTRACT, MYSWAP_ABI, provider)
    token_contract = Contract(LIQ_CONTRACTS["my"][token], ABIs[token], provider)
    calldata = [
        approve_token_call(liq_balance, MYSWAP_CONTRACT, token_contract),
        myswap_remove_liq_call(liq_balance, provider.address, ETH_TOKEN_CONTRACT, token, eth_amount, usd_amount, myswap_contract)
    ]
    return await execute_function(provider, calldata)

def ten_k_swap_remove_liq_call(amount: int, sender: int, token1: int, token2: int, token1_amount: int, token2_amount: int, contract: Contract):


    call = contract.functions["removeLiquidity"].prepare(
            token1,
            token2,
            amount,
            int(token1_amount*0.8),
            int(token2_amount*0.8),
            sender,
            int(time.time())+3600
            )
    return call

async def ten_k_swap_remove_liq(token: int, provider: Account):
    
    while True:
        try:
            liq_balance = await provider.get_balance(LIQ_CONTRACTS["10k"][token])
            break
        except Exception as e:
            logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] can't get balance. {e}")
            await sleeping('0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::], True)
    if liq_balance <= 0:
        return NOT_ENOUGH_NATIVE, ""
    usd_bal = liq_balance/LIQ_PRICES["10k"]
    eth_price = get_eth_price()
    usd_amount = int((10**DECIMALS[token])*usd_bal/2)
    eth_amount = int((10**DECIMALS[ETH_TOKEN_CONTRACT])*((usd_bal/2)/eth_price))

    ten_k_swap_contract = Contract(TEN_K_SWAP_CONTRACT, TEN_K_SWAP_ABI, provider)
    token_contract = Contract(LIQ_CONTRACTS["10k"][token], ABIs[token], provider)
    calldata = [
        approve_token_call(liq_balance, TEN_K_SWAP_CONTRACT, token_contract),
        ten_k_swap_remove_liq_call(liq_balance, provider.address, ETH_TOKEN_CONTRACT, token, eth_amount, usd_amount, ten_k_swap_contract)
    ]
    return await execute_function(provider, calldata)

def sithswap_remove_liq_call(amount: int, sender: int, token1: int, token2: int, token1_amount: int, token2_amount: int, contract: Contract):


    call = contract.functions["removeLiquidity"].prepare(
            token1,
            token2,
            0,
            amount,
            int(token1_amount*0.8),
            int(token2_amount*0.8),
            sender,
            int(time.time())+3600
            )
    return call

async def sithswap_remove_liq(token: int, provider: Account):
    
    while True:
        try:
            liq_balance = await provider.get_balance(LIQ_CONTRACTS["sith"][token])
            break
        except Exception as e:
            logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] can't get balance. {e}")
            await sleeping('0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::], True)
    if liq_balance <= 0:
        return NOT_ENOUGH_NATIVE, ""
    usd_bal = liq_balance/LIQ_PRICES["sith"]
    eth_price = get_eth_price()
    usd_amount = int((10**DECIMALS[token])*usd_bal/2)
    eth_amount = int((10**DECIMALS[ETH_TOKEN_CONTRACT])*((usd_bal/2)/eth_price))

    sithswap_contract = Contract(SITHSWAP_CONTRACT, SITHSWAP_ABI, provider)
    token_contract = Contract(LIQ_CONTRACTS["sith"][token], ABIs[token], provider)
    calldata = [
        approve_token_call(liq_balance, SITHSWAP_CONTRACT, token_contract),
        sithswap_remove_liq_call(liq_balance, provider.address, ETH_TOKEN_CONTRACT, token, eth_amount, usd_amount, sithswap_contract)
    ]
    return await execute_function(provider, calldata)


async def remove_liq(dex: str, token2: int, provider: Account):

    if dex == "jedi":
        res = await jediswap_remove_liq(token2, provider)
    elif dex == "my":
        res = await myswap_remove_liq(token2, provider)
    elif dex == "10k":
        res = await ten_k_swap_remove_liq(token2, provider)

    else:
        logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] chosen wrong dex for swap: {dex}; supported: jedi, my, 10k")
        await sleeping('0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::], True)
        return WRONG_CHOICE, ""
    return res 



def task_5(stark_keys):
    loop = asyncio.new_event_loop()
    tasks = []  
    delay = 0
    for key in stark_keys:
        if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
            client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
        else:
            client = GatewayClient(net=MAINNET)
        account, call_data, salt, class_hash = import_argent_account(key, client)
        tasks.append(loop.create_task(remove_liq_task(account, delay)))
        delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])
    
    loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))


async def remove_liq_task(account: Account, delay: int):
    await asyncio.sleep(delay)
    for token in SETTINGS["LiqTokens"]:
        for dex in SETTINGS["LiqDEXs"]:
            try:
                token_contract = TOKENS[token]
            except:
                logger.error(f"Selected unsupported token ({token}), please choose one from this (USDT, USDC)")
                input("Please restart soft with correct settings")

            if dex not in SUPPORTED_FOR_LIQ:
                logger.error(f"Selected unsupported DEX ({dex}), please choose one from this (jedi, my, 10k, sith)")
                input("Please restart soft with correct settings")

            while True:
                try:
                    liq_balance = await account.get_balance(LIQ_CONTRACTS[dex][token_contract])
                    break
                except Exception as e:
                    logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] can't get balance. {e}")
                    await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
            if liq_balance <= 0:
                continue
            
            await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])
            
            logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] going to remove liquidity in ETH/{token} pair on {dex}swap")

            await remove_liq(dex, token_contract, account)
            await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])
