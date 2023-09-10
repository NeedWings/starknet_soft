from task2 import *

async def random_swaps_fibrous_quest(account: Account, delay: int):
    await asyncio.sleep(delay)

    val = 0
    while val < 11:
        await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])
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
            val += usd_value
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
                pass
        else:
            dex = random.choice(SETTINGS["SwapDEXs"])
            if token_contract == USDT_TOKEN_CONTRACT:
                token = "USDT"
            else:
                token = "USDC"
            token_balance = max(balances) * get_random_value(SETTINGS["WorkPercent"])
            val += token_balance
            if dex not in SUPPORTED_FOR_SWAPS:
                logger.error(f"Selected unsupported DEX ({dex}), please choose one from this (jedi, my, 10k, sith, anvu, fibrous)")
                input("Please restart soft with correct settings")
            await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])

            logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] going to swap {token_balance} {token} for ETH on {dex}swap")


            if (await swap(token_balance, dex, token_contract, ETH_TOKEN_CONTRACT, account))[0] == SUCCESS:
                pass
            await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])

    

   


def fibrous_task(stark_keys):
    SETTINGS["LiqDEXs"] = ["fibrous"]
    SETTINGS["SwapDEXs"] = ["fibrous"]
    loop = asyncio.new_event_loop()
    tasks = []
    delay = 0
    for key in stark_keys:
        if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
        else:
            client = GatewayClient(net=MAINNET)
        account, call_data, salt, class_hash = import_argent_account(key, client)
        tasks.append(loop.create_task(random_swaps_fibrous_quest(account, delay)))
        delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])

    loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

