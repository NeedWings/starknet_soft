import random
from cfg import *
from starknet_py.net.account.account import _add_max_fee_to_transaction, _add_signature_to_transaction, _merge_calls, _execute_payload_serializer
from starknet_py.hash.utils import compute_hash_on_elements
from eth_account import Account as eth_account


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

async def get_wsteth_price(address):
    while True:
        response = req("https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd&ids=wrapped-steth")
        if type(response) is dict:
            return float(response["wrapped-steth"]["usd"])
        else:
            logger.error(f"[{address}] can't get wsteth price, will try again")
            await sleeping(address, True)

def get_eth_price():
    while True:
        try:
            result = req(f'https://api.etherscan.io/api?module=stats&action=ethprice&apikey={SETTINGS["etherscanKey"]}')
            return float(result['result']['ethusd'])
        except:
            print('failed to get eth price, sleeping 5')
            time.sleep(5)
    #return get_ticker_price('eth')

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
    if SETTINGS["useAdvanced"]:
        key_pair = KeyPair.from_private_key(private_key)
        salt = key_pair.public_key
        if SETTINGS["Provider"].lower() == "argent":
            account_initialize_call_data = [key_pair.public_key, 0]
        elif SETTINGS["Provider"].lower() == "braavos":
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
        elif SETTINGS["Provider"].lower() == "braavos_old":
            class_hash = 0x03131fa018d520a037686ce3efddeab8f28895662f019ca3ca18a626650f7d1e
            key_pair = KeyPair.from_private_key(private_key)
            salt = key_pair.public_key
            account_initialize_call_data = [key_pair.public_key]

            call_data = [
                0x69577e6756a99b584b5d1ce8e60650ae33b6e2b13541783458268f07da6b38a,
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


    account = Account(
            address=address, client=client, key_pair=key_pair, chain=chain
        )

    return account, call_data, salt, class_hash

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

async def execute_function(provider: Account,  calls: list):
    i = 0
    while retries_limit > i:
        resp = await get_invocation(provider, 0, calls, retries_limit)
        if resp == MAX_RETRIES_LIMIT_REACHED:
            logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] max retries limit reached!")
            return MAX_RETRIES_LIMIT_REACHED, ""
        try:
            logger.success(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] sending transaction with hash: {hex(resp.transaction_hash)}")
            await provider.client.wait_for_tx(resp.transaction_hash)
            logger.success(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] txn has sent! hash of txn: "+hex(resp.transaction_hash))
            return SUCCESS, hex(resp.transaction_hash)
        except Exception as e:
            logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] got error while sending txn: {hex(resp.transaction_hash)}, trying again")
            await sleeping('0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::], True)
        i += 1
    logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] max retries limit reached")
    return CAIRO_ERROR, ""


async def sign_deploy_account_transaction_braavos(
    class_hash: int,
        contract_address_salt: int,
        constructor_calldata: Optional[List[int]] = None,
        *,
        nonce: int = 0,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
        signer: BaseSigner
    ) -> DeployAccount:
    constructor_calldata = constructor_calldata or []

    deploy_account_tx = DeployAccount(
        class_hash=class_hash,
        contract_address_salt=contract_address_salt,
        constructor_calldata=constructor_calldata,
        version=1,
        max_fee=0,
        signature=[],
        nonce=nonce,
    )

    deploy_account_tx = _add_max_fee_to_transaction(deploy_account_tx, max_fee)
    signature = sign_transaction_braavos(deploy_account_tx, signer.private_key)
    return _add_signature_to_transaction(deploy_account_tx, signature)


