from modules.utils.token import EVMToken, EVMNativeToken, StarkToken


eth = StarkToken("ETH", 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7, 18)
usdc = StarkToken("USDC", 0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8, 6, stable=True)
usdt = StarkToken("USDT", 0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8, 6, stable=True)
dai = StarkToken("DAI", 0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3, 18, stable=True)
wbtc = StarkToken("WBTC", 0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac, 8)
wsteth = StarkToken("WSTETH", 0x042b8f0484674ca266ac5d08e4ac6a3fe65bd3129795def2dca5c34ecc5f96d2, 18)
lords = StarkToken("LORDS", 0x0124aeb495b947201f5fac96fd1138e326ad86195b98df6dec9009158a533b49, 18)

eth_ethereum = EVMNativeToken("ethereum")
weth_bsc = EVMToken("ETH", "0x2170Ed0880ac9A755fd29B2688956BD959F933F8", 18, "bsc")
weth_polygon = EVMToken("ETH", "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619", 18, "polygon")
eth_optimism = EVMNativeToken("optimism")
eth_arbitrum = EVMNativeToken("arbitrum")
eth_zksync = EVMNativeToken("zksync")

usdt_arbitrum = EVMToken("USDT", "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", 6, "arbitrum", stable=True)
usdc_arbitrum = EVMToken("USDC", "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8", 6, "arbitrum", stable=True)


usdt_polygon = EVMToken("USDT", "0xc2132D05D31c914a87C6611C10748AEb04B58e8F", 6, "polygon", stable=True)
usdc_polygon = EVMToken("USDC", "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", 6, "polygon", stable=True)

usdt_bsc = EVMToken("USDT", "0x55d398326f99059fF775485246999027B3197955", 18, "bsc", stable=True)

nets_stables = {
    "arbitrum": [usdt_arbitrum, usdc_arbitrum],
    "polygon": [usdt_polygon, usdc_polygon],
    "bsc": [usdt_bsc]
}

nets_weth = {
    "bsc": weth_bsc,
    "polygon": weth_polygon
}

nets_eth = {
    "arbitrum": eth_arbitrum,
    "optimism": eth_optimism,
    "zksync": eth_zksync,
    "ethereum": eth_ethereum,
}

tokens = [eth, usdc, usdt, dai, wbtc, wsteth, lords]

tokens_dict = {
    "ETH": eth,
    "USDC": usdc,
    "USDT": usdt,
    "DAI": dai,
    "WBTC": wbtc,
    "WSTETH": wsteth,
    "LORDS": lords
}
