from abi import *
from starknet_py.hash import transaction 
from starknet_py.hash.address import compute_address
from starknet_py.net.account.account import Account as StarkNativeAccount
from starknet_py.net.client import Client
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.networks import MAINNET
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract, PreparedFunctionCall
from starknet_py.hash.utils import message_signature, private_to_stark_key, verify_message_signature, compute_hash_on_elements
from starknet_py.net.models import AddressRepresentation, StarknetChainId, parse_address
from starknet_py.net.account.account_deployment_result import AccountDeploymentResult
from starknet_py.net.account.account import _add_max_fee_to_transaction
from starknet_py.net.signer import BaseSigner
from starknet_py.utils.iterable import ensure_iterable
from starknet_py.net.models.transaction import (
    AccountTransaction,
    Declare,
    DeclareV2,
    DeployAccount,
    Invoke,
)
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union, cast
from starknet_py.constants import DEFAULT_ENTRY_POINT_SELECTOR
from starknet_py.hash.transaction import (
    TransactionHashPrefix,
    compute_declare_transaction_hash,
    compute_declare_v2_transaction_hash,
    compute_deploy_account_transaction_hash,
    compute_transaction_hash,
)
from starknet_py.net.client_models import (
    Call,
    Calls,
    EstimatedFee,
    Hash,
    SentTransactionResponse,
    Tag,
)
from random import shuffle
import multiprocessing
from threading import Thread
try:
    import Crypto.Hash._keccak
    import cytoolz._signatures
    import Crypto.Cipher._raw_ecb
    import Crypto.Cipher._raw_cbc
    import Crypto.Cipher._raw_aes
    import Crypto.Cipher._raw_cfb
    import Crypto.Cipher._raw_ctr
    import Crypto.Cipher._raw_des
    import Crypto.Cipher._raw_aes
    import Crypto.Cipher._raw_ofb
    import Crypto.Cipher._raw_aesni
    import Crypto.Cipher._raw_des3
    import Crypto.Cipher._raw_ofb
    import Crypto.Cipher._raw_ocb
    import Crypto.Cipher._raw_eksblowfish
    import Crypto.Util._strxor
    import Crypto.Util._raw_api
    import Crypto.Util._cpu_features
    import Crypto.Util._cpuid_c
    import Crypto.Util._file_system
    import Crypto.Util._strxor
    import Crypto.Hash._BLAKE2b
    import Crypto.Hash._BLAKE2s
    import Crypto.Hash._ghash_clmul
    import Crypto.Hash._ghash_portable
    import Crypto.Hash._SHA1
    import Crypto.Hash._SHA224
    import Crypto.Hash._SHA256
    import Crypto.Hash._SHA384
    import Crypto.Hash._SHA512
    import Crypto.Hash._MD2
    import Crypto.Hash._MD4
    import Crypto.Hash._MD5
    import Crypto.Cipher._Salsa20
    import Crypto.Cipher._ARC4
    import Crypto.Cipher._EKSBlowfish
    import Crypto.Cipher._chacha20
    import Crypto.Protocol._scrypt
    import Crypto.PublicKey._ec_ws
    import Crypto.PublicKey._ed25519
    import Crypto.PublicKey._ed448
    import Crypto.PublicKey._ed448
    import Crypto.PublicKey._openssh
    import Crypto.PublicKey._x25519
    import Crypto
    import eth_hash.backends.pycryptodome
except:
    pass
from eth_hash.auto import keccak
import random
import time
import json
import asyncio
import base64
from typing import (
    Optional
)
from typing_extensions import Literal
import requests
from web3 import Web3
import uuid
import decimal
from os import getcwd
import os
import base64
from cryptography.fernet import Fernet
import getpass
import hashlib
import sys
import socket
import wmi
from aiohttp import ClientSession
import sys, os
import inquirer
from termcolor import colored
from inquirer.themes import load_theme_from_dict as loadth


def override_where():
    """ overrides certifi.core.where to return actual location of cacert.pem"""
    # change this to match the location of cacert.pem
    return os.path.abspath("data/cacert.pem")