async def deploy_account_braavos(
        *,
        address: AddressRepresentation,
        class_hash: int,
        salt: int,
        key_pair: KeyPair,
        client: Client,
        chain: StarknetChainId,
        constructor_calldata: Optional[List[int]] = None,
        nonce: int = 0,
        max_fee: Optional[int] = None,
        auto_estimate: bool = False,
    ) -> AccountDeploymentResult:
    # pylint: disable=too-many-locals
    """
    Deploys an account contract with provided class_hash on Starknet and returns
    an AccountDeploymentResult that allows waiting for transaction acceptance.
    Provided address must be first prefunded with enough tokens, otherwise the method will fail.
    If using Client for either TESTNET, TESTNET2 or MAINNET, this method will verify if the address balance
    is high enough to cover deployment costs.
    :param address: calculated and prefunded address of the new account.
    :param class_hash: class_hash of the account contract to be deployed.
    :param salt: salt used to calculate the address.
    :param key_pair: KeyPair used to calculate address and sign deploy account transaction.
    :param client: a Client instance used for deployment.
    :param chain: id of the Starknet chain used.
    :param constructor_calldata: optional calldata to account contract constructor. If ``None`` is passed,
        ``[key_pair.public_key]`` will be used as calldata.
    :param nonce: Nonce of the transaction.
    :param max_fee: max fee to be paid for deployment, must be less or equal to the amount of tokens prefunded.
    :param auto_estimate: Use automatic fee estimation, not recommend as it may lead to high costs.
    """
    address = parse_address(address)
    calldata = (
        constructor_calldata
        if constructor_calldata is not None
        else [key_pair.public_key]
    )
    if address != (
        computed := compute_address(
            salt=salt,
            class_hash=class_hash,
            constructor_calldata=calldata,
            deployer_address=0,
        )
    ):
        raise ValueError(
            f"Provided address {hex(address)} is different than computed address {hex(computed)} "
            f"for the given class_hash and salt."
        )

    account = Account(
        address=address, client=client, key_pair=key_pair, chain=chain
    )
    deploy_account_tx = await sign_deploy_account_transaction_braavos(
        class_hash=class_hash,
        contract_address_salt=salt,
        constructor_calldata=calldata,
        nonce=nonce,
        max_fee=max_fee,
        auto_estimate=auto_estimate,
        signer=account.signer
    )
    if chain in (
        StarknetChainId.TESTNET,
        StarknetChainId.TESTNET2,
        StarknetChainId.MAINNET,
    ):
        balance = await account.get_balance()
        if balance < deploy_account_tx.max_fee:
            raise ValueError(
                "Not enough tokens at the specified address to cover deployment costs."
            )
    
    result = await client.deploy_account(deploy_account_tx)
    
    return AccountDeploymentResult(
        hash=result.transaction_hash, account=account, _client=account.client
    )

async def get_contract_txns(address):
    address = ("0x" + "0"*(66 - len(hex(address))) + hex(address)[2::]).lower()
    while True:
        try:
            resp = req(f"https://api.viewblock.io/starknet/contracts/{address}?network=mainnet", headers={"Origin":"https://viewblock.io","Referer":"https://viewblock.io/"})
            pages_amount = int(resp["txs"]["pages"])
            first_txns = resp["txs"]["docs"]
            break
        except:
            logger.error(f"[{address}] can't get transactions, trying again")
            await sleeping(address, True)
    txns_raw = []
    
    txns_raw += first_txns
    for i in range(pages_amount-1):
        while True:
            try:
                resp = req(f"https://api.viewblock.io/starknet/contracts/{address}/txs?page={i+2}&network=mainnet", headers={"Origin":"https://viewblock.io","Referer":"https://viewblock.io/"})
                txns_raw += resp["docs"]
                break
            except:
                logger.error(f"[{address}] can't get transactions, trying again")
                await sleeping(address, True)
        
        await sleeping(address)

    txns = []
    for txn in txns_raw:
        txns.append(txn["hash"])

    return remove_same_elements_from_list(txns)
    
def remove_same_elements_from_list(data: List):
    end_data = []

    for element in data:
        if element not in end_data:
            end_data.append(element)
    return end_data

