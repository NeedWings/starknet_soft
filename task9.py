from utils import *
from task1 import *




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

async def check_main_asset(address: str):
        main_asset = (None, 0, None, None)
        
        data = RPC_OTHER.keys()

            
        for net_name in data:
            usdt_contract = USDT_CONTRACTS.get(net_name)
            if usdt_contract != None:
                usdt, human_usdt = await get_evm_token_balance(address, usdt_contract, net_name)
                logger.info(f'[{address}] ({net_name}) Got USDT balance: {human_usdt}')
            else:
                usdt, human_usdt = 0, 0
            if net_name != "BSC_MAINNET":
                usdc_contract = USDC_CONTRACTS.get(net_name)
                if usdc_contract != None:
                    usdc, human_usdc = await get_evm_token_balance(address, USDC_CONTRACTS.get(net_name), net_name)
                    logger.info(f'[{address}] ({net_name}) Got USDC balance: {human_usdc}')
                else: usdc, human_usdc = 0, 0
            else: usdc, human_usdc = 0, 0

            if usdc > usdt:
                if human_usdc > SETTINGS["minUSDamount"]:
                    asset, name_, token_contract = usdc, "USDC", USDC_CONTRACTS.get(net_name)
                else: asset = 0
            else: 
                if human_usdt > SETTINGS["minUSDamount"]:
                    asset, name_, token_contract = usdt, "USDT", USDT_CONTRACTS.get(net_name)
                else: asset = 0

            if asset > main_asset[1]:
                main_asset = net_name, asset, name_, token_contract

        return main_asset





def send_transaction_evm(private_key: str, tx: dict, net_name: str, approve=False) -> str: 
    w3 = Web3(Web3.HTTPProvider(random.choice(RPC_OTHER[net_name])))


    gasEstimate = w3.eth.estimate_gas(tx)

    tx['gas'] = round(gasEstimate)
    signed_txn = w3.eth.account.sign_transaction(tx, private_key=private_key)

    tx_token = w3.to_hex(w3.eth.send_raw_transaction(signed_txn.rawTransaction))

    logger.success(f"Approved: {tx_token}")
    return tx_token

async def wait_until_tx_finished_evm(address: str, hash: str, net_name: str, max_time=500) -> bool:
        w3 = Web3(Web3.HTTPProvider(random.choice(RPC_OTHER[net_name])))
        start_time = time.time()
        while True:
            try:
                if time.time() - start_time > max_time:
                    logger.error(f'[{address}] [{hash}] transaction is failed (timeout)')
                    return False
                receipts = w3.eth.get_transaction_receipt(hash)
                status = receipts.get("status")

                if status == 1:
                    logger.success(f"{hash} is completed")
                    return True
                elif status is None:
                    #print(f'[{hash}] still processed')
                    await asyncio.sleep(0.3)
                elif status != 1:
                    logger.error(f'[{address}] [{hash}] transaction is failed')
                    return False
            except:
                #print(f"[{hash}] still in progress")
                await asyncio.sleep(1)

async def approve_token_evm(private_key: str, address: str, token_address: str, net_name: str, spender: str, amount=False):
        async def __check_allowance__():
            amount_approved = contract.functions.allowance(address, spender).call()
            if amount_approved < balance:
                while True:
                    try:
                        tx = contract.functions.approve(spender, balance).build_transaction(
                            await get_tx_data_evm(address, w3, net_name)
                        )
                        return tx
                    except Exception as error:

                        logger.error(f'[{address}] Got error while trying approve token: {error}')
                        await sleeping(f'[{address}] Error fault. Update after ')

        contract, w3 = get_contract_evm(token_address, net_name)
        while True:
            balance, human_balance = await get_evm_token_balance(address, contract=contract)
            if amount:
                if balance > amount:
                    balance = amount
                elif amount > balance:
                    pass
                
            check_data = await __check_allowance__()
            if check_data is not None:
                try:
                    tx_hash = send_transaction_evm(private_key, check_data, net_name, approve=True)
                    if await wait_until_tx_finished_evm(address, tx_hash, net_name):
                        return
                    else:
                        await sleeping(f'[{address}] Tx is failed. Will retry approve token ')
                except Exception as error:
                    logger.error(f'[{address}] Cant submit tx! Error: {error}')
                    await sleeping(f'[{address}] Error fault. Update after ')
            else:
                return