# is the program compiled?
if True:
    import certifi.core

    os.environ["REQUESTS_CA_BUNDLE"] = override_where()
    certifi.core.where = override_where

    # delay importing until after where() has been replaced
    import requests.utils
    import requests.adapters
    # replace these variables in case these modules were
    # imported before we replaced certifi.core.where
    requests.utils.DEFAULT_CA_BUNDLE_PATH = override_where()
    requests.adapters.DEFAULT_CA_BUNDLE_PATH = override_where()

def str_to_felt(text: str) -> int:
    b_text = bytes(text, 'UTF-8')
    return int.from_bytes(b_text, "big")

def get_bytes(value: str) -> str:
    i = len(value)
    return '0x' + ''.join('0' for k in range(64-i)) + value

def get_orbiter_value(base_num: float):
    base_num_dec = decimal.Decimal(str(base_num))
    orbiter_amount_dec = decimal.Decimal(str(0.000000000000009004))
    difference = base_num_dec - orbiter_amount_dec
    random_offset = decimal.Decimal(str(random.uniform(-0.000000000000001, 0.000000000000001)))
    result_dec = difference + random_offset
    orbiter_str = "9004"
    result_str = '{:.18f}'.format(result_dec.quantize(decimal.Decimal('0.000000000000000001')))
    result_str = result_str[:-4] + orbiter_str
    return decimal.Decimal(result_str)

def json_remove_comments(invalid_json: str):
    comment_start = -1
    for char in range(len(invalid_json)):
        if invalid_json[char:char+4] == ", //":
                comment_start = char+1
        
        if invalid_json[char] == "\n" and comment_start != -1:
            invalid_json = invalid_json[0:comment_start] + invalid_json[char:len(invalid_json)]
            return json_remove_comments(invalid_json)
    return invalid_json


autosoft = """

 _______          _________ _______  _______  _______  _______ _________
(  ___  )|\     /|\__   __/(  ___  )(  ____ \(  ___  )(  ____ \\__   __/
| (   ) || )   ( |   ) (   | (   ) || (    \/| (   ) || (    \/   ) (   
| (___) || |   | |   | |   | |   | || (_____ | |   | || (__       | |   
|  ___  || |   | |   | |   | |   | |(_____  )| |   | ||  __)      | |   
| (   ) || |   | |   | |   | |   | |      ) || |   | || (         | |   
| )   ( || (___) |   | |   | (___) |/\____) || (___) || )         | |   
|/     \|(_______)   )_(   (_______)\_______)(_______)|/          )_(   

"""
subs_text = """
You have purchased an AutoSoft software license.
Thank you for your trust.
Link to the channel with announcements: t.me/swiper_tools
Ask all questions in our chat.

"""

KEY = "CEy426oSSaOTWDPgtuKxm1nS2uWN_4-L_eyt0dmAr40="
SETTINGS_PATH = getcwd() + '\\data\\'

CONTRACT_ADDRESS_PREFIX = str_to_felt('STARKNET_CONTRACT_ADDRESS')
UNIVERSAL_DEPLOYER_PREFIX = str_to_felt('UniversalDeployerContract')


WETH = {
    "ARBITRUM_MAINNET": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
}

ROUTES = {
    "ARBITRUM_MAINNET": {
        "USDC": "0x02ff970a61a04b1ca14834a43f5de4533ebddb5cc801ffff0115e444da5b343c5a0931f5d3e85d158d1efc3d4000fc506aaa1340b4dedffd88be278bee058952d6740182af49447d8a07e3bd95bd0d56f35241523fbab101ffff0200",
        "USDT": "0x02fd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb901ffff00cb0e5bfa72bbb4d16ab5aa0c60601c438f04b4ad00fc506aaa1340b4dedffd88be278bee058952d6740182af49447d8a07e3bd95bd0d56f35241523fbab101ffff0200"
    }
}

STARKGATE_CONTRACT = "0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419"
ORBITER_CONTRACTS_REC = "0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8"
ORBITER_CONTRACT = "0xD9D74a29307cc6Fc8BF424ee4217f1A587FBc8Dc"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

