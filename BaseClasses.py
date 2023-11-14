from abc import ABC, abstractmethod
from .cfg import *
from starknet_py.net.account.account import _add_max_fee_to_transaction, _add_signature_to_transaction, _parse_calls_v2, _execute_payload_serializer_v2, _merge_calls, _execute_payload_serializer

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



class EVMTransactionDataHandler():
    
    def __init__(self, address, net_name) -> None:
        self.address = address
        self.net_name = net_name
        self.w3 = Web3(Web3.HTTPProvider(random.choice(RPC_OTHER[net_name])))
    
    def get_gas_price(self):
        
        max_gas = Web3.to_wei(SETTINGS.get("GWEI").get(self.net_name), 'gwei')

        while True:
            try:
                gas_price = self.w3.eth.gas_price
                if gas_price > max_gas:
                    h_gas, h_max = Web3.from_wei(gas_price, 'gwei'), Web3.from_wei(max_gas, 'gwei')
                    logger.error(f'[{self.address}] Sender net: {self.net_name}. Current gasPrice: {h_gas} | Max gas price: {h_max}')
                    sleeping_sync(f'[{self.address}] Waiting best gwei. Update after ')
                else:
                    return round(gas_price)
                
            except Exception as error:
                logger.error(f'[{self.address}] Error: {error}')
                sleeping_sync(f'[{self.address}] Error fault. Update after ')


    def get_txn_data(self, value=0):
        gas_price = self.get_gas_price()


        data = {
            'chainId': self.w3.eth.chain_id, 
            'nonce': self.w3.eth.get_transaction_count(self.address),  
            'from': self.address, 
            "value": value
        }


        if self.net_name in ["avalanche", "polygon", "arbitrum", "ethereum"]:
            data["type"] = "0x2"


        if self.net_name not in ['arbitrum', "avalanche", "polygon", "ethereum"]:
            data["gasPrice"] = gas_price
            
        else:
            data["maxFeePerGas"] = gas_price
            if self.net_name == "polygon":
                data["maxPriorityFeePerGas"] = Web3.to_wei(30, "gwei")
            elif self.net_name == "avalanche":
                data["maxPriorityFeePerGas"] = gas_price
            elif self.net_name == "ethereum":
                data["maxPriorityFeePerGas"] = Web3.to_wei(0.05, "gwei")
            elif self.net_name == "arbitrum":
                data["maxPriorityFeePerGas"] = Web3.to_wei(0.01, "gwei")
        return data

class EVMToken():
    def __init__(self, symbol, contract_address, decimals, net) -> None:
        self.net_name = net
        self.w3 = Web3(Web3.HTTPProvider(random.choice(RPC_OTHER[net])))
        self.decimals = decimals
        self.symbol = symbol
        self.contract_address = contract_address
        self.contract = self.w3.eth.contract(contract_address, abi=ERC20_ABI)

    def get_balance(self, address, of_wrapped = False):
        balance = self.contract.functions.balanceOf(address).call()
        human_balance = balance/10**self.decimals
        return balance, human_balance

    def get_approve_txn(self, address, spender, amount):
        txn_data_handler = EVMTransactionDataHandler(address, self.net_name)
        txn = self.contract.functions.approve(spender, amount).build_transaction(
                            txn_data_handler.get_txn_data()
                        )
        return txn
    
    def get_price(self):
        if self.symbol in ["USDC", "USDT"]:
            return 1
        else:
            def __find__(ticker: str, rates: list):
                for k in rates:
                    name = k.get("symbol")
                    if name == ticker.upper() + 'USDT':
                        return float(k.get("price"))
            while True:
                response = req("https://api.binance.com/api/v3/ticker/price")
                if type(response) is list:
                    return __find__(self.symbol, response)
                else:
                    print(f'Cant get response from binance, tring again...')
                    time.sleep(5)

    def get_usd_value(self, amount):
        return self.get_price()*amount
        
            

