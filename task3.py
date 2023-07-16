
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
        tasks.append(loop.create_task(swap_to_eth(account, delay)))
        delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])


    loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))


async def swap_to_eth(account: Account, delay: int):
    await asyncio.sleep(delay)
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

        
        await swap(token_balance, dex, token_contract, ETH_TOKEN_CONTRACT, account)
        await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])