try:
    f = open(f"{SETTINGS_PATH}settings.json", "r")
    a = json_remove_comments(f.read())
    SETTINGS = json.loads(a)
    f.close()
except Exception as e:
    input("Error with settings.json")
    exit()

retries_limit = SETTINGS["RetriesLimit"]


ETH_RPC = SETTINGS["RPC"]["ETHEREUM_MAINNET"]
OPTI_RPC = SETTINGS["RPC"]["OPTIMISM_MAINNET"]
ARB_RPC = SETTINGS["RPC"]["ARBITRUM_MAINNET"]
BSC_RPC = SETTINGS["RPC"]["BSC_MAINNET"]
POLYGON_RPC = SETTINGS["RPC"]["POLYGON_MAINNET"]
AVAX_RPC = SETTINGS["RPC"]["AVALANCHE_MAINNET"]

RPC_FOR_LAYERSWAP = {
    "ETHEREUM_MAINNET": ETH_RPC,
    "OPTIMISM_MAINNET": OPTI_RPC,
    "ARBITRUM_MAINNET": ARB_RPC
}

RPC_OTHER = {
    "ETHEREUM_MAINNET": ETH_RPC,
    "OPTIMISM_MAINNET": OPTI_RPC,
    "ARBITRUM_MAINNET": ARB_RPC,
    "BSC_MAINNET": BSC_RPC,
    "POLYGON_MAINNET": POLYGON_RPC,
    "AVALANCHE_MAINNET": AVAX_RPC,
}

USDC_CONTRACTS = {
    "ARBITRUM_MAINNET"  : "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
    "AVALANCHE_MAINNET" : "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
    "POLYGON_MAINNET"   : "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
    "OPTIMISM_MAINNET"  : "0x7F5c764cBc14f9669B88837ca1490cCa17c31607",
    "ETHEREUM_MAINNET"  : "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
}

USDT_CONTRACTS = {
    "ARBITRUM_MAINNET"  : "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
    "BSC_MAINNET"       : "0x55d398326f99059fF775485246999027B3197955",
    "AVALANCHE_MAINNET" : "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7",
    "POLYGON_MAINNET"   : "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
    "ETHEREUM_MAINNET"  : "0xdAC17F958D2ee523a2206206994597C13D831ec7"
}

STARGATE_CONTRACTS = {
    'AVALANCHE_MAINNET' : '0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
    'POLYGON_MAINNET'   : '0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
    'BSC_MAINNET'       : '0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8',
    'ARBITRUM_MAINNET'  : '0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614',
    'OPTIMISM_MAINNET'  : '0xB0D502E938ed5f4df2E681fE6E419ff29631d62b',
    'ETHEREUM_MAINNET'  : '0x8731d54E9D02c286767d56ac03e8037C07e01e98'
}

ASSETS_TYPES = {
    "ARBITRUM_MAINNET"  : [1, 2],
    "BSC_MAINNET"       : [2],
    "AVALANCHE_MAINNET" : [1, 2],
    "POLYGON_MAINNET"   : [1, 2],
    "OPTIMISM_MAINNET"  : [1],
    "ETHEREUM_MAINNET"  : [1, 2]
}

LAYERZERO_CHAINS_ID = {
    'AVALANCHE_MAINNET' : 106,
    'POLYGON_MAINNET'   : 109,
    'ETHEREUM_MAINNET'  : 101,
    'BSC_MAINNET'       : 102,
    'ARBITRUM_MAINNET'  : 110,
    'OPTIMISM_MAINNET'  : 111
}

SUSHI_SWAP = {
    "ARBITRUM_MAINNET": "0xfc506AaA1340b4dedFfd88bE278bEe058952D674"
}

MASK_250 = 2**250 - 1


proxy_dict_cfg = {

}

NATIVE_TOKENS_SYMBOLS = {
     "zkevm": "ETH",
     "arbitrum": "ETH",
     "polygon": "MATIC",
     "bsc": "BNB",
     "optimism": "ETH",
     "avalanche": "AVAX",
     "ethereum": "ETH"
}

