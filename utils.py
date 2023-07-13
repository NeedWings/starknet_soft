import random
from cfg import *



async def check_net_assets(address: str):
    nets = ["ARBITRUM_MAINNET", "ETHEREUM_MAINNET", "OPTIMISM_MAINNET"]
    max_valued_net_value = 0
    max_valued_net = "ARBITRUM_MAINNET"
    for net in nets:
        eth = await get_native_balance_evm(net, address)
        human = Web3.from_wei(eth, "ether")
        logger.info(f'Got {net} balance: {human}')
        if human > max_valued_net_value:
            max_valued_net_value = human
            max_valued_net = net


    return float(max_valued_net_value), max_valued_net

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

def get_wsteth_price():
    while True:
        response = req("https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd&ids=wrapped-steth")
        if type(response) is dict:
            return float(response["wrapped-steth"]["usd"])

def get_eth_price():
    return get_ticker_price('eth')

async def sleeping(address, error = False):
        if error:
            rand_time = random.randint(SETTINGS["ErrorSleepeng"][0], SETTINGS["ErrorSleepeng"][1])
        else:
            rand_time = random.randint(SETTINGS["TaskSleep"][0], SETTINGS["TaskSleep"][1])
        logger.info(f'[{address}] sleeping {rand_time} s')
        await asyncio.sleep(rand_time)

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

async def get_native_balance_evm(net_name: str, address: str):
        while True:
            try:
                web3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP[net_name])))
                balance = web3.eth.get_balance(address)

                return balance
            except Exception as error:
                logger.error(f'[{address}] Cant get balance of native: {net_name}! Error: {error}')
                await sleeping(address, True)


def get_random_value_int(param):
    return random.randint(param[0], param[1])

def get_random_value(param):
    return random.uniform(param[0], param[1])

def import_argent_account(private_key: int, client):
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


    address = compute_address(
        salt=salt,
        class_hash=class_hash,  
        constructor_calldata=call_data,
        deployer_address=0,
    )
    

    account = Account(
            address=address, client=client, key_pair=key_pair, chain=chain
        )

    return account, call_data, salt, class_hash


async def execute_function(provider: Account,  calls: list):
    i = 0
    while retries_limit > i:
        resp = await get_invocation(provider, 0, calls, retries_limit)
        if resp == MAX_RETRIES_LIMIT_REACHED:
            logger.error(f"[{hex(provider.address)}] max retries limit reached!")
            return MAX_RETRIES_LIMIT_REACHED
        try:
            logger.success(f"[{hex(provider.address)}] sending transaction with hash: {hex(resp.transaction_hash)}")
            await provider.client.wait_for_tx(resp.transaction_hash)
            logger.success(f"[{hex(provider.address)}] txn has sent! hash of txn: "+hex(resp.transaction_hash))
            return SUCCESS, hex(resp.transaction_hash)
        except Exception as e:
            logger.error(f"[{hex(provider.address)}] got error while sending txn: {hex(resp.transaction_hash)}, trying again")
            await sleeping(hex(provider.address), True)
        i += 1
    logger.error(f"[{hex(provider.address)}] max retries limit reached")
    return CAIRO_ERROR
   


async def get_invocation(provider: Account, i: int, calls, limit: int):

    if i >= limit:
        return MAX_RETRIES_LIMIT_REACHED
    try:
        invocation = await provider.execute(calls=calls, max_fee=int(SETTINGS["MaxFee"] * 1e18))
        return invocation
    except Exception as e:
        i+=1
        logger.error(f"[{hex(provider.address)}] got error while trying to execute a function: {e}")
        logger.info(f"[{hex(provider.address)}] trying again")
        await sleeping(hex(provider.address), True)
        
        return await get_invocation(provider, i, calls, limit)
    
def approve_token_call(amount: float, spender: int, contract: Contract):
    decimals = DECIMALS[contract.address]
    call = contract.functions["approve"].prepare(
        spender, int(amount*10**decimals)
    )
    return call


async def wait_for_better_eth_gwei(address: str):
    w3 = Web3(Web3.HTTPProvider(random.choice(RPC_OTHER["ETHEREUM_MAINNET"])))
    limit = Web3.to_wei(SETTINGS["MaxETHGwei"], "gwei")
    while True:
        try:
            price = w3.eth.gas_price
        except:
            logger.error(f"[{address}] can't get eth gas price. will try later")
            await sleeping(address, True)
            continue
        if price < limit:
            break
        logger.info(f"[{address}] Current gas price in eth is {Web3.from_wei(price, 'gwei')}, which is more, than max in settings({SETTINGS['MaxETHGwei']}). Will wait for better fees")
        await sleeping(address)


