from time import sleep
from random import shuffle
import asyncio
from asyncio import Event

import inquirer
from termcolor import colored
from eth_account import Account as ethAccount
from inquirer.themes import load_theme_from_dict as loadth
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.full_node_client import FullNodeClient

try:
    from modules.utils.utils import get_random_value, get_random_value_int, gas_locker
    from modules.routers.activity.main_router import MainRouter
    from modules.config import autosoft, subs_text, RPC_LIST

    from modules.utils.starter import *
    

    if __name__ == "__main__":
        pass
        checking_license()

    def get_action() -> str:
        theme = {
            "Question": {
                "brackets_color": "bright_yellow"
            },
            "List": {
                "selection_color": "bright_blue"
            }
        }

        question = [
            inquirer.List(
                "action",
                message=colored("Choose soft work task", 'light_yellow'),
                choices=[
                    "Off bridge",
                    "Off bridge different wallet(EVM)",
                    "Orbiter",
                    "Orbiter different wallet(EVM)",
                    "withdraw",
                    "withdraw different wallet(EVM)",
                    "",
                    "random swaps",
                    "swap to one token",
                    "",
                    "add liquidity",
                    "remove liquidity",
                    "",
                    "lending task",
                    "remove from lend",
                    "return borrowed tokens",
                    "collateral on zklend",
                    "",
                    "dmail",
                    "starkstars",
                    "starknet id",
                    "bids on flex",
                    "bids on unframed",
                    "bids on element",
                    "upgrade argent",
                    "upgrade braavos",
                    "deploy accounts",
                    "",
                    "okx withdraw",
                    "okx sender",
                    "",
                    "stats",
                    "",
                    "own tasks",
                    "",
                    "encrypt_secrets",
                ],
            )
        ]
        action = inquirer.prompt(question, theme=loadth(theme))['action']
        return action

    def main():
        with open(f"{SETTINGS_PATH}starkstats.csv", "w") as f:
            f.write("address;txn count;ETH balance;USDC balance;USDT balance;DAI balance;WBTC balance;WSTETH balance;LORDS balance;Have liq;Have lend")
        global RPC_LIST
        gas_lock = Event()
        one_thread_lock = Event()
        if SETTINGS["UseOurRPCStark"]:
            RPC_LIST["starknet"] = ["http://23.88.45.175:6070/"]

        print(autosoft)
        print(subs_text)
        print("\n")
        f = open(f"{SETTINGS_PATH}to_run_addresses.txt", "r")
        addresses = f.read().lower().split("\n")
        f.close()
        action = get_action()
        if action == "Off bridge":
            task_number = 110
        elif action == "Off bridge different wallet(EVM)":
            task_number = 111
        elif action == "Orbiter":
            task_number = 120
        elif action == "Orbiter different wallet(EVM)":
            task_number = 121
        elif action == "withdraw":
            task_number = 130
        elif action == "withdraw different wallet(EVM)":
            task_number = 131
        elif action == "random swaps":
            task_number = 21
        elif action == "swap to one token":
            task_number = 22
        elif action == "add liquidity":
            task_number = 31
        elif action == "remove liquidity":
            task_number = 32
        elif action == "lending task":
            task_number = 41
        elif action == "remove from lend":
            task_number = 42
        elif action == "return borrowed tokens":
            task_number = 43
        elif action == "collateral on zklend":
            task_number = 44
        elif action == "dmail":
            task_number = 51
        elif action == "starkstars":
            task_number = 52
        elif action == "starknet id":
            task_number = 53
        elif action == "bids on flex":
            task_number = 541
        elif action == "bids on unframed":
            task_number = 542
        elif action == "bids on element":
            task_number = 543
        elif action == "upgrade argent":
            task_number = 551
        elif action == "upgrade braavos":
            task_number = 552
        elif action == "deploy accounts":
            task_number = 56
        elif action == "okx withdraw":
            task_number = 61
        elif action == "okx sender":
            task_number = 62
        elif action == "stats":
            task_number = 71
        elif action == "own tasks":
            task_number = 0
        elif action == "encrypt_secrets":
            task_number = 11
        for i in range(len(addresses)):
            if len(addresses[i]) < 50:
                addresses[i] = "0x" + "0"*(42-len(addresses[i])) + addresses[i][2::]
            else:
                addresses[i] = "0x" + "0"*(66-len(addresses[i])) + addresses[i][2::]
        if task_number == 11:
            encode_secrets()
        else:    
            private_keys = decode_secrets()
            accounts, counter = transform_keys(private_keys, addresses)
            print(f"Soft found {counter} keys to work")
            tasks = []

            if task_number != 71:
                shuffle(accounts)
                if SETTINGS["delayed_start"]:
                    console_log.info(f"waiting delayed start: {SETTINGS['delayed_start_time']} hours")
                    sleep(SETTINGS['delayed_start_time']*3600)

            
            print(f"Bot found {counter} private keys to work")
            
            if SETTINGS["UseProxies"]:
                loop = asyncio.new_event_loop()

                f = open(f"{SETTINGS_PATH}proxies.txt", "r")
                proxies_raw = f.read().split("\n")
                f.close()

                proxies = []

                for proxy in proxies_raw:
                    proxies.append(proxy.split("@"))
                if task_number != 10 and task_number != 16:
                    shuffle(proxies)
                proxy_dict = {}
                args = []
                for proxy in proxies:
                    if f"http://{proxy[0]}@{proxy[1]}" in proxy_dict.keys():
                        proxy_dict[f"http://{proxy[0]}@{proxy[1]}"].append(('0x' + '0'*(66-len(proxy[2])) + proxy[2][2::]).lower())
                    else:
                        proxy_dict[f"http://{proxy[0]}@{proxy[1]}"] = [('0x' + '0'*(66-len(proxy[2])) + proxy[2][2::]).lower()]

                counter = 1
                delay = 0
                for proxy in proxy_dict:

                    addresses = proxy_dict[proxy]
                    for key in accounts:
                        address =  Account.get_starknet_address_from_private(hex(key))
                        
                        if address in addresses:
                            print(f"[{address}] connected to proxy: {proxy}")
                            tasks.append(loop.create_task(MainRouter(key, delay, task_number, proxy=proxy).start(gas_lock=gas_lock, one_thread_lock=one_thread_lock)))
                            delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])
                
            else:
                loop = asyncio.new_event_loop()

                delay = 0
                for account in accounts:
                    tasks.append(loop.create_task(MainRouter(account, delay, task_number).start(gas_lock=gas_lock, one_thread_lock=one_thread_lock)))
                    delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])
            tasks.append(loop.create_task(gas_locker(gas_lock=gas_lock)))
            loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))
           
    if __name__ == "__main__":
        while True:
            main()
            input("Soft successfully end work")

except Exception as e:
    console_log.error(f"Unexpected error: {e}")

input("Soft successfully end work")