chain = StarknetChainId.MAINNET

slippage = SETTINGS["Slippage"]

ACTUAL_IMPL = 0x5dec330eebf36c8672b60db4a718d44762d3ae6d1333e553197acb47ee5a062


out_wallets_result = {
    
}
addr_dict = {}

indexes = []

def req_post(url: str, **kwargs):
    try:
        resp = requests.post(url, **kwargs)
        if resp.status_code == 200:
            return resp.json()
        else:
            logger.error("Bad status code, will try again")
            pass
    except Exception as error:
        logger.error(f"Requests error: {error}")



async def handle_dangerous_request(func, message, address = "", *args):
    while True:
        try:
            return await func(*args)
        except Exception as e:
            pass
            logger.error(f"[{address}] {message}: {e}")
            await sleeping(address, True)

def get_random_value_int(param):
    return random.randint(param[0], param[1])

def get_random_value(param):
    return random.uniform(param[0], param[1])

def import_argent_account(private_key: int, client):
    if SETTINGS["useAdvanced"]:
        key_pair = KeyPair.from_private_key(private_key)
        salt = key_pair.public_key
        if SETTINGS["Provider"].lower() == "argent" or SETTINGS["Provider"].lower() == "argent_newest":
            account_initialize_call_data = [key_pair.public_key, 0]
        elif SETTINGS["Provider"].lower() == "braavos" or SETTINGS["Provider"].lower() == "braavos_newest":
            account_initialize_call_data = [key_pair.public_key]
        else:
            logger.error(f"Selected unsupported wallet provider: {SETTINGS['Provider'].lower()}. Please select one of this: argent, braavos")
            return
        class_hash = int(SETTINGS["class_hash"], 16)
        call_data = [
                int(SETTINGS["implementation"], 16),
                int(SETTINGS["selector"], 16),
                len(account_initialize_call_data),
                *account_initialize_call_data
            ]
    else:
        if SETTINGS["Provider"].lower() == "argent":
            class_hash = 0x025ec026985a3bf9d0cc1fe17326b245dfdc3ff89b8fde106542a3ea56c5a918

            key_pair = KeyPair.from_private_key(private_key)
            salt = key_pair.public_key


            account_initialize_call_data = [key_pair.public_key, 0]

            call_data = [
                0x33434ad846cdd5f23eb73ff09fe6fddd568284a0fb7d1be20ee482f044dabe2,
                0x79dc0da7c54b95f10aa182ad0a46400db63156920adb65eca2654c0945a463,
                len(account_initialize_call_data),
                *account_initialize_call_data
            ]
        elif SETTINGS["Provider"].lower() == "argent_newest":
            class_hash = 0x01a736d6ed154502257f02b1ccdf4d9d1089f80811cd6acad48e6b6a9d1f2003

            key_pair = KeyPair.from_private_key(private_key)
            salt = key_pair.public_key


            account_initialize_call_data = [key_pair.public_key, 0]

            call_data = [
                *account_initialize_call_data
            ]
        elif SETTINGS["Provider"].lower() == "braavos":
            class_hash = 0x03131fa018d520a037686ce3efddeab8f28895662f019ca3ca18a626650f7d1e
            key_pair = KeyPair.from_private_key(private_key)
            salt = key_pair.public_key
            account_initialize_call_data = [key_pair.public_key]

            call_data = [
                0x5aa23d5bb71ddaa783da7ea79d405315bafa7cf0387a74f4593578c3e9e6570,
                0x2dd76e7ad84dbed81c314ffe5e7a7cacfb8f4836f01af4e913f275f89a3de1a,
                len(account_initialize_call_data),
                *account_initialize_call_data
            ]
        elif SETTINGS["Provider"].lower() == "braavos_newest":
            class_hash = 0x03131fa018d520a037686ce3efddeab8f28895662f019ca3ca18a626650f7d1e
            key_pair = KeyPair.from_private_key(private_key)
            salt = key_pair.public_key
            account_initialize_call_data = [key_pair.public_key]

            call_data = [
                0x5aa23d5bb71ddaa783da7ea79d405315bafa7cf0387a74f4593578c3e9e6570,
                0x2dd76e7ad84dbed81c314ffe5e7a7cacfb8f4836f01af4e913f275f89a3de1a,
                len(account_initialize_call_data),
                *account_initialize_call_data
            ]
        elif SETTINGS["Provider"].lower() == "argent_old":
            class_hash = 0x025ec026985a3bf9d0cc1fe17326b245dfdc3ff89b8fde106542a3ea56c5a918
            key_pair = KeyPair.from_private_key(private_key)
            salt = key_pair.public_key
            account_initialize_call_data = [key_pair.public_key]

            call_data = [
                0x1a7820094feaf82d53f53f214b81292d717e7bb9a92bb2488092cd306f3993f,
                0x79dc0da7c54b95f10aa182ad0a46400db63156920adb65eca2654c0945a463,
                len(account_initialize_call_data),
                *account_initialize_call_data
            ]
        else:
            logger.error(f"Selected unsupported wallet provider: {SETTINGS['Provider'].lower()}. Please select one of this: argent, braavos")
            return
    address = compute_address(
        salt=salt,
        class_hash=class_hash,  
        constructor_calldata=call_data,
        deployer_address=0,
    )
    

    account = StarkNativeAccount(
            address=address, client=client, key_pair=key_pair, chain=chain
        )

    return account, call_data, salt, class_hash


def sleeping_sync(address, error = False):
    if error:
        rand_time = random.randint(SETTINGS["ErrorSleepeng"][0], SETTINGS["ErrorSleepeng"][1])
    else:
        rand_time = random.randint(SETTINGS["TaskSleep"][0], SETTINGS["TaskSleep"][1])
    logger.info(f'[{address}] sleeping {rand_time} s')
    time.sleep(rand_time)

starkstats = "address;txn count;ETH balance;USDC balance;USDT balance;myswap wstETH;myswap USDC; myswap USDT;jediswap USDC;jediswap USDT;sithswap USDC;sithswap USDT;10kswap USDC;10kswap USDT;avnu USDC;avnu USDT\n"

from loguru import logger as console_log

global_log = {}
indexes = []
SETTINGS["retries_limit"] = SETTINGS["RetriesLimit"]
def write_global_log():
    log = ""
    for key in global_log:
        buff = f"{key}:\n"
        for data in global_log[key]:
            buff += f"{data}\n"
        log += buff + "\n"
    with open(f"{SETTINGS_PATH}log.txt", "w") as f:
        f.write(log)

class logger():
    @staticmethod
    def info(message: str):
        try:
            addr = message.split("]")[0][1::]
            console_log.info(f"[{addr}] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}")
            if addr not in list(global_log.keys()):
                global_log[addr] = [f"[INFO] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}"]
            else:
                global_log[addr].append(f"[INFO] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}")
            write_global_log()
        except:
            pass
    
    @staticmethod
    def error(message: str):
        try:
            addr = message.split("]")[0][1::]
            console_log.error(f"[{addr}] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}")
            if addr not in list(global_log.keys()):
                global_log[addr] = [f"[ERROR] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}"]
            else:
                global_log[addr].append(f"[ERROR] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}")

            write_global_log()
        except:
            pass
    
    @staticmethod
    def success(message: str):
        try:
            addr = message.split("]")[0][1::]
            console_log.success(f"[{addr}] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}")
            if addr not in list(global_log.keys()):
                global_log[addr] = [f"[SUCCESS] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}"]
            else:
                global_log[addr].append(f"[SUCCESS] [{indexes.index(addr)+1}/{len(indexes)}] {message.split(']')[1]}")

            write_global_log()
        except:
            pass

async def sleeping(address, error = False):
        if error:
            rand_time = random.randint(SETTINGS["ErrorSleepeng"][0], SETTINGS["ErrorSleepeng"][1])
        else:
            rand_time = random.randint(SETTINGS["TaskSleep"][0], SETTINGS["TaskSleep"][1])
        logger.info(f'[{address}] sleeping {rand_time} s')
        await asyncio.sleep(rand_time)