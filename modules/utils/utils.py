from random import randint, uniform, choice
from asyncio import sleep, Event

import aiohttp
from web3 import AsyncWeb3
import json

from modules.utils.logger import logger, console_log
from modules.config import SETTINGS, SETTINGS_PATH, RPC_LIST, json_remove_comments

async def req(url: str, **kwargs):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, **kwargs) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    console_log.error("Bad status code, will try again")
    except Exception as error:
        console_log.error(f"Requests error: {error}")

async def req_post(url: str, **kwargs):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, **kwargs) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    console_log.error("Bad status code, will try again")
    except Exception as error:
        console_log.error(f"Requests error: {error}")

async def sleeping(address, error = False):
    if error:
        rand_time = randint(SETTINGS["ErrorSleepeng"][0], SETTINGS["ErrorSleepeng"][1])
    else:
        rand_time = randint(SETTINGS["TaskSleep"][0], SETTINGS["TaskSleep"][1])
    logger.info(f'[{address}] sleeping {rand_time} s')
    await sleep(rand_time)

async def handle_dangerous_request(func, message, address = "", *args):
    while True:
        try:
            return await func(*args)
        except Exception as e:
            pass
            logger.error(f"[{address}] {message}: {e}")
            await sleeping(address, True)

def get_random_value_int(param):
    return randint(param[0], param[1])

def get_random_value(param):
    return uniform(param[0], param[1])

def str_to_felt(text: str) -> int:
    b_text = bytes(text, 'UTF-8')
    return int.from_bytes(b_text, "big")

def get_bytes(value: str) -> str:
    i = len(value)
    return '0x' + ''.join('0' for k in range(64-i)) + value

def require_hexstr(hexstr: str):
    try:
        int(hexstr, 16)
        return True
    except:
        return False

def normalize_to_32_bytes(data: str):
    assert require_hexstr(data), "Not hexstr"
    return "0x" + "0"*(64 - len(hex(int(data, 16))[2::])) + hex(int(data, 16))[2::]


def decimal_to_int(qty, decimal):
    return int(qty * int("".join(["1"] + ["0"]*decimal)))


def get_pair_for_address_from_file(filename: str, address: str):
    address = address.lower()
    with open(f"{SETTINGS_PATH}{filename}", "r") as f:
        buff = f.read().lower().split("\n")
    pairs_raw = []
    for i in buff:
        if ";" in i:
            pairs_raw.append(i)

    for pair in pairs_raw:
        if pair.split(";")[0] == address:
            return pair.split(";")[1].lower()
        elif pair.split(";")[1] == address:
            return pair.split(";")[0].lower()
    return None



async def gas_locker(gas_lock: Event):
    w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(choice(RPC_LIST["ethereum"])))
    while True:
        while True:
            try:
                f = open(f"{SETTINGS_PATH}settings.json", "r")
                a = json_remove_comments(f.read())
                SETTINGS = json.loads(a)
                f.close()
                break
            except Exception as e:
                input("Error with settings.json. Please fix it and press Enter")
        max_gas = AsyncWeb3.to_wei(SETTINGS["MaxEthGwei"], 'gwei')
        try:
            gas_price = await w3.eth.gas_price
            if gas_price > max_gas:
                h_gas, h_max = AsyncWeb3.from_wei(gas_price, 'gwei'), AsyncWeb3.from_wei(max_gas, 'gwei')
                gas_lock.set()
                logger.info(f"[GAS LOCKER] GAS ({h_gas}) HIGH new wallets are not loading")
            else:
                gas_lock.clear()
                h_gas, h_max = AsyncWeb3.from_wei(gas_price, 'gwei'), AsyncWeb3.from_wei(max_gas, 'gwei')
                logger.info(f"[GAS LOCKER] GAS ({h_gas}) NORMAL new wallets are loading")
            
        except Exception as error:
            print(error)
        await sleep(randint(20, 40))
