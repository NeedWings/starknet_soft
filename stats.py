from BaseClasses import *

eth = Token("ETH", 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 18)
usdc = Token("USDC", 0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8, 6, stable=True)
usdt = Token("USDT", 0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8, 6, stable=True)
dai = Token("DAI", 0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3, 18, stable=True)
wbtc = Token("WBTC", 0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac, 8)
wsteth = Token("WSTETH", 0x042b8f0484674ca266ac5d08e4ac6a3fe65bd3129795def2dca5c34ecc5f96d2, 18)
lords = Token("LORDS", 0x0124aeb495b947201f5fac96fd1138e326ad86195b98df6dec9009158a533b49, 18)



async def stat(self):
    eth_balance = await self.account.get_balance()/1e18
        
    usdc_balance = await self.account.get_balance(usdc.contract_address, usdc.symbol)/1e6
        
    usdt_balance = await self.account.get_balance(usdt.contract_address, usdc.symbol)/1e6
    dai_balance = await self.account.get_balance(dai.contract_address, dai.symbol)/10**dai.decimals
    wbtc_balance = await self.account.get_balance(wbtc.contract_address, wbtc.symbol)/10**wbtc.decimals
    wsteth_balance = await self.account.get_balance(wsteth.contract_address, wsteth.symbol)/10**wsteth.decimals
    lords_balance = await self.account.get_balance(lords.contract_address, usdc.symbol)/10**lords.decimals
        


    txn_count = await handle_dangerous_request(self.account.stark_native_account.get_nonce, "Can't get nonce, error", self.account.formatted_hex_address)
        
    with open(f"{SETTINGS_PATH}starkstats.csv", "r") as f:
        starkstats = f.read()
    data = f"{self.account.formatted_hex_address};{txn_count};{eth_balance};{usdc_balance};{usdt_balance};{dai_balance};{wbtc_balance};{wsteth_balance};{lords_balance}\n"
    starkstats += data.replace(".",",")
    with open(f"{SETTINGS_PATH}starkstats.csv", "w") as f:
        f.write(starkstats)
    logger.info(f"[{self.account.formatted_hex_address}] data:\ntxn count: {txn_count}\nETH: {eth_balance}\nUSDC: {usdc_balance}\nUSDT: {usdt_balance}\nDAI: {dai_balance}\nWBTC: {wbtc_balance}\nWSTETH: {wsteth_balance}\nLORDS: {lords_balance}")

