from starknet_py.hash import transaction 
from starknet_py.hash.address import compute_address
from starknet_py.net.account.account import Account
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.networks import MAINNET
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.contract import Contract, PreparedFunctionCall
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
from loguru import logger
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

client = GatewayClient(net=MAINNET)
chain = StarknetChainId.MAINNET
import sys, os


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

NOT_ENOUGH_NATIVE = -1
DEPLOY_ERROR = -2
MAX_RETRIES_LIMIT_REACHED = -3
INVALID_DECIMALS = -4
CAIRO_ERROR = -5
LAYERSWAP_BAD_DATA = -6
VALUE_TOO_LOW = -7
WRONG_CHOICE = -8
UNEXPECTED_ERROR = -9999
SUCCESS = 1
CONTRACT_ADDRESS_PREFIX = str_to_felt('STARKNET_CONTRACT_ADDRESS')
UNIVERSAL_DEPLOYER_PREFIX = str_to_felt('UniversalDeployerContract')
JEDISWAP_CONTRACT = 0x041fd22b238fa21cfcf5dd45a8548974d8263b3a531a60388411c5e230f97023
ETH_TOKEN_CONTRACT = 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7
USDT_TOKEN_CONTRACT = 0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8
USDC_TOKEN_CONTRACT = 0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8
MYSWAP_CONTRACT = 0x10884171baf1914edc28d7afb619b40a4051cfae78a094a55d230f19e944a28
TEN_K_SWAP_CONTRACT = 0x07a6f98c03379b9513ca84cca1373ff452a7462a3b61598f0af5bb27ad7f76d1
SITHSWAP_CONTRACT = 0x028c858a586fa12123a1ccb337a0a3b369281f91ea00544d0c086524b759f627
ORBITER_STARK_CONTRACT = 0x0173f81c529191726c6e7287e24626fe24760ac44dae2a1f7e02080230f8458b
ANVU_CONTRACT = 0x4270219d365d6b017231b52e92b3fb5d7c8378b05e9abc97724537a80e93b0f
wstETH_TOKEN_CONTRACT = 0x042b8f0484674ca266ac5d08e4ac6a3fe65bd3129795def2dca5c34ecc5f96d2

LIQ_PRICES = {
    "my" : 8136191259,
    "jedi": 9529583074,
    "10k": 8415876230,
    "sith": 80141
}

SUPPORTED_FOR_SWAPS = [
    "jedi",
    "my",
    "10k",
    "sith",
    "anvu"
]

SUPPORTED_FOR_LIQ = [
    "jedi",
    "my",
    "10k"
]

ROUTE_FOR_ANVU = {
    USDT_TOKEN_CONTRACT: JEDISWAP_CONTRACT,
    USDC_TOKEN_CONTRACT: TEN_K_SWAP_CONTRACT
}

LIQ_CONTRACTS = {
    "my":{
        USDC_TOKEN_CONTRACT : 0x022b05f9396d2c48183f6deaf138a57522bcc8b35b67dee919f76403d1783136,
        USDT_TOKEN_CONTRACT : 0x041f9a1e9a4d924273f5a5c0c138d52d66d2e6a8bee17412c6b0f48fe059ae04
    },
    "jedi":{
        USDC_TOKEN_CONTRACT : 0x04d0390b777b424e43839cd1e744799f3de6c176c7e32c1812a41dbd9c19db6a,
        USDT_TOKEN_CONTRACT : 0x045e7131d776dddc137e30bdd490b431c7144677e97bf9369f629ed8d3fb7dd6
    },
    "10k":{
        USDC_TOKEN_CONTRACT : 0x000023c72abdf49dffc85ae3ede714f2168ad384cc67d08524732acea90df325,
        USDT_TOKEN_CONTRACT : 0x05900cfa2b50d53b097cb305d54e249e31f24f881885aae5639b0cd6af4ed298
    },
    "sith":{
        USDC_TOKEN_CONTRACT : 0x030615bec9c1506bfac97d9dbd3c546307987d467a7f95d5533c2e861eb81f3f,
        USDT_TOKEN_CONTRACT : 0x00691fa7f66d63dc8c89ff4e77732fff5133f282e7dbd41813273692cc595516
    }
}

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


TOKENS = {
    "USDT": USDT_TOKEN_CONTRACT,
    "USDC": USDC_TOKEN_CONTRACT,
    "ETH": ETH_TOKEN_CONTRACT,
    "wstETH": wstETH_TOKEN_CONTRACT
}

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

