from utils import *


def myswap_call_quest(amount: float, token1: int, token2: int, contract: Contract):
    token1_dec = DECIMALS[token1]
    token2_dec = DECIMALS[token2]
    eth_price = get_eth_price()
    wstEth_price = get_wsteth_price()
    if token1 == ETH_TOKEN_CONTRACT:
        amount_out = amount * (eth_price/wstEth_price)
    else:
        amount_out = amount * (wstEth_price/eth_price)
    amount_out = int((amount_out - amount_out * slippage * 2) * token2_dec)
    call = contract.functions["swap"].prepare(
            MYSWAP_POOLS[f"{token1}:{token2}"],
            token1,
            int(amount*(10**token1_dec)), 
            amount_out
            )
    return call

async def myswap_quest(amount: float, token1: int, token2: int, provider: Account):
    myswap_contract = Contract(MYSWAP_CONTRACT, MYSWAP_ABI, provider)
    token_contract = Contract(token1, ABIs[token1], provider)
    calldata = [
        approve_token_call(amount, MYSWAP_CONTRACT, token_contract),
        myswap_call_quest(amount, token1, token2, myswap_contract)
    ]

    return await execute_function(provider, calldata)



async def swap_myswap_task(amount: float, dex: str, token1: int, token2: int, provider: Account):
    while True:
        try:
            token1_balance = await provider.get_balance(token1)/10**DECIMALS[token1]
            break
        except:
            logger.error(f"[{hex(provider.address)}] can't get balance. Too many attempts ")
            await sleeping(hex(provider.address), True)
    if token1_balance < amount:
        logger.error(f"[{hex(provider.address)}] not enough token for swap: balance {token1_balance}, required {amount}")
        await sleeping(hex(provider.address), True)
        return NOT_ENOUGH_NATIVE, ""

    if dex == "my":
        res = await myswap_quest(amount, token1, token2, provider)
    else:
        logger.error(f"[{hex(provider.address)}] chosen wrong dex for swap: {dex}; supported:  my")
        await sleeping(hex(provider.address), True)
        return WRONG_CHOICE, ""
    return res

async def mint_myswap_quest_nft(provider: Account):
    mint_contract = Contract(0x07c351118b538157458aebedb92212624027f4813ab39cd7971df9f1720f7633, MYSWAP_NFT_QUEST_ABI, provider)
    i = 0
    while retries_limit > i:
        resp = req(f"https://api.braavos.app/v1/notifications/myswap_nft100?address={hex(provider.address)}")
        try:
            a = resp['sig']
            break
        except:
            logger.error(f"[{hex(provider.address)}] myswap sent bad data :( trying again")
            await sleeping(hex(provider.address), True)
        i+=1
    if retries_limit <= i:
        logger.error(f"[{hex(provider.address)}] max retries limit reached")
        return MAX_RETRIES_LIMIT_REACHED
    call = mint_contract.functions["signed_mint"].prepare(
            100,
            int(resp["sig"]["r"], 16),
            int(resp["sig"]["s"], 16) 
            )
    calldata = [
        call
    ]

    return await execute_function(provider, calldata)


async def random_swaps_myswap_quest(account: Account, delay: int):
    await asyncio.sleep(delay)
    while True:
        try:
            eth_balacne = await account.get_balance()/1e18
            break
        except:
            logger.error(f"[{hex(account.address)}] got error while trying to get balance: too many requests")
            await sleeping(hex(account.address), True)
    limit = int((int(0.03/(eth_balacne*0.6))+1) / 2 ) + 1
    while limit > 0:
        limit -= 1
        dex = "my"
        eth_price = get_eth_price()
        wstEth_price = get_wsteth_price()
        while True:
            try:
                eth_balacne = await account.get_balance()
                break
            except:
                logger.error(f"[{hex(account.address)}] got error while trying to get balance: too many requests")
                await sleeping(hex(account.address), True)
        swap_amount_eth = (eth_balacne * 0.8)/1e18
        
        wstEth_value = swap_amount_eth * (eth_price/wstEth_price)
        
        token = "wstETH"
        try:
            token_contract = TOKENS[token]
        except:
            logger.error(f"Selected unsupported token ({token}), please choose one from this (USDT, USDC)")
            input("Please restart soft with correct settings")




        if dex != "my":
            logger.error(f"Selected unsupported DEX ({dex}), please choose one from this (my)")
            input("Please restart soft with correct settings")
        
        await wait_for_better_eth_gwei(hex(account.address))

        logger.info(f"[{hex(account.address)}] going to swap {swap_amount_eth} ETH for {token} on {dex}swap")

        await swap_myswap_task(swap_amount_eth, dex, ETH_TOKEN_CONTRACT, token_contract, account)
        
        await sleeping(hex(account.address))

        while True:
            try:
                wsteth_balacne = await account.get_balance(token_contract)
                break
            except:
                logger.error(f"[{hex(account.address)}] got error while trying to get balance: too many requests")
                await sleeping(hex(account.address), True)

        swap_amount_wsteth = wsteth_balacne/1e18 - (wsteth_balacne/1e18)*0.02
        
        await wait_for_better_eth_gwei(hex(account.address))

        logger.info(f"[{hex(account.address)}] going to swap {swap_amount_wsteth} wstETH for ETH on {dex}swap")

        await swap_myswap_task(swap_amount_wsteth, dex, token_contract, ETH_TOKEN_CONTRACT, account)
        
        await sleeping(hex(account.address))

    logger.info(f"[{hex(account.address)}] going to mint nft")

    await mint_myswap_quest_nft(account)

    await sleeping(hex(account.address))
    

   


def myswap_task(stark_keys):
    loop = asyncio.new_event_loop()
    tasks = []
    delay = 0
    for key in stark_keys:
        account, call_data, salt, class_hash = import_argent_account(key)
        tasks.append(loop.create_task(random_swaps_myswap_quest(account, delay)))
        delay += get_random_value_int(SETTINGS["TaskSleep"])

    loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

async def myswap_mint_only(account: Account, delay: int):
    await asyncio.sleep(delay)

    logger.info(f"[{hex(account.address)}] going to mint nft")

    await mint_myswap_quest_nft(account)

    await sleeping(hex(account.address))

def myswap_task_mint(stark_keys):
    loop = asyncio.new_event_loop()
    tasks = []
    delay = 0
    for key in stark_keys:
        account, call_data, salt, class_hash = import_argent_account(key)
        tasks.append(loop.create_task(myswap_mint_only(account, delay)))
        delay += get_random_value_int(SETTINGS["TaskSleep"])

    loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))