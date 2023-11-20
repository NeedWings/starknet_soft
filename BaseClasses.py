from abc import ABC, abstractmethod
from .cfg import *
from .lib.account import _add_max_fee_to_transaction, _add_signature_to_transaction, _parse_calls_v2, _execute_payload_serializer_v2, _merge_calls, _execute_payload_serializer

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
    
    def get_price(self, proxy=None):
        proxies = {'https': proxy, 'http': proxy} if proxy else None
        if self.symbol in ["USDC", "USDT"]:
            return 1
        else:
            def __find__(ticker: str, rates: list):
                for k in rates:
                    name = k.get("symbol")
                    if name == ticker.upper() + 'USDT':
                        return float(k.get("price"))
            while True:
                response = req("https://api.binance.com/api/v3/ticker/price", proxies=proxies)
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
    def __init__(self, stark_key, provider, stark_rpc, proxy=None) -> None:
        self.client = FullNodeClient(stark_rpc, proxy=proxy)
        (
            self.stark_native_account,
            self.call_data,
            self.salt,
            self.class_hash
        ) = import_argent_account(stark_key, self.client, provider)
        self.formatted_hex_address = "0x" + "0"*(64 - len(hex(self.stark_native_account.address)[2::])) + hex(self.stark_native_account.address)[2::]
        self.address = self.stark_native_account.address
        self.provider = provider
        self.proxy = proxy

    def get_address(self):
        return self.formatted_hex_address
    
    async def get_balance(self, token: int = None, symbol: str = "ETH"):
        return await handle_dangerous_request(self.stark_native_account.get_balance, f"can't get balance of {symbol}. Error", self.formatted_hex_address, token)

    async def wait_for_gwei(self, max_gwei=0):
        limit = Web3.to_wei(max_gwei, "gwei")
        client = GatewayClient(MAINNET, proxy=self.proxy)
        while True:
            try:
                price = (await client.get_block()).gas_price
                if price > limit:
                    time.sleep(10)
                    continue
                return True
            except Exception as e:
                print(e)
                time.sleep(10)
                continue

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

    async def send_txn(self, calldata, RetriesLimit=3):
        i = 0
        while RetriesLimit > i:
            resp = await self.get_invocation(calldata)
            if resp == -3:
                logger.error(f"[{self.formatted_hex_address}] max retries limit reached")
                return -3, "max retries limit reached"
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
        return -1, "max retries limit reached"

    async def get_invocation(self, calls, RetriesLimit=3):
        i = 0
        while i <= RetriesLimit:
            i+=1
            try:
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
                invocation = await self.stark_native_account.execute(calls=calls, auto_estimate=True)
                return invocation
            except Exception as e:
                logger.error(f"[{self.formatted_hex_address}] can't create transaction. Error:{e}")
                await sleeping(self.formatted_hex_address, True)
        return -3

    async def deploy(self):
        call_data = self.call_data
        class_hash = self.class_hash
        salt = self.salt
        account = self.stark_native_account
        balance = 0
        while True:
            try:
                nonce = await account.get_nonce()
                if nonce > 0:
                    return 0, 'already deployed'
                else:
                    break
            except Exception as e:
                if "contract not found" in (str(e)).lower():
                    nonce = 0
                    break
                logger.error(f"[{self.formatted_hex_address}] got error while trying to get nonce: {e}")
                await sleeping(self.formatted_hex_address, True)
        while True:
            logger.info(f"[{self.formatted_hex_address}] checking balance.")
            balance = await self.get_balance()
            logger.info(f"[{self.formatted_hex_address}] got balance: {balance/1e18} ETH")
            if balance >= 1e14:
                break
            await sleeping(self.formatted_hex_address)
        match self.provider:
            case "argent":
                deploy = StarkNativeAccount.deploy_account
            case "argent_newest":
                deploy = StarkNativeAccount.deploy_account
            case "braavos_newest":
                deploy = deploy_account_braavos
            case _:
                return -1, 'Provider unknown'
        try:
            account_deployment_result = await deploy(
                address=account.address,
                class_hash=class_hash,
                salt=salt,
                key_pair=account.signer.key_pair,
                client=account.client,
                chain=chain,
                constructor_calldata=call_data,
                auto_estimate=True,
            )
            await account_deployment_result.wait_for_acceptance()
            # From now on, account can be used as usual
            return 0, hex(account_deployment_result.hash)

        except Exception:
            return -1, traceback.format_exc().replace('\n', '\t')

    async def upgrade(self, new_implementation_for_upgrade=None):
        new_impl = int(new_implementation_for_upgrade if new_implementation_for_upgrade else SETTINGS["new_implementation_for_upgrade"], 16)
        match self.provider:
            case "argent" | "argent_newest":
                abi = UPGRADE_ARGENT
                call_args = new_impl, [0]
            case "braavos_newest":
                deploy = BRAAVOS_UPGRADE
                call_args = new_impl
            case _:
                return -1, 'Provider unknown'
        contract = Contract(self.account.stark_native_account.address, abi, self.account.stark_native_account)
        calldata = [contract.functions["upgrade"].prepare(*call_args)]
        status, result_tx = await self.account.send_txn(calldata)
        return status, result_tx
        

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
    
    def get_price(self, proxy=None):
        proxies = {'https': proxy, 'http': proxy} if proxy else None
        if self.stable:
            return 1
        elif self.symbol == "LORDS":
            def __find__(ticker: str, rates: list):
                for k in rates:
                    name = k.get("symbol")
                    if name == ticker.upper() + 'USDT':
                        return float(k.get("price"))
            while True:
                response = req("https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd&ids=lords", proxies=proxies)
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
                response = req("https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd&ids=wrapped-steth", proxies=proxies)
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
                response = req(f'https://api.etherscan.io/api?module=stats&action=ethprice&apikey={SETTINGS["etherscanKey"]}', proxies=proxies)
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
                response = req("https://api.binance.com/api/v3/ticker/price", proxies=proxies)
                if type(response) is list:
                    return __find__(self.symbol, response)
                else:
                    print(f'Cant get response from binance for {self.symbol}, tring again...')
                    time.sleep(5)

    def get_usd_value(self, amount, proxy=None):
        return self.get_price(proxy)*amount

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

    def get_pair(self, token: str):
        return random.choice([pair for pair in self.supported_tokens if pair != token])
    
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
