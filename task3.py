
from utils import *
from task2 import *


def task_3(stark_keys):
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
        tasks.append(loop.create_task(swap_to_eth(account, delay)))
        delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])


    loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

    res = ""

    for i in out_wallets_result:
        res += f"{i}:\n{out_wallets_result[i]}\n"
        
    with open("log.txt", "w") as f:
        f.write(res)


async def swap_to_eth(account: Account, delay: int, in_full = False):
    await asyncio.sleep(delay)
    if not in_full:
        for token in SETTINGS["Supported_tokens"]:
            try:
                token_contract = TOKENS[token]
            except:
                logger.error(f"Selected unsupported token ({token}), please choose one from this (USDT, USDC)")
                input("Please restart soft with correct settings")
            while True:
                try:
                    token_balance = await account.get_balance(token_contract) / 1e6
                    break
                except Exception as e:
                    logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got error while trying to get balance: {e}")
                    await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
            if token_balance <= SETTINGS["MINIMAL_SWAP_AMOUNTS"][token]:
                logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] {token} balance is {token_balance} which is lower than MINIMAL_SWAP_AMOUNTS in settings({SETTINGS['MINIMAL_SWAP_AMOUNTS'][token]})")
                continue
            dex = random.choice(SETTINGS["SwapDEXs"])

            if dex not in SUPPORTED_FOR_SWAPS:
                logger.error(f"Selected unsupported DEX ({dex}), please choose one from this (jedi, my, 10k, sith, anvu)")
                input("Please restart soft with correct settings")
            await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])

            logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] going to swap {token_balance} {token} for ETH on {dex}swap")


            if (await swap(token_balance, dex, token_contract, ETH_TOKEN_CONTRACT, account))[0] == SUCCESS:
                out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] = out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] + f"swap {token_balance} {token} for ETH on {dex}swap\n"

            await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])
    else:
        dist_token = random.choice(SETTINGS["toSaveFunds"])
        logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] going to save balance in {dist_token}")
        if dist_token == "USDT" or dist_token == "USDC":
            OPPOSITES = {
                "USDT": "USDC",
                "USDC": "USDT"
            }
            save_eth = get_random_value(SETTINGS["SaveEthOnBalance"])
            token1 = OPPOSITES[dist_token]
            token1_contract = TOKENS[token1]
            while True:
                try:
                    token1_balance = await account.get_balance(token1_contract) / 1e6
                    break
                except Exception as e:
                    logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got error while trying to get balance: {e}")
                    await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
            if token1_balance <= SETTINGS["MINIMAL_SWAP_AMOUNTS"][token1]:
                logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] {token1} balance is {token1_balance} which is lower than MINIMAL_SWAP_AMOUNTS in settings({SETTINGS['MINIMAL_SWAP_AMOUNTS'][token1]})")
            else:   
                dex = random.choice(SETTINGS["SwapDEXs"])

                if dex not in SUPPORTED_FOR_SWAPS:
                    logger.error(f"Selected unsupported DEX ({dex}), please choose one from this (jedi, my, 10k, sith, anvu)")
                    input("Please restart soft with correct settings")
                await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])

                logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] going to swap {token1_balance} {token1} for ETH on {dex}swap")

                if (await swap(token1_balance, dex, token1_contract, ETH_TOKEN_CONTRACT, account))[0] == SUCCESS:
                    out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] = out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] + f"swap {token1_balance} {token1} for ETH on {dex}swap\n"


                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])

            eth_contract = TOKENS["ETH"]

            while True:
                try:
                    eth_balance = await account.get_balance(eth_contract) / 1e18
                    break
                except Exception as e:
                    logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got error while trying to get balance: {e}")
                    await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
            
            to_swap = eth_balance - save_eth

            if to_swap <= 0:
                logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] ETH balance below SaveEthOnBalance. Will leave in ETH")
                return
            
            dex = random.choice(SETTINGS["SwapDEXs"])

            if dex not in SUPPORTED_FOR_SWAPS:
                logger.error(f"Selected unsupported DEX ({dex}), please choose one from this (jedi, my, 10k, sith, anvu)")
                input("Please restart soft with correct settings")

            await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])

            logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] going to swap {to_swap} ETH for {dist_token} on {dex}swap")

            if (await swap(to_swap, dex, eth_contract, TOKENS[dist_token], account))[0] == SUCCESS:
                out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] = out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] + f"swap {to_swap} ETH for {dist_token} on {dex}swap\n"

            await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])
        elif dist_token == "ETH":
            for token in SETTINGS["Supported_tokens"]:
                try:
                    token_contract = TOKENS[token]
                except:
                    logger.error(f"Selected unsupported token ({token}), please choose one from this (USDT, USDC)")
                    input("Please restart soft with correct settings")
                while True:
                    try:
                        token_balance = await account.get_balance(token_contract) / 1e6
                        break
                    except Exception as e:
                        logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got error while trying to get balance: {e}")
                        await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
                if token_balance <= SETTINGS["MINIMAL_SWAP_AMOUNTS"][token]:
                    logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] {token} balance is {token_balance} which is lower than MINIMAL_SWAP_AMOUNTS in settings({SETTINGS['MINIMAL_SWAP_AMOUNTS'][token]})")
                    continue
                dex = random.choice(SETTINGS["SwapDEXs"])

                if dex not in SUPPORTED_FOR_SWAPS:
                    logger.error(f"Selected unsupported DEX ({dex}), please choose one from this (jedi, my, 10k, sith, anvu)")
                    input("Please restart soft with correct settings")
                await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])

                logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] going to swap {token_balance} {token} for ETH on {dex}swap")


                if (await swap(token_balance, dex, token_contract, ETH_TOKEN_CONTRACT, account))[0] == SUCCESS:
                    out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] = out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] + f"swap {token_balance} {token} for ETH on {dex}swap\n"

                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])
        else:
            logger.error(f"Selected unsupported token for save({dist_token}). Please select one of this: USDT, USDC, ETH")




            
