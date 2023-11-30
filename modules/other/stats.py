
from modules.base_classes.base_account import BaseAccount
from modules.routers.activity.lending_handler import lends
from modules.routers.activity.liquidity_handler import liq_dexes
from modules.utils.token_storage import eth, usdc, usdt, dai, wbtc, wsteth, lords
from modules.utils.logger import logger
from modules.utils.utils import handle_dangerous_request
from modules.config import SETTINGS_PATH


async def stat(account: BaseAccount):
    eth_balance = (await account.get_balance_starknet(eth))[1]
        
    usdc_balance = (await account.get_balance_starknet(usdc))[1]
        
    usdt_balance = (await account.get_balance_starknet(usdt))[1]
    dai_balance = (await account.get_balance_starknet(dai))[1]
    wbtc_balance = (await account.get_balance_starknet(wbtc))[1]
    wsteth_balance = (await account.get_balance_starknet(wsteth))[1]
    lords_balance = (await account.get_balance_starknet(lords))[1]
        
    have_liq = False
    have_lend = False
    dexes = liq_dexes.copy()
    
    for dex in dexes:
        if have_liq:
            break
        for lpt in dex.lpts:
            if have_liq:
                break
            bal = (await account.get_balance_starknet(lpt))[0]
            if bal >= 1:
                have_liq = True
    
    for dex in lends:
        if have_lend:
            break
        for lpt in dex.lend_tokens:
            if have_lend:
                break
            bal = (await account.get_balance_starknet(lpt))[0]
            if bal >= 1:
                have_lend = True

    if have_lend:
        have_lend = "Yes"
    else:
        have_lend = "No"
    if have_liq:
        have_liq = "Yes"
    else:
        have_liq = "No"

    txn_count = await handle_dangerous_request(account.stark_native_account.get_nonce, "Can't get nonce, error", account.stark_address)
        
    with open(f"{SETTINGS_PATH}starkstats.csv", "r") as f:
        starkstats = f.read()
    data = f"{account.stark_address};{txn_count};{eth_balance};{usdc_balance};{usdt_balance};{dai_balance};{wbtc_balance};{wsteth_balance};{lords_balance};{have_liq};{have_lend}\n"
    starkstats += data.replace(".",",")
    with open(f"{SETTINGS_PATH}starkstats.csv", "w") as f:
        f.write(starkstats)
    logger.info(f"[{account.stark_address}] data:\ntxn count: {txn_count}\nETH: {eth_balance}\nUSDC: {usdc_balance}\nUSDT: {usdt_balance}\nDAI: {dai_balance}\nWBTC: {wbtc_balance}\nWSTETH: {wsteth_balance}\nLORDS: {lords_balance}\nHave lend: {have_lend}\nHave liq: {have_liq}\n")