async def sushi_swap_handler(private_key: str, net_name: str, amount: int, ticker_name: str, token_contract: str):
    web3 = Web3(Web3.HTTPProvider(random.choice(RPC_OTHER[net_name])))
    wallet = web3.eth.account.from_key(private_key).address
    while True:
        try:
            to_work_amount = random.uniform(SETTINGS["USDAmountToBridge"][0], SETTINGS["USDAmountToBridge"][1])
            spender = SUSHI_SWAP[net_name]
            eth_price = get_ticker_price('eth')
            balance, human = await get_evm_token_balance(wallet, token_contract, net_name)

            if human > to_work_amount:
                balance, human, decimals = await get_evm_token_balance(wallet, token_contract, net_name, get_decimals=True)
                amount = round(to_work_amount * 10**decimals)
                minimal_amount = to_work_amount
            else:
                balance, human, decimals = await get_evm_token_balance(wallet, token_contract, net_name, get_decimals=True)
                amount = balance
                minimal_amount = human


            minimal = (float(minimal_amount) / eth_price) * 0.97
            await approve_token_evm(private_key, wallet, token_contract, net_name, spender)
            await sleeping(wallet)

            contract, w3 = get_contract_evm(spender, net_name, token=SUSHI)

            if net_name in ["BSC_MAINNET", "POLYGON_MAINNET"]:
                minimal = round(minimal * 10**18)
            elif net_name in ["ARBITRUM_MAINNET", "OPTIMISM_MAINNET"]:
                minimal = Web3.to_wei(minimal, 'ether')
            else:
                minimal = round(minimal * 10**12)

            tx_data = await get_tx_data_evm(wallet, w3, net_name)

            tx = contract.functions.processRoute(
                token_contract,
                amount,
                WETH[net_name],
                minimal,
                wallet,
                ROUTES[net_name][ticker_name] + wallet.lower().split("0x")[1]
            ).build_transaction(tx_data)

            hash = send_transaction_evm(private_key, tx, net_name)
            if await wait_until_tx_finished_evm(wallet, hash, net_name):
                return
            else:
                logger.error(f'[{wallet}] Tx is failed! Will wake one more soon..')
                await sleeping(wallet, True)

                
        except Exception as error:
            logger.error(f"[{wallet}] Error with swap sushi", str(error))
            await sleeping(wallet, True)

async def quote_layer_zero_fee(dist_chain_name: str, sender_net: str, private_key: str):
    
    while True:
        try:
            contract, w3 = get_contract_evm(STARGATE_CONTRACTS[sender_net], sender_net, token=BRIDGE_ABI)
            address = w3.eth.account.from_key(private_key).address
            chain_id = LAYERZERO_CHAINS_ID[dist_chain_name]

            comission = contract.functions.quoteLayerZeroFee(
                chain_id, 1, 
                get_bytes(address.split("0x")[1]),
                get_bytes(address.split("0x")[1]), 
                    (
                        0, 0, 
                        get_bytes(ZERO_ADDRESS.split("0x")[1])
                    )
            ).call()[0]
            human_readable = round(Web3.from_wei(comission, 'ether'), 7)

            if human_readable > SETTINGS["FEES"][sender_net]:
                logger.info(f'[{address[35:45]}] Got fee to way:{sender_net}->{dist_chain_name} : {human_readable} Fee is to high')
                await sleeping(address, True)
            else:
                logger.info(f'[{address[35:45]}] Got fee to way:{sender_net}->{dist_chain_name} : {human_readable} ')
                return comission
            
        except Exception as error:
            logger.error(f'[{address}] Cant get L0 fees | {error}')
            await sleeping(address, True)