class EVMNativeToken(EVMToken):
    def __init__(self, net) -> None:
        self.net_name = net
        self.w3 = Web3(Web3.HTTPProvider(random.choice(RPC_OTHER[net])))
        self.decimals = 18
        self.symbol = NATIVE_TOKENS_SYMBOLS[net]
        self.contract = self.w3.eth.contract(self.contract_address, abi=ERC20_ABI)

    def get_balance(self, address, of_wrapped = False):
        if of_wrapped:
            balance = self.contract.functions.balanceOf(address).call()
        else:
            balance = self.w3.eth.get_balance(address)
        human_balance = balance/10**self.decimals
        return balance, human_balance

    def get_approve_txn(self, address, spender, amount):
        return None


class BaseAccount(ABC):

    @abstractmethod
    def send_txn(self, txn):
        """sends transaction"""
        pass
    
    @abstractmethod
    def get_address(self):
        "returns address"
        pass

class BaseStarkAccount(ABC):
    stark_native_account: StarkNativeAccount = None
    formatted_hex_address: str = None
    @abstractmethod
    async def send_txn(self, calldata):
        """sends transaction"""
        pass
    
    @abstractmethod
    def get_address(self):
        "returns address"
        pass

    @abstractmethod
    async def get_balance(self, token: int = None, symbol: str = "ETH"):
        pass

class StarkAccount(BaseStarkAccount):

    def __init__(self, stark_native_account: StarkNativeAccount, call_data, salt, class_hash) -> None:
        self.stark_native_account = stark_native_account
        self.call_data = call_data
        self.salt = salt
        self.class_hash = class_hash
        self.formatted_hex_address = "0x" + "0"*(64 - len(hex(stark_native_account.address)[2::])) + hex(stark_native_account.address)[2::]
        self.client = stark_native_account.client
        self.address = self.stark_native_account.address

    def get_address(self):
        return self.formatted_hex_address
    
    async def get_balance(self, token: int = None, symbol: str = "ETH"):
        return await handle_dangerous_request(self.stark_native_account.get_balance, f"can't get balance of {symbol}. Error", self.formatted_hex_address, token)

    async def wait_for_better_eth_gwei(self, silent = False):
        w3 = Web3(Web3.HTTPProvider(random.choice(RPC_OTHER["ETHEREUM_MAINNET"])))
        address = self.formatted_hex_address
        while True:
            try:
                f = open(f"{SETTINGS_PATH}settings.json", "r")
                a = json_remove_comments(f.read())
                SETTINGS = json.loads(a)
                f.close()
            except Exception as e:
                input("Error with settings.json")
                exit()
            limit = Web3.to_wei(SETTINGS["MaxETHGwei"], "gwei")
            try:
                if SETTINGS["UseStarknetGwei"]:
                    client = GatewayClient(MAINNET)
                    price = (await client.get_block()).gas_price
                else:
                    price = w3.eth.gas_price
            except:
                if not silent:
                    logger.error(f"[{address}] can't get gas price. will try later")
                    await sleeping(address, True)
                else:
                    await asyncio.sleep(get_random_value(SETTINGS["ErrorSleepeng"]))
                continue
            if price < limit:
                break
            if not silent:
                logger.info(f"[{address}] Current gas price is {Web3.from_wei(price, 'gwei')}, which is more, than max in settings({SETTINGS['MaxETHGwei']}). Will wait for better fees")
                await asyncio.sleep(get_random_value(SETTINGS["WaitGWEISleep"]))
            else:
                await asyncio.sleep(get_random_value(SETTINGS["WaitGWEISleep"]))

            
    async def send_txn(self, calldata):
        await self.wait_for_better_eth_gwei()
        i = 0
        while SETTINGS["RetriesLimit"] > i:
            resp = await self.get_invocation(calldata)
            if resp == -3:
                logger.error(f"[{self.formatted_hex_address}] max retries limit reached")
                return -3, ""
            try:
                logger.success(f"[{self.formatted_hex_address}] sending txn with hash: {hex(resp.transaction_hash)}")
                await self.stark_native_account.client.wait_for_tx(resp.transaction_hash)
                logger.success(f"[{self.formatted_hex_address}] tnx has sent! Hash: {hex(resp.transaction_hash)}")
                return 1, hex(resp.transaction_hash)
            except Exception as e:
                logger.error(f"[{self.formatted_hex_address}]  got error while sending txn: {hex(resp.transaction_hash)}. Error: {e}")
                await sleeping(self.formatted_hex_address, True)
            i +=1
        logger.error(f"[{self.formatted_hex_address}] max retries limit reached")
        return -1, ""

    async def get_invocation(self, calls):
        i = 0
        while i <= SETTINGS["RetriesLimit"]:
            i+=1
            try:
                if SETTINGS["cairo_version"] == 1:
                    nonce = await handle_dangerous_request(self.stark_native_account.get_nonce, "can't get nonce. Error", self.formatted_hex_address)
                    calldata = _parse_calls_v2(ensure_iterable(calls))
                    wrapped_calldata = _execute_payload_serializer_v2.serialize(
                        {"calls": calldata}
                    )

                    transaction = Invoke(
                        calldata=wrapped_calldata,
                        signature=[],
                        max_fee=0,
                        version=1,
                        nonce=nonce,
                        sender_address=self.stark_native_account.address,
                    )
                    max_fee = await self.stark_native_account._get_max_fee(transaction, auto_estimate=True)/1e18
                    if max_fee > SETTINGS["MaxFee"]:
                        logger.error(f"[{self.formatted_hex_address}] counted fee for txn is {max_fee}, which is more than in settings ({SETTINGS['MaxFee']}). Trying again")
                        await sleeping(self.formatted_hex_address, True)
                        continue
                    invocation = await self.stark_native_account.execute(calls=calls, auto_estimate=True, cairo_version=1)
                else:
                    nonce = await handle_dangerous_request(self.stark_native_account.get_nonce, "can't get nonce. Error", self.formatted_hex_address)
                    call_descriptions, calldata = _merge_calls(ensure_iterable(calls))
                    wrapped_calldata = _execute_payload_serializer.serialize(
                        {"call_array": call_descriptions, "calldata": calldata}
                    )

                    transaction = Invoke(
                        calldata=wrapped_calldata,
                        signature=[],
                        max_fee=0,
                        version=1,
                        nonce=nonce,
                        sender_address=self.stark_native_account.address,
                    )
                    max_fee = await self.stark_native_account._get_max_fee(transaction, auto_estimate=True)/1e18
                    if max_fee > SETTINGS["MaxFee"]:
                        logger.error(f"[{self.formatted_hex_address}] counted fee for txn is {max_fee}, which is more than in settings ({SETTINGS['MaxFee']}). Trying again")
                        await sleeping(self.formatted_hex_address, True)
                        continue
                    invocation = await self.stark_native_account.execute(calls=calls, auto_estimate=True, cairo_version=0)
                return invocation
            except Exception as e:
                logger.error(f"[{self.formatted_hex_address}] can't create transaction. Error:{e}")
                await sleeping(self.formatted_hex_address, True)
        return -3


class Token():
    def __init__(self, symbol: str, contract_address: int, decimals, stable = False) -> None:
        self.decimals = decimals
        self.symbol: str = symbol
        self.contract_address = contract_address
        self.stable = stable

    def get_approve_call(self, amount: float, spender: int, sender: BaseStarkAccount):
        contract = Contract(self.contract_address, STARK_TOKEN_ABI, sender.stark_native_account)
        decimals = self.decimals
        call = contract.functions["approve"].prepare(
            spender, int(amount*10**decimals)
        )
        return call
    
    def get_approve_call_wei(self, amount: int, spender: int, sender: BaseStarkAccount):
        contract = Contract(self.contract_address, STARK_TOKEN_ABI, sender.stark_native_account)
        decimals = self.decimals

        call = contract.functions["approve"].prepare(
            spender, amount
        )
        return call
    
    def get_price(self):
        if self.stable:
            return 1
        elif self.symbol == "LORDS":
            def __find__(ticker: str, rates: list):
                for k in rates:
                    name = k.get("symbol")
                    if name == ticker.upper() + 'USDT':
                        return float(k.get("price"))
            while True:
                response = req("https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd&ids=lords")
                if type(response) is dict:
                    return response["lords"]["usd"]
                else:
                    print(f'Cant get response from coingecko for lords, tring again...')
                    time.sleep(5)
        elif self.symbol == "WSTETH":
            def __find__(ticker: str, rates: list):
                for k in rates:
                    name = k.get("symbol")
                    if name == ticker.upper() + 'USDT':
                        return float(k.get("price"))
            while True:
                response = req("https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd&ids=wrapped-steth")
                if type(response) is dict:
                    return response["wrapped-steth"]["usd"]
                else:
                    print(f'Cant get response from coingecko for wrapped-steth, tring again...')
                    time.sleep(5)
        elif self.symbol == "ETH":
            def __find__(ticker: str, rates: list):
                for k in rates:
                    name = k.get("symbol")
                    if name == ticker.upper() + 'USDT':
                        return float(k.get("price"))
            while True:
                response = req(f'https://api.etherscan.io/api?module=stats&action=ethprice&apikey={SETTINGS["etherscanKey"]}')
                if type(response) is dict:
                    return float(response['result']['ethusd'])
                else:
                    print(f'Cant get response from etherscan for {self.symbol}, tring again...')
                    time.sleep(5)
        else:
            def __find__(ticker: str, rates: list):
                for k in rates:
                    name = k.get("symbol")
                    if name == ticker.upper() + 'USDT':
                        return float(k.get("price"))
            while True:
                response = req("https://api.binance.com/api/v3/ticker/price")
                if type(response) is list:
                    return __find__(self.symbol, response)
                else:
                    print(f'Cant get response from binance for {self.symbol}, tring again...')
                    time.sleep(5)

    def get_usd_value(self, amount):
        return self.get_price()*amount

class LPToken(Token):
    def __init__(self, symbol, contract_address: int, decimals) -> None:
        self.decimals = decimals
        self.symbol = symbol
        self.contract_address = contract_address
        
    def transform_amounts(self, token1, amount1, token2, amount2):
        order = self.symbol.split("-")

        token1_correct = order[0]

        if token1 == token1_correct:
            return (amount1, amount2)
        else:
            return (amount2, amount1)

class BaseDex(ABC):
    name = None
    supported_tokens = []
    lpts = []
    contract_address_lp = None
    def __init__(self) -> None:
        new_supported_tokens = []
        for token in self.supported_tokens:
            if token in SETTINGS["Supported_tokens"]:
                new_supported_tokens.append(token)
        self.supported_tokens = new_supported_tokens

    @abstractmethod
    async def create_txn_for_swap(self, amount_in: float, token1: Token, amount_out: float, token2: Token, sender: BaseStarkAccount, full: bool = False):
        pass

    @abstractmethod
    async def create_txn_for_liq(self, amount1: float, token1: Token, amount2: float, token2: Token, sender: BaseStarkAccount):
        pass

    @abstractmethod
    async def create_txn_for_remove_liq(self, lptoken: Token, sender: BaseStarkAccount):
        pass

    def get_pair_for_token(self, token: str):
        for i in range(20):
            pair = random.choice(self.supported_tokens)
            if token != pair:
                return pair
        logger.error("Can't find pair for token")
        return -5
    
class BaseLend(ABC):
    contract_address = None
    name = None
    supported_tokens = []
    lend_tokens = []
    @abstractmethod
    async def create_txn_for_adding_token(self, token: Token, amount: float, sender: BaseStarkAccount):
        pass

    @abstractmethod
    async def create_txn_for_removing_token(self, amount: int, token: Token, sender: BaseStarkAccount):
        pass

    @abstractmethod
    async def create_txn_for_borrow(self, amount: float, token: Token, sender: BaseStarkAccount):
        pass
    
    @abstractmethod
    async def create_txn_for_return(self, token: Token, sender: BaseStarkAccount):
        pass
