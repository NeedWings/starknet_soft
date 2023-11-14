from .cfg import *

ORBITER_ABI = [{"inputs":[{"internalType":"address payable","name":"_to","type":"address"},{"internalType":"bytes","name":"_ext","type":"bytes"}],"name":"transfer","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"bytes","name":"_ext","type":"bytes"}],"name":"transferERC20","outputs":[],"stateMutability":"nonpayable","type":"function"}]

def req(url: str, **kwargs):
    try:
        resp = requests.get(url, **kwargs)
        if resp.status_code == 200:
            return resp.json()
        else:
            logger.error("Bad status code, will try again")
            pass
    except Exception as error:
        logger.error(f"Requests error: {error}")


def get_ticker_price(ticker) -> float:
    def __find__(ticker: str, rates: list):
        for k in rates:
            name = k.get("symbol")
            if name == ticker.upper() + 'USDT':
                return float(k.get("price"))
    while True:
        response = req("https://api.binance.com/api/v3/ticker/price")
        if type(response) is list:
            return __find__(ticker, response)
        else:
            print(f'Cant get response from binance, tring again...')
            time.sleep(5)


def get_eth_price():
    return get_ticker_price('eth')

async def get_native_balance_evm(net_name: str, address: str):
        while True:
            try:
                web3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP[net_name])))
                balance = web3.eth.get_balance(address)

                return balance
            except Exception as error:
                logger.error(f'[{address}] Cant get balance of native: {net_name}! Error: {error}')
                await sleeping(address, True)

async def get_gas_price_evm(address: str, net_name: str):
    w3 = Web3(Web3.HTTPProvider(random.choice(RPC_OTHER[net_name])))
    max_gas = Web3.to_wei(SETTINGS.get("GWEI").get(net_name), 'gwei')

    while True:
        try:
            gas_price = w3.eth.gas_price
            if gas_price > max_gas:
                h_gas, h_max = Web3.from_wei(gas_price, 'gwei'), Web3.from_wei(max_gas, 'gwei')
                logger.error(f'[{address}] Sender net: {net_name}. Current gasPrice: {h_gas} | Max gas price: {h_max}')
                await sleeping(f'[{address}] Waiting best gwei. Update after ')
            else:
                return round(gas_price)
            
        except Exception as error:
            logger.error(f'[{address}] Error: {error}')
            await sleeping(f'[{address}] Error fault. Update after ')


async def get_tx_data_evm(address, w3: Web3, net_name: str, value=0) -> dict:

        gas_price = await get_gas_price_evm(address, net_name)


        data = {
            'chainId': w3.eth.chain_id, 
            'nonce': w3.eth.get_transaction_count(address),  
            'from': address, 
            "value": value
        }


        if net_name in ["AVALANCHE_MAINNET", "POLYGON_MAINNET", "ARBITRUM_MAINNET", "ETHEREUM_MAINNET"]:
            data["type"] = "0x2"


        if net_name not in ['ARBITRUM_MAINNET', "AVALANCHE_MAINNET", "POLYGON_MAINNET", "ETHEREUM_MAINNET"]:
            data["gasPrice"] = gas_price
            
        else:
            data["maxFeePerGas"] = gas_price
            if net_name == "POLYGON_MAINNET":
                data["maxPriorityFeePerGas"] = Web3.to_wei(30, "gwei")
            elif net_name == "AVALANCHE_MAINNET":
                data["maxPriorityFeePerGas"] = gas_price
            elif net_name == "ETHEREUM_MAINNET":
                data["maxPriorityFeePerGas"] = Web3.to_wei(0.05, "gwei")
            elif net_name == "ARBITRUM_MAINNET":
                data["maxPriorityFeePerGas"] = Web3.to_wei(0.01, "gwei")
        return data

async def check_net_assets(address: str):
    nets = []
    net_dict = {
        "arbitrum": "ARBITRUM_MAINNET",
        "ethereum": "ETHEREUM_MAINNET",
        "optimism": "OPTIMISM_MAINNET"
    }
    for i in SETTINGS["nets_for_deposit"]:
        nets.append(net_dict[i])
    max_valued_net_value = 0
    max_valued_net = nets[0]
    for net in nets:
        eth = await get_native_balance_evm(net, address)
        human = Web3.from_wei(eth, "ether")
        logger.info(f'[{address}] Got {net} balance: {human}')
        if human > max_valued_net_value:
            max_valued_net_value = human
            max_valued_net = net
    
    return float(max_valued_net_value), max_valued_net


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


async def orbiter(amount: float, source: str, private_key: str, recepient: str):
    try:
        if amount < 0.005:
            logger.error(f"[{wallet}] value lower, than minimal amount of bridge(0.005)")
            return -1, ""
        recepient = recepient[2::]
        while len(recepient)<64:
            recepient = "0"+recepient
        recepient = "0x03"+recepient
        rpc = str(random.choice(RPC_FOR_LAYERSWAP[source]))
        web3 = Web3(Web3.HTTPProvider(rpc))
        amount = get_orbiter_value(amount)
        wallet = web3.eth.account.from_key(private_key).address
        balance = await get_native_balance_evm(source, wallet)
        if balance < amount*decimal.Decimal(1e18):
            logger.error(f"[{wallet}] not enough ETH for bridge ")
            return -1, ""
        contract = web3.eth.contract(ORBITER_CONTRACT, abi=ORBITER_ABI)

        dict_transaction = await get_tx_data_evm(wallet, web3, source, int(amount * decimal.Decimal(1e18)))

        txn = contract.functions.transfer(
            ORBITER_CONTRACTS_REC, recepient
        ).build_transaction(dict_transaction)

        signed_txn = web3.eth.account.sign_transaction(txn, private_key)
        txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return 1, Web3.to_hex(txn_hash)
    except Exception as e:
        logger.error(f"[{wallet}] failed to send tx: {source}! Error: {e}")
        await sleeping(wallet, True)
        return -1, ""

