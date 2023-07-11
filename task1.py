from utils import *


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


async def orbiter(amount: float, source: str, eth_key: str, recepient: str):
	try:
		if amount < 0.005:
			logger.error(f"[{wallet}] value lower, than minimal amount of bridge(0.005)")
			return VALUE_TOO_LOW, ""
		recepient = recepient[2::]
		while len(recepient)<64:
			recepient = "0"+recepient
		recepient = "0x03"+recepient
		rpc = str(random.choice(RPC_FOR_LAYERSWAP[source]))
		web3 = Web3(Web3.HTTPProvider(rpc))
		amount = get_orbiter_value(amount)
		wallet = web3.eth.account.from_key(eth_key).address
		balance = await get_native_balance_evm(source, wallet)
		if balance < amount*decimal.Decimal(1e18):
			logger.error(f"[{wallet}] not enough ETH for bridge ")
			return NOT_ENOUGH_NATIVE, ""
		contract = web3.eth.contract(ORBITER_CONTRACT, abi=ORBITER_ABI)
		dict_transaction = {
			'chainId': web3.eth.chain_id,
			'value' : int(amount * decimal.Decimal(1e18)),
			'gasPrice': web3.eth.gas_price,
			'nonce': web3.eth.get_transaction_count(wallet),
		}
		gasEstimate = web3.eth.estimate_gas(dict_transaction)

		dict_transaction["gas"] = gasEstimate*2
		txn = contract.functions.transfer(
			ORBITER_CONTRACTS_REC, recepient
		).build_transaction(dict_transaction)

		signed_txn = web3.eth.account.sign_transaction(txn, eth_key)
		txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
		return SUCCESS, Web3.to_hex(txn_hash)
	except Exception as e:
		logger.error(f"[{wallet}] failed to send tx: {source}! Error: {e}")
		await sleeping(wallet, True)
		return UNEXPECTED_ERROR, ""

async def layerswap(amount: float, source: str, eth_key: str, recepient: str):
	try:
		rpc = random.choice(RPC_FOR_LAYERSWAP[source])
		web3 = Web3(Web3.HTTPProvider(rpc))
		wallet = web3.eth.account.from_key(eth_key).address

		balance = await get_native_balance_evm(source, wallet)
		if balance < amount*1e18:
			logger.error(f"[{wallet}] not enough ETH for bridge ")
			return NOT_ENOUGH_NATIVE, ""

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
				"Accept-Language":"en-US,en;q=0.9",
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
			return LAYERSWAP_BAD_DATA, ""


		tx = {
			'nonce': web3.eth.get_transaction_count(wallet),
			'to': Web3.to_checksum_address(address),
			'value': Web3.to_wei(amount, 'ether'),
			'gasPrice': web3.eth.gas_price,
			'chainId': web3.eth.chain_id
		}
		gasEstimate = web3.eth.estimate_gas(tx)

		tx["gas"] = gasEstimate*2

		signed_tx = web3.eth.account.sign_transaction(tx, eth_key)

		#send transaction
		tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)


		return SUCCESS, Web3.to_hex(tx_hash)
	except Exception as e:
		logger.error(f"[{wallet}] failed to send tx: {source}! Error: {e}")
		await sleeping(wallet, True)
		return UNEXPECTED_ERROR, ""

async def eth_bridge_no_off(private_key: str, recepient: str, eth_key, delay: int):
	await asyncio.sleep(delay)
	way = random.choice(SETTINGS["BridgeType"])
	#web3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))
	#wallet = web3.eth.account.from_key(private_key).address
	#wallet = web3.eth.account.from_key(eth_key).address
	wallet = eth_account.from_key(eth_key).address #less network footprint
	while True:
		value, net = await check_net_assets(wallet)
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

	amount
	if amount < SETTINGS["MinEthValue"] and amount < 0.006:
		logger.error(f"[{wallet}] amount to bridge({amount} ETH) lower than minimum")
	logger.info(f"[{wallet}] going to bridge {amount} ETH in {way} to {recepient}")

	if way == "orbiter":
		#res = await orbiter(amount, net, private_key, recepient)
		res = await orbiter(amount, net, eth_key, recepient)
	elif way == "layerswap":
		#res = await layerswap(amount, net, private_key, recepient)
		res = await layerswap(amount, net, eth_key, recepient)
	else:
		logger.error(f"selected unsupported bridge ({way}), please choose one from this (orbiter, layerswap)")
		input("Please restart soft with correct settings")

	if res[0] == SUCCESS:
		logger.success(f"[{wallet}] txn has sent, hash: {res[1]}")
		await sleeping(wallet)



def task_1(stark_keys, eth_keys):
	loop = asyncio.new_event_loop()
	tasks = []
	delay = 0
	number = len(stark_keys)

	#for key in stark_keys:
	for i in range(number):
		account, call_data, salt, class_hash = import_argent_account(stark_keys[i])
		tasks.append(loop.create_task(eth_bridge_no_off(hex(key), hex(account.address), eth_keys[i], delay)))
		delay += get_random_value_int(SETTINGS["TaskSleep"])


	loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))