async def process_bridge(private_key: str, dist_net: str, 
                         sending_net: str, token_address: str,
                         w3: Web3, contract, asset_type: int,
                         contract_address):
    attemps = 0
    w3 = Web3(Web3.HTTPProvider(random.choice(RPC_OTHER[sending_net])))
    wallet = w3.eth.account.from_key(private_key).address
    while True:
        try:
            dist_asset = random.choice(ASSETS_TYPES[dist_net])
            await approve_token_evm(private_key, wallet, token_address, sending_net, contract_address)
            await sleeping(wallet)

            balance, human_readable = await get_evm_token_balance(wallet, token_address, sending_net)
            logger.info(f'[{wallet}] Want to bridge: {human_readable} USD, dist asset: {dist_asset}')
            if human_readable < SETTINGS["minUSDamount"]:
                logger.debug(f'human: {human_readable}, min: {SETTINGS["minUSDamount"]}, balance: {balance}')
                return
            min_recv_amount = round(balance * 0.998)
            comission = await quote_layer_zero_fee(dist_net, sending_net, private_key)
            tx_data = await get_tx_data_evm(wallet, w3, sending_net, value=comission)

            tx = contract.functions.swap(
                LAYERZERO_CHAINS_ID[dist_net],
                asset_type, dist_asset, wallet,
                balance, min_recv_amount,
                (0, 0, "0x0000000000000000000000000000000000000001"),
                wallet.lower(), b''
            ).build_transaction(tx_data)

            hash = send_transaction_evm(private_key, tx, sending_net)
            if await wait_until_tx_finished_evm(wallet, hash, sending_net):
                return True
        except Exception as error:
            attemps += 1
            if attemps > 10:
                logger.error(f'[{wallet}] Attemps amount is too high!')
                return
            logger.error(f"[{wallet}] Failed to send bridge. Error: " + str(error))
            await sleeping(wallet, True)

async def make_bridge(sending_net: str, dist_net: str, private_key: str, token_address: str):
    if token_address in USDT_CONTRACTS.values():
        asset_type = 2
    elif token_address in USDC_CONTRACTS.values():
        asset_type = 1
    else:
        logger.error(f'This asset: {token_address} is not supported to bridge')
        return
    
    contract_address = STARGATE_CONTRACTS[sending_net]
    contract, w3 = get_contract_evm(contract_address, sending_net, token=BRIDGE_ABI)

    return await process_bridge(private_key, dist_net, sending_net, token_address,
                   w3, contract, asset_type, contract_address)

async def collector(private_key: str, recepient: str, delay: int):
    private_key = "0x" + "0"*(66-len(private_key)) + private_key[2::]
    await asyncio.sleep(delay)
    web3 = Web3(Web3.HTTPProvider(random.choice(RPC_OTHER["ARBITRUM_MAINNET"])))
    wallet = web3.eth.account.from_key(private_key).address
    while True:
        try:
            net_name, amount, ticker_name, token_contract = await check_main_asset(wallet)
            if net_name is not None:
            
                if net_name in ["ARBITRUM_MAINNET"]:
                    logger.info(f'[{wallet}] Will wake swap for eth')
                    await sushi_swap_handler(private_key, net_name, amount, ticker_name, token_contract)
                    break
                else:
                    while True:
                        logger.info(f"[{wallet}] Want to make bridge! (main asset in net: {net_name})")
                        dist_net = "ARBITRUM_MAINNET"
                        bridge_status = await make_bridge(net_name, dist_net, private_key, token_contract)
                        break
                        
                    if bridge_status is True:
                        while True:
                            net_name, amount, ticker_name, token_contract = await check_main_asset(wallet)
                            if net_name == dist_net:
                                break
                            await sleeping(wallet)
                    else:
                        logger.error(f"[{wallet}] Bridge status is False!")
                        return
            else:
                max_net_value, net_name = await check_net_assets(wallet)
                if max_net_value > SETTINGS["MinEthValue"]:
                    logger.info(f'[{wallet}] Found weth assets!')
                    break
                else:
                    logger.info(f"[{wallet}] Net name is None, will wait assets. Will sleep: {SETTINGS['ParsingSleep']}")
                    await asyncio.sleep(SETTINGS["ParsingSleep"])
    
        except Exception as error:
            logger.error(f"[{wallet}] failed to make bridge/swap Error: " + str(error))
            await sleeping(wallet, True)
    
    await eth_bridge_no_off(private_key, recepient, 0)

def start_collector(private_key: str, recepient: str, delay: int):
    loop = asyncio.new_event_loop()
    tasks = []
    tasks.append(loop.create_task(collector(private_key, recepient, delay)))
    loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

def task_9(stark_keys):
    loop = asyncio.new_event_loop()
    tasks = []
    delay = 0
    for key in stark_keys:
        if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
            client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
        else:
            client = GatewayClient(net=MAINNET)
        account, call_data, salt, class_hash = import_argent_account(key, client)

        tasks.append(Thread(target=start_collector, args=(hex(key), '0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], delay)))
        
        delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])
    for i in tasks:
        i.start()
    for k in tasks:
        k.join()