async def layerswap(amount: float, source: str, private_key: str, recepient: str):
    try:
        rpc = random.choice(RPC_FOR_LAYERSWAP[source])
        web3 = Web3(Web3.HTTPProvider(rpc))
        wallet = web3.eth.account.from_key(private_key).address

        balance = await get_native_balance_evm(source, wallet)
        if balance < amount*1e18:
            logger.error(f"[{wallet}] not enough ETH for bridge ")
            return -1, ""

        try:
            correlationId = uuid.uuid4()
            r = requests.post('https://identity-api.layerswap.io/connect/token', data={"client_id": "layerswap_bridge_ui", "grant_type":"credentialless"})

            token = r.json()["access_token"]

            r = requests.post("https://bridge-api.layerswap.io//api/swaps", data=json.dumps({
                "amount":amount,
                "source":source,
                "destination":"STARKNET_MAINNET",
                "asset":"ETH",
                "source_address": wallet,
                "destination_address":recepient,
                "refuel":False
                }),
                headers={
                "Accept":"application/json, text/plain, */*",
                "Accept-Language":"ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin":"*",
                "X-Ls-Correlation-Id": str(correlationId),
                "Authorization": f"Bearer {token}",
                "Origin":"https://www.layerswap.io",
                "Referer":"https://www.layerswap.io/",
                "Sec-Ch-Ua":'"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
                "Sec-Ch-Ua-Mobile":"?0",
                "Sec-Ch-Ua-Platform":"Windows",
                "Sec-Fetch-Dest":"empty",
                "Sec-Fetch-Mode":"cors",
                "Sec-Fetch-Site":"same-site",
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            })
            
            r = requests.post("https://bridge-api.layerswap.io//api/deposit_addresses/" + source, headers={
                "Authorization": f"Bearer {token}",
            })


            address = r.json()["data"]["address"]

            if len(address)<42:
                address = "0x"+"0"+address[2::]
            if len(address)<42:
                address = "0x"+"0"+address[2::]
        except Exception as e:
            logger.error(f"[{wallet}] LayerSwap sent bad data")
            return -1, ""


        
        tx = await get_tx_data_evm(wallet, web3, source, Web3.to_wei(amount, 'ether'))
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        
        #send transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        
        return 1, Web3.to_hex(tx_hash)
    except Exception as e:
        logger.error(f"[{wallet}] failed to send tx: {source}! Error: {e}")
        await sleeping(wallet, True)
        return -1, ""
    
async def eth_bridge_no_off(private_key: str, recepient: str, delay: int):
    private_key = "0x" + "0"*(66-len(private_key)) + private_key[2::]

    await asyncio.sleep(delay)
    way = random.choice(SETTINGS["BridgeType"])
    web3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))
    wallet = web3.eth.account.from_key(private_key).address
    i = 0
    while True:
        value, net = await check_net_assets(wallet)
        value = value - get_random_value(SETTINGS["SaveOnWallet"])
        if value >= SETTINGS["MinEthValue"]:
            break
        else:
            logger.error(f"{[wallet]} balance below MinEthValue, keep looking")
            await sleeping(wallet, True)
        if i >= retries_limit:
            logger.error(f"[{wallet}] max retries limit reached, stop searching")
            return
        i+=1
    
    amountUSD = get_random_value(SETTINGS["USDAmountToBridge"])
    ETH_price = get_eth_price()
    
    amount = amountUSD/ETH_price

    if value < amount:
        amount = value
    
    
    if amount < SETTINGS["MinEthValue"] and amount < 0.006:
        logger.error(f"[{wallet}] amount to bridge({amount} ETH) lower than minimum")
    logger.info(f"[{wallet}] going to bridge {amount} ETH in {way} to {recepient}")

    if way == "orbiter":
        res = await orbiter(amount, net, private_key, recepient)
    elif way == "layerswap":
        res = await layerswap(amount, net, private_key, recepient)
    else:
        logger.error(f"[{wallet}] selected unsupported bridge ({way}), please choose one from this (orbiter, layerswap)")
        input("Please restart soft with correct settings")
    
    if res[0] == 1:
        logger.success(f"[{wallet}] txn has sent, hash: {res[1]}")
        await sleeping(wallet)

def start_eth_bridge_no_off(private_key: str, recepient: str, delay: int):
    loop = asyncio.new_event_loop()
    tasks = []
    tasks.append(loop.create_task(eth_bridge_no_off(private_key, recepient, delay)))
    loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))



def get_contract_evm(token_address: str, net_name: str, token=False):
        w3 = Web3(Web3.HTTPProvider(random.choice(RPC_OTHER[net_name])))

        if token:
            abi = token
        else: abi = ERC20_ABI

        contract = w3.eth.contract(token_address, abi=abi)
        return contract, w3

async def get_evm_token_balance(address, token_address=None, net_name=None, contract=False, get_decimals=False):
    while True:
        try:
            if contract == False:
                    contract, w3 = get_contract_evm(token_address, net_name)
            decimals = contract.functions.decimals().call()
            balance = contract.functions.balanceOf(address).call()

            from_wei_balance = balance / 10**decimals
            if get_decimals:

                return balance, from_wei_balance, decimals
            
            return balance, float(from_wei_balance)
        except Exception as error:
            logger.error(f'[{address}] Cant get balance of: {token_address}! Error: {error}')
            await sleeping(address, True)