async def get_total_swap_value(txns, client: GatewayClient):
    result = {
        "myswap":{
            "usdt": 0,
            "usdc": 0,
            "wsteth": 0
        },
        "10kswap":{
            "usdt": 0,
            "usdc": 0
        },
        "sithswap":{
            "usdt": 0,
            "usdc": 0
        },
        "jediswap":{
            "usdt": 0,
            "usdc": 0
        },
        "avnu":{
            "usdt": 0,
            "usdc": 0
        }
    }
    for txn in txns:
        try:
            while True:
                try:
                    tx_data = await client.get_transaction(txn)
                    break
                except Exception as e:
                    logger.error("can't get transaction, trying again")
                    await sleeping("", True)
            calldata = tx_data.calldata
            if calldata[0] == 2:
                dex = calldata[5]
                first_token = calldata[1]
                if dex == MYSWAP_CONTRACT:
                    pool_id = calldata[13]
                    if first_token == ETH_TOKEN_CONTRACT:
                        second_token = SECOND_TOKEN_FROM_POOL_ID_MYSWAP[pool_id]
                        eth_value = calldata[15]/1e18
                        result["myswap"][second_token] += eth_value

                    else:
                        second_token = SECOND_TOKEN_FROM_POOL_ID_MYSWAP[pool_id]
                        eth_value = calldata[17]/1e18
                        result["myswap"][second_token] += eth_value

                elif dex == JEDISWAP_CONTRACT:
                    if first_token == ETH_TOKEN_CONTRACT:
                        second_token = TOKENS_REVERCE[calldata[19]]
                        eth_value = calldata[13]/1e18
                        result["jediswap"][second_token] += eth_value

                    else:
                        second_token = TOKENS_REVERCE[calldata[18]]
                        eth_value = calldata[15]/1e18
                        result["jediswap"][second_token] += eth_value

                elif dex == TEN_K_SWAP_CONTRACT:
                    if first_token == ETH_TOKEN_CONTRACT:
                        second_token = TOKENS_REVERCE[calldata[19]]
                        eth_value = calldata[13]/1e18
                        result["10kswap"][second_token] += eth_value

                    else:
                        second_token = TOKENS_REVERCE[calldata[18]]
                        eth_value = calldata[15]/1e18
                        result["10kswap"][second_token] += eth_value
                
                elif dex == SITHSWAP_CONTRACT:
                    if first_token == ETH_TOKEN_CONTRACT:
                        second_token = TOKENS_REVERCE[calldata[19]]
                        eth_value = calldata[13]/1e18
                        result["sithswap"][second_token] += eth_value

                    else:
                        second_token = TOKENS_REVERCE[calldata[18]]
                        eth_value = calldata[15]/1e18
                        result["sithswap"][second_token] += eth_value
                
                elif dex == ANVU_CONTRACT:
                    if first_token == ETH_TOKEN_CONTRACT:
                        second_token = TOKENS_REVERCE[calldata[26]]
                        eth_value = calldata[14]/1e18
                        result["avnu"][second_token] += eth_value

                    else:
                        second_token = TOKENS_REVERCE[calldata[25]]
                        eth_value = calldata[19]/1e18
                        result["avnu"][second_token] += eth_value
        except Exception as e:
            pass
    return result

def get_braavos_addr_from_private_key(private_key):
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
    address = compute_address(
        salt=salt,
        class_hash=class_hash,  
        constructor_calldata=call_data,
        deployer_address=0,
    )
    return address


