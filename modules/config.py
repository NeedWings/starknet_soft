from os import getcwd
import json
import os
SETTINGS_PATH = (getcwd() + "/data/").replace("\\", "/")

KEY = "CEy426oSSaOTWDPgtuKxm1nS2uWN_4-L_eyt0dmAr40="

def json_remove_comments(invalid_json: str):
    comment_start = -1
    for char in range(len(invalid_json)):
        if invalid_json[char:char+4] == ", //":
                comment_start = char+1
        
        if invalid_json[char] == "\n" and comment_start != -1:
            invalid_json = invalid_json[0:comment_start] + invalid_json[char:len(invalid_json)]
            return json_remove_comments(invalid_json)
    return invalid_json



try:
    f = open(f"{SETTINGS_PATH}settings.json", "r")
    a = json_remove_comments(f.read())
    SETTINGS = json.loads(a)
    f.close()
except Exception as e:
    input("Error with settings.json")
    exit()



RPC_LIST = SETTINGS["RPC"]

NATIVE_TOKENS_SYMBOLS = {
     "zkevm": "ETH",
     "arbitrum": "ETH",
     "polygon": "MATIC",
     "bsc": "BNB",
     "optimism": "ETH",
     "avalanche": "AVAX",
     "ethereum": "ETH",
     "base": "ETH",
     "scroll":"ETH",
     "zksync": "ETH",
     "linea": "ETH",
}
NATIVE_WRAPPED_CONTRACTS = {
    "arbitrum": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
    "optimism": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
    "ethereum": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "base":     "0x4200000000000000000000000000000000000006",
    "scroll":   "0x5300000000000000000000000000000000000004",
    "zksync":   "0x000000000000000000000000000000000000800A",
    "linea":    "0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f"
}

SLIPPAGE = SETTINGS["Slippage"]
MAX_PRICE_IMPACT = SETTINGS["Max price impact"]

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