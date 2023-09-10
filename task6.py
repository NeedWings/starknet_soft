from utils import *

async def get_fee_for_starkgate(rec: str, amount: int):
    r = requests.post("https://alpha-mainnet.starknet.io/feeder_gateway/estimate_message_fee?blockNumber=pending",
                      data= json.dumps({"from_address":"993696174272377493693496825928908586134624850969",
                             "to_address":"0x073314940630fd6dcda0d772d4c972c4e0a9946bef9dabf4ef84eda8ef542b82",
                             "entry_point_selector":"0x2d757788a8d8d6f21d1cd40bce38a8222d70654214e96ff95d8086e684fbee5",
                             "payload":
                             [rec,
                              hex(amount),
                              "0x0"]}),
                        headers={
                            "Content-type": "application/json"
                        })

    return r.json()["overall_fee"]

async def starkgate(amount: float, eth_key: str, recepient: str):
    try:
        rpc = random.choice(RPC_FOR_LAYERSWAP["ETHEREUM_MAINNET"])

        web3 = Web3(Web3.HTTPProvider(rpc))
        fee = await get_fee_for_starkgate(recepient.lower(), int(amount*1e18))/1e18
        #wallet = web3.eth.account.from_key(eth_key).address
        wallet = eth_account.from_key(eth_key).address #less network footprint
        gas_price = await get_gas_price_evm(wallet, "ETHEREUM_MAINNET")

        balance = await get_native_balance_evm("ETHEREUM_MAINNET", wallet)/1e18
        amount = amount-fee
        if balance < amount+fee:
            logger.error(f"[{wallet}] not enough ETH for bridge ")
            return NOT_ENOUGH_NATIVE, ""

        contract = web3.eth.contract(STARKGATE_CONTRACT, abi=STARKGATE_ABI)

        dict_transaction = {
            'chainId': web3.eth.chain_id,
            'value' : int((amount + fee)*1e18),
            'gasPrice': gas_price,
            'nonce': web3.eth.get_transaction_count(wallet),
        }

        txn = contract.functions.deposit(
            int(amount*1e18), int(recepient, 16)
        ).build_transaction(dict_transaction)
        gasEstimate = web3.eth.estimate_gas(txn)

        txn['gas'] = round(gasEstimate)*2
        signed_txn = web3.eth.account.sign_transaction(txn, eth_key)
        txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.success(f"[{wallet}] txn has sent, hash: { Web3.to_hex(txn_hash)}")
        return SUCCESS, Web3.to_hex(txn_hash)

    except Exception as e:
        logger.error(f"[{wallet}] failed to send tx: ETHEREUM_MAINNET! Error: {e}")
        await sleeping(wallet, True)
        return UNEXPECTED_ERROR, ""

async def eth_bridge_officialOld(private_key: str, recepient: str, eth_key, delay: int):
    #private_key = "0x" + "0"*(66-len(private_key)) + private_key[2::]
    await asyncio.sleep(delay)
    #web3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ETHEREUM_MAINNET"])))
    #wallet = web3.eth.account.from_key(private_key).address
    wallet = eth_account.from_key(eth_key).address #less network footprint
    while True:
        value = await get_native_balance_evm("ETHEREUM_MAINNET", wallet)/1e18
        value = value - get_random_value(SETTINGS["SaveOnWallet"])
        if value >= SETTINGS["MinEthValue"]:
            break
        else:
            logger.error(f"{[wallet]} balance below MinEthValue, keep looking")
            await sleeping(wallet, True)

    amountUSD = get_random_value(SETTINGS["USDAmountToBridge"])
    ETH_price = get_eth_price()

    amount = amountUSD/ETH_price

    if value < amount:
        amount = value
    logger.info(f"[{wallet}] going to bridge {amount} ETH in starkgate to {recepient}")
    await starkgate(amount, eth_key, recepient)
    await sleeping(wallet)

async def eth_bridge_official(private_key: str, recepient: str, eth_key, delay: int):
    await asyncio.sleep(delay)
    wallet = eth_account.from_key(eth_key).address #less network footprint
    while True:
        balance = await get_native_balance_evm("ETHEREUM_MAINNET", wallet)/1e18
        amount = balance * get_random_value(SETTINGS["EthShareToBridge"])
        value = balance - get_random_value(SETTINGS["SaveOnWallet"])
        if value >= SETTINGS["MinEthValue"]:
            break
        else:
            logger.error(f"{[wallet]} balance below MinEthValue, keep looking")
            return
            await sleeping(wallet, True)
    if value < amount:
        amount = value
    logger.info(f"[{wallet}] going to bridge {amount} ETH in starkgate to {recepient}")
    await starkgate(amount, eth_key, recepient)
    await sleeping(wallet)

def task_6(stark_keys, eth_keys):
    loop = asyncio.new_event_loop()
    tasks = []
    delay = 0
    number = len(stark_keys)
    #for key in stark_keys:
    for i in range(number):
        account, call_data, salt, class_hash = import_argent_account(stark_keys[i])
        tasks.append(loop.create_task(eth_bridge_official(hex(stark_keys[i]), hex(account.address), eth_keys[i], delay)))
        delay += get_random_value_int(SETTINGS["TaskSleep"])

    loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))