async def get_invocation(provider: Account, i: int, calls, limit: int):

    if i >= limit:
        return MAX_RETRIES_LIMIT_REACHED
    try:
        nonce = await provider.get_nonce()
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
            sender_address=provider.address,
        )

        max_fee = await provider._get_max_fee(transaction, auto_estimate=True)/1e18
        if max_fee > SETTINGS["MaxFee"]:
            logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] countd fee for txn is {max_fee}, which is more than in settings ({SETTINGS['MaxFee']}). Trying again")
            await sleeping('0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::], True)
        
            return await get_invocation(provider, i, calls, limit)
        invocation = await provider.execute(calls=calls, auto_estimate=True)
        return invocation
    except Exception as e:
        i+=1
        logger.error(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] got error while trying to execute a function: {e}")
        logger.info(f"[{'0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::]}] trying again")
        await sleeping('0x' + '0'*(66-len(hex(provider.address))) + hex(provider.address)[2::], True)
        
'''
        logger.error(f"[{hex(provider.address)}] got error while trying to execute a function: {e}")
        logger.info(f"[{hex(provider.address)}] trying again")
        await sleeping(hex(provider.address), True)
'''
        return await get_invocation(provider, i, calls, limit)

def approve_token_call(amount: float, spender: int, contract: Contract):
    decimals = DECIMALS[contract.address]
    call = contract.functions["approve"].prepare(
        spender, int(amount*10**decimals)
    )
    return call


def _sign_deploy_account_transaction_braavos(transaction: DeployAccount, private_key: int):
        contract_address = compute_address(
            salt=transaction.contract_address_salt,
            class_hash=transaction.class_hash,
            constructor_calldata=transaction.constructor_calldata,
            deployer_address=0,
        )
        tx_hash = compute_deploy_account_transaction_hash(
            contract_address=contract_address,
            class_hash=transaction.class_hash,
            constructor_calldata=transaction.constructor_calldata,
            salt=transaction.contract_address_salt,
            max_fee=transaction.max_fee,
            version=transaction.version,
            chain_id=23448594291968334,
            nonce=transaction.nonce,
        )
        
        tx_hash = compute_hash_on_elements([tx_hash, ACTUAL_IMPL, 0, 0, 0, 0, 0, 0, 0])

        # pylint: disable=invalid-name
        r, s = message_signature(msg_hash=tx_hash, priv_key=private_key)
        return [r, s, 0x2c2b8f559e1221468140ad7b2352b1a5be32660d0bf1a3ae3a054a4ec5254e4, 0, 0, 0, 0, 0, 0, 0]

def _sign_transaction_braavos(transaction: Invoke, private_key: int):
    tx_hash = compute_transaction_hash(
        tx_hash_prefix=TransactionHashPrefix.INVOKE,
        version=transaction.version,
        contract_address=get_braavos_addr_from_private_key(private_key),
        entry_point_selector=DEFAULT_ENTRY_POINT_SELECTOR,
        calldata=transaction.calldata,
        max_fee=transaction.max_fee,
        chain_id=23448594291968334,
        additional_data=[transaction.nonce],
    )
    # pylint: disable=invalid-name
    r, s = message_signature(msg_hash=tx_hash, priv_key=private_key)
    return [r, s, 0x2c2b8f559e1221468140ad7b2352b1a5be32660d0bf1a3ae3a054a4ec5254e4, 0, 0, 0, 0, 0, 0, 0]

def _sign_declare_transaction_braavos(transaction: Declare, private_key: int):
    tx_hash = compute_declare_transaction_hash(
        contract_class=transaction.contract_class,
        chain_id=23448594291968334,
        sender_address=get_braavos_addr_from_private_key(private_key),
        max_fee=transaction.max_fee,
        version=transaction.version,
        nonce=transaction.nonce,
    )
    # pylint: disable=invalid-name
    r, s = message_signature(msg_hash=tx_hash, priv_key=private_key)
    return [r, s, 0x2c2b8f559e1221468140ad7b2352b1a5be32660d0bf1a3ae3a054a4ec5254e4, 0, 0, 0, 0, 0, 0, 0]
def _sign_declare_v2_transaction_braavos(transaction: DeclareV2, private_key: int):
    tx_hash = compute_declare_v2_transaction_hash(
        contract_class=transaction.contract_class,
        compiled_class_hash=transaction.compiled_class_hash,
        chain_id=23448594291968334,
        sender_address=get_braavos_addr_from_private_key(private_key),
        max_fee=transaction.max_fee,
        version=transaction.version,
        nonce=transaction.nonce,
    )
    # pylint: disable=invalid-name
    r, s = message_signature(msg_hash=tx_hash, priv_key=private_key)
    return [r, s, 0x2c2b8f559e1221468140ad7b2352b1a5be32660d0bf1a3ae3a054a4ec5254e4, 0, 0, 0, 0, 0, 0, 0]

def sign_transaction_braavos(
        transaction: AccountTransaction, private_key: int
    ):
        if isinstance(transaction, Declare):
            return _sign_declare_transaction_braavos(transaction, private_key)
        if isinstance(transaction, DeclareV2):
            return _sign_declare_v2_transaction_braavos(transaction, private_key)
        if isinstance(transaction, DeployAccount):
            return _sign_deploy_account_transaction_braavos(transaction, private_key)
        return _sign_transaction_braavos(cast(Invoke, transaction), private_key)

async def wait_for_better_eth_gwei(address: str):
    w3 = Web3(Web3.HTTPProvider(random.choice(RPC_OTHER["ETHEREUM_MAINNET"])))
    
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
            price = w3.eth.gas_price
        except:
            logger.error(f"[{address}] can't get eth gas price. will try later")
            await sleeping(address, True)
            continue
        if price < limit:
            break
        logger.info(f"[{address}] Current gas price in eth is {Web3.from_wei(price, 'gwei')}, which is more, than max in settings({SETTINGS['MaxETHGwei']}). Will wait for better fees")
        await sleeping(address)