MYSWAP_POOLS = {    
    f"{ETH_TOKEN_CONTRACT}:{USDT_TOKEN_CONTRACT}": 4,
    f"{ETH_TOKEN_CONTRACT}:{USDC_TOKEN_CONTRACT}": 1,
    f"{USDT_TOKEN_CONTRACT}:{ETH_TOKEN_CONTRACT}": 4,
    f"{USDC_TOKEN_CONTRACT}:{ETH_TOKEN_CONTRACT}": 1,
    f"{ETH_TOKEN_CONTRACT}:{wstETH_TOKEN_CONTRACT}": 7,
    f"{wstETH_TOKEN_CONTRACT}:{ETH_TOKEN_CONTRACT}": 7,
}
DECIMALS = {
    ETH_TOKEN_CONTRACT: 18,
    wstETH_TOKEN_CONTRACT: 18,
    USDC_TOKEN_CONTRACT: 6,
    USDT_TOKEN_CONTRACT: 6,
    LIQ_CONTRACTS["jedi"][USDC_TOKEN_CONTRACT]: 18,
    LIQ_CONTRACTS["jedi"][USDT_TOKEN_CONTRACT]: 18,
    LIQ_CONTRACTS["my"][USDC_TOKEN_CONTRACT]: 12,
    LIQ_CONTRACTS["my"][USDT_TOKEN_CONTRACT]: 12,
    LIQ_CONTRACTS["10k"][USDC_TOKEN_CONTRACT]: 18,
    LIQ_CONTRACTS["10k"][USDT_TOKEN_CONTRACT]: 18,
    LIQ_CONTRACTS["sith"][USDC_TOKEN_CONTRACT]: 18,
    LIQ_CONTRACTS["sith"][USDT_TOKEN_CONTRACT]: 18,
}

MASK_250 = 2**250 - 1

f = open(f"{SETTINGS_PATH}abi/ETH_stark_abi.json", "r")
ETH_STARK_ABI = json.loads(f.read())
f.close()
f = open(f"{SETTINGS_PATH}abi/jediswap.json", "r")
JEDISWAP_ABI = json.loads(f.read())
f.close()
f = open(f"{SETTINGS_PATH}abi/USDT_abi.json", "r")
USDT_ABI = json.loads(f.read())
f.close()
f = open(f"{SETTINGS_PATH}abi/USDC_abi.json", "r")
USDC_ABI = json.loads(f.read())
f.close()
f = open(f"{SETTINGS_PATH}abi/myswap.json", "r")
MYSWAP_ABI = json.loads(f.read())
f.close()
f = open(f"{SETTINGS_PATH}abi/10kswap.json", "r")
TEN_K_SWAP_ABI = json.loads(f.read())
f.close()
f = open(f"{SETTINGS_PATH}abi/sithswap.json", "r")
SITHSWAP_ABI = json.loads(f.read())
f.close()
f = open(f"{SETTINGS_PATH}abi/orbiter.json", "r")
ORBITER_ABI = json.loads(f.read())
f.close()
f = open(f"{SETTINGS_PATH}abi/starkgate.json", "r")
STARKGATE_ABI = json.loads(f.read())
f.close()
f = open(f"{SETTINGS_PATH}abi/orbiter_stark.json", "r")
ORBITER_STARK_ABI = json.loads(f.read())
f.close()
f = open(f"{SETTINGS_PATH}abi/anvu.json", "r")
ANVU_ABI = json.loads(f.read())
f.close()
with open(f"{SETTINGS_PATH}abi\\erc20.json", "r", encoding='utf-8') as file:
    ERC20_ABI = json.load(file)
with open(f"{SETTINGS_PATH}abi\\sushi.json", "r", encoding='utf-8') as file:
    SUSHI = json.load(file)
with open(f"{SETTINGS_PATH}abi\\bridge.json", "r", encoding='utf-8') as file:
    BRIDGE_ABI = json.load(file)
with open(f"{SETTINGS_PATH}abi\\myswap_quest_nft.json", "r", encoding='utf-8') as file:
    MYSWAP_NFT_QUEST_ABI = json.load(file)

ABIs = {
    ETH_TOKEN_CONTRACT: ETH_STARK_ABI,
    USDT_TOKEN_CONTRACT: USDT_ABI,
    USDC_TOKEN_CONTRACT: USDC_ABI,
    wstETH_TOKEN_CONTRACT: ETH_STARK_ABI
}



slippage = SETTINGS["Slippage"]