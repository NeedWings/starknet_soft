
from utils import *
from task2 import *


def task_3(stark_keys):
    loop = asyncio.new_event_loop()
    tasks = []
    delay = 0
    for key in stark_keys:
        account, call_data, salt, class_hash = import_argent_account(key)
        tasks.append(loop.create_task(swap_to_eth(account, delay)))
        delay += get_random_value_int(SETTINGS["TaskSleep"])


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
            except:
                logger.error(f"[{hex(account.address)}] got error while trying to get balance: too many requests")
                await sleeping(hex(account.address), True)
        if token_balance == 0:
            continue
        dex = random.choice(SETTINGS["SwapDEXs"])
        
        if dex not in SUPPORTED_FOR_SWAPS:
            logger.error(f"Selected unsupported DEX ({dex}), please choose one from this (jedi, my, 10k, sith, anvu)")
            input("Please restart soft with correct settings")
        await wait_for_better_eth_gwei(hex(account.address))

        logger.info(f"[{hex(account.address)}] going to swap {token_balance} {token} for ETH on {dex}swap")

        
        await swap(token_balance, dex, token_contract, ETH_TOKEN_CONTRACT, account)
        await sleeping(hex(account.address))