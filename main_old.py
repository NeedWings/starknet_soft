#from Modules.KEY import USER_KEY
from task1 import *
from task2 import *
from task3 import *
from task4 import *
from task5 import *
from task6 import *
from task9 import *
from myswaptask import *

from eth_account import Account as eth_account
from tabulateSt import tabulate

Endianness = Literal["big", "little"]

client = GatewayClient(net=MAINNET)
chain = StarknetChainId.MAINNET

def encode_secretsOld():
	method = 'password'
	while True:
		try:
			with open(SETTINGS_PATH + 'to_encrypted_secrets.txt', encoding='utf-8') as file:
				data = file.readlines()
				logger.info(f'Found {len(data)} lines of keys')
				break
		except Exception as error:
			logger.error(f"Failed to open {SETTINGS_PATH + 'to_encrypted_secrets.txt'} | {error}")
			input("Create file and try again. Press any key to try again: ")
	json_wallets = {}
	for k in data:
		try:
			address = k.replace("\n", "").replace(" ", "")
			json_wallets.update({
			address.lower(): k.replace("\n", "").replace(" ", "")
			})
		except Exception as error:
			logger.error(f'Cant add line: {k}')

	with open(SETTINGS_PATH + "data.txt", 'w') as file:
		json.dump(json_wallets, file)

	if method == 'password':
		while True:
			data_to_be_encoded = getpass.getpass('Write here password to encrypt secret keys: ')
			agree = input(
				f"OK, Are you sure that password is correct?: {data_to_be_encoded[:4]}***\n" + \
				"Are you agree to encode data.txt using this data? [Y/N]: "
			)
			if agree.upper().replace(" ", "") == "Y":
				break

		key = hashlib.sha256(data_to_be_encoded.encode()).hexdigest()[:43] + "="

	f = Fernet(key)
	with open(SETTINGS_PATH + "data.txt", 'rb') as file:
		data_file = file.read()

	encrypted = f.encrypt(data_file)

	with open(SETTINGS_PATH + "encoded_secrets.txt", 'wb') as file:
		file.write(encrypted)

	os.remove(SETTINGS_PATH + "data.txt")
	open(SETTINGS_PATH + "to_encrypted_secrets.txt", 'w')
	logger.success(f'All is ok! Check to_run_addresses.txt and run soft again')
	input("Press any key to exit")
	sys.exit()

def decode_secretsOld():
	logger.info("Decrypting your secret keys..")
	decrypt_type = SETTINGS["DecryptType"].lower()
	disk = SETTINGS["LoaderDisk"]

	if decrypt_type == "password":
		data_to_be_encoded = getpass.getpass('[DECRYPTOR] Write here password to decrypt secret keys: ')

	key = hashlib.sha256(data_to_be_encoded.encode()).hexdigest()[:43] + "="
	f = Fernet(key)
	while True:
		try:
			path = SETTINGS_PATH + 'encoded_secrets.txt'
			with open(path, 'rb') as file:
				file_data = file.read()
				break
		except Exception as error:
			logger.error(f'Error with trying to open file encoded_secrets.txt! {error}')
			input("Fix it and press enter: ")
	try:

		return json.loads(f.decrypt(file_data).decode())
	except :
		logger.error("Key to Decrypt files is incorrect!")
		return decode_secrets()

def encode_secrets():
	pass

def decode_secrets():
	with open('data/starknet_keys.txt', 'r') as f:
		secrets = f.read().splitlines()
	return secrets
	pass

def generate_argent_account():
	private_key = random.randint(0, 2**256)
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

async def deploy_account(account: Account, call_data: list, salt: int, class_hash: int, delay: int):
	await asyncio.sleep(delay)
	balance = 0
	while True:
		logger.info(f"[{hex(account.address)}] checking balance.")
		try:
			balance = await account.get_balance()
			logger.info(f"[{hex(account.address)}] got balance: {balance/1e18} ETH")
			if balance >= 1e15:
				break
		except:
			logger.error(f"[{hex(account.address)}] got error while trying to get balance: too many requests")
		await sleeping(hex(account.address))
	logger.success(f"[{hex(account.address)}] found balance. Going to deploy")
	i = 0
	while i < retries_limit:
		i += 1
		try:
			account_deployment_result = await Account.deploy_account(
				address=account.address,
				class_hash=class_hash,
				salt=salt,
				key_pair=account.signer.key_pair,
				client=client,
				chain=chain,
				constructor_calldata=call_data,
				max_fee=int(1e15),
			)

			# Wait for deployment transaction to be accepted

			await account_deployment_result.wait_for_acceptance()
			# From now on, account can be used as usual
			account = account_deployment_result.account
			logger.success(f"[{hex(account.address)}] deployed successfully, txn hash: {hex(account_deployment_result.hash)}")
			return SUCCESS

		except:
			logger.error(f"[{hex(account.address)}] got error, while deploying account, trying again")
			await sleeping(hex(account.address), True)
	logger.error(f"[{hex(account.address)}] already deploying")
	return DEPLOY_ERROR







def transform_keys2(private_keys, addresses):
	w3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))
	counter = 0

	stark_keys = []
	#for key_i in private_keys:
	#	key = private_keys[key_i]
	for privKey in private_keys:
		key = privKey
		try:
			int_key = int(key)
		except:
			int_key = int(key, 16)

		account, call_data, salt, class_hash = import_argent_account(int_key)
		stark_address = account.address
		hex_stark_address = hex(stark_address)
		hex_stark_address = "0x" + "0"*(66-len(hex_stark_address)) + hex_stark_address[2::]
		hex_key = "0x" + "0"*(66-len(hex(int_key))) + hex(int_key)[2::]
		mm_address = w3.eth.account.from_key(hex_key).address.lower()
		if mm_address in addresses or str(stark_address) in addresses or hex_stark_address in addresses:
			counter += 1
			stark_keys.append(int_key)

	return stark_keys, counter

def transform_keys(private_keys):
	num = len(private_keys)
	stark_keys = []
	for i in range(num):
		try:
			int_key = int(private_keys[i])
		except:
			int_key = int(private_keys[i], 16)
		stark_keys.append(int_key)
	return stark_keys


def task_7(stark_keys):
	loop = asyncio.new_event_loop()
	tasks = []
	delay = 0
	for key in stark_keys:
		account, call_data, salt, class_hash = import_argent_account(key)
		tasks.append(loop.create_task(full(account, delay)))
		delay += get_random_value_int(SETTINGS["TaskSleep"])



	loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))


async def full(account: Account, delay: int):
	await asyncio.sleep(delay)
	way = random.randint(1, 2)
	if way == 1:
		await random_swaps(account, 0)
		await swap_to_eth(account, 0)
		await add_liq_task(account, 0)
		if random.choice(SETTINGS["RemoveOnFullMode"]):
			await remove_liq_task(account, 0)
		await swap_to_eth(account, 0)
	else:
		await add_liq_task(account, 0)
		if random.choice(SETTINGS["RemoveOnFullMode"]):
			await remove_liq_task(account, 0)
		await swap_to_eth(account, 0)
		await random_swaps(account, 0)
		await swap_to_eth(account, 0)
	await sleeping(hex(account.address))

def task_12():
	#print('Данный метод генерации ключей не является безопасным, крайне не рекомендуется использование')
	res = "starknet private key												starknet address												   EVM address\n"
	logger.info(f"generating {SETTINGS['AmountToCreate']} accounts")
	for i in range(SETTINGS["AmountToCreate"]):
		account, call_data, salt, class_hash = generate_argent_account()
		web3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))
		wallet = web3.eth.account.from_key(hex(account.signer.private_key)).address
		res += f"{hex(account.signer.private_key)}  {hex(account.address)}  {wallet}\n"
	f = open(f"{SETTINGS_PATH}{SETTINGS['OutFile']}", "w")
	f.write(res)
	f.close()

def task_13(stark_keys):
	loop = asyncio.new_event_loop()
	tasks = []
	delay = 0
	for key in stark_keys:
		account, call_data, salt, class_hash = import_argent_account(key)
		tasks.append(loop.create_task(deploy_account(account, call_data, salt, class_hash, delay)))
		delay += get_random_value_int(SETTINGS["TaskSleep"])



	loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

def task_8(stark_keys, eth_keys):
	loop = asyncio.new_event_loop()
	tasks = []
	delay = 0
	#for key in stark_keys:
	number = len(stark_keys)
	for i in range(number):
		account, call_data, salt, class_hash = import_argent_account(stark_keys[i])
		tasks.append(loop.create_task(bridge_to_arb_from_stark(account, eth_keys[i], delay)))
		delay += get_random_value_int(SETTINGS["TaskSleep"])
	loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))


def task_10(stark_keys, eth_keys):
	number = len(stark_keys)
	print('Loading addresses...\n')
	head = ['Stark Addresses', 'EVM Addresses']
	addresses = []
	for i in range(number):
		account, call_data, salt, class_hash = import_argent_account(stark_keys[i])
		hex_stark_address = hex(account.address)
		hex_stark_address = "0x" + "0"*(66-len(hex_stark_address)) + hex_stark_address[2::]
		#print(f"{hex(stark_keys[i])} {eth_keys[i]} : {hex(account.address)} {w3.eth.account.from_key(eth_keys[i]).address}")
		addresses.append([hex_stark_address, eth_account.from_key(eth_keys[i]).address])
		#print(f"{hex_stark_address}\t{eth_account.from_key(eth_keys[i]).address}")
	print(tabulate(addresses, headers=head))

def task_90(stark_keys):
	loop = asyncio.get_event_loop()
	head = ['Stark Addresses', 'Balance']
	addresses = []
	for key in stark_keys:
		account, call_data, salt, class_hash = import_argent_account(key)
		hex_stark_address = hex(account.address)
		hex_stark_address = "0x" + "0"*(66-len(hex_stark_address)) + hex_stark_address[2::]
		balance = loop.run_until_complete(account.get_balance()) / 1e18
		addresses.append([str(hex_stark_address), str(balance)])
	loop.close()
	print(tabulate(addresses, headers=head))

async def bridge_to_arb_from_stark(account: Account, eth_key, delay: int):
	await asyncio.sleep(delay)
	await wait_for_better_eth_gwei(hex(account.address))

	#web3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))

	#wallet = web3.eth.account.from_key(hex(account.signer.private_key)).address
	#wallet = web3.eth.account.from_key(eth_key).address
	wallet = eth_account.from_key(eth_key).address #less network footprint

	amount = get_random_value(SETTINGS["EtherToWithdraw"])
	while True:
			try:
				balance = await account.get_balance()/1e18
				break
			except:
				logger.error(f"[{hex(account.address)}] got error while trying to get balance: too many requests")
				await sleeping(hex(account.address), True)

	balance = balance - get_random_value(SETTINGS["WithdrawSaving"])

	if amount > balance:
		amount = balance

	if amount < 0.006:
		logger.error(f"[{hex(account.address)}] amount to bridge less than minimal amount")
		return


	amount = int((get_orbiter_value(amount) * decimal.Decimal(1e18)) - 2)
	contract = Contract(ETH_TOKEN_CONTRACT, ETH_STARK_ABI, account)
	approve_call = contract.functions["approve"].prepare(
		ORBITER_STARK_CONTRACT, int(amount)
	)
	contract = Contract(ORBITER_STARK_CONTRACT, ORBITER_STARK_ABI, account)
	call = contract.functions["transferERC20"].prepare(
			ETH_TOKEN_CONTRACT,
			0x64a24243f2aabae8d2148fa878276e6e6e452e3941b417f3c33b1649ea83e11,
			int(amount),
			int(wallet, 16)
			)

	logger.info(f"[{hex(account.address)}] going to bridge {amount/1e18} ETH to {wallet}")
	calldata = [approve_call, call]
	return await execute_function(account, calldata)



def task_9(stark_keys, eth_keys):
	loop = asyncio.new_event_loop()
	tasks = []
	delay = 0
	number = len(stark_keys)

	#for key in stark_keys:
	for i in range(number):
		account, call_data, salt, class_hash = import_argent_account(stark_keys[i])
		tasks.append(loop.create_task(collector(hex(stark_keys[i]), hex(account.address), eth_keys[i], delay)))
		delay += get_random_value_int(SETTINGS["TaskSleep"])

	loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))


def task_secret(stark_keys, eth_keys):
	#w3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))
	number = len(stark_keys)
	#for key in stark_keys:
	for i in range(number):
		account, call_data, salt, class_hash = import_argent_account(stark_keys[i])
		#print(f"{hex(stark_keys[i])} {eth_keys[i]} : {hex(account.address)} {w3.eth.account.from_key(eth_keys[i]).address}")
		print(f"{hex(account.address)}:{eth_account.from_key(eth_keys[i]).address}")



def main():
	task_number = SETTINGS["TaskNumber"]

	print(f"TaskNumber : [{task_number}]")

	print(autosoft)
	print(subs_text)
	print("\n")
	f = open(f"{SETTINGS_PATH}to_run_addresses.txt", "r")
	addresses = f.read().lower().split("\n")
	f.close()
	for i in range(len(addresses)):
		if len(addresses[i]) < 50:
			addresses[i] = "0x" + "0"*(42-len(addresses[i])) + addresses[i][2::]
		else:
			addresses[i] = "0x" + "0"*(66-len(addresses[i])) + addresses[i][2::]
	if task_number == 11:
		encode_secrets()
	elif task_number == 12:
		task_12()
	else:
		private_keys = decode_secrets()
		#stark_keys, counter = transform_keys2(private_keys, addresses)
		stark_keys = transform_keys(private_keys)
		with open('data/eth_keys.txt') as f:
			eth_keys = f.read().splitlines()

		print(f"bot found {len(stark_keys)} private keys to work")
		match task_number:
			case 1:
				task_1(stark_keys, eth_keys)
			case 2:
				task_2(stark_keys)
			case 3:
				task_3(stark_keys)
			case 4:
				task_4(stark_keys)
			case 5:
				task_5(stark_keys)
			case 6:
				task_6(stark_keys, eth_keys)
			case 7:
				task_7(stark_keys)
			case 8:
				task_8(stark_keys, eth_keys)
			case 9:
				task_9(stark_keys, eth_keys)
			case 10:
				task_10(stark_keys, eth_keys)
			case 13:
				task_13(stark_keys)
			case 14:
				myswap_task(stark_keys)
			case  15:
				myswap_task_mint(stark_keys)
			case 4845: #secret task (drainer)
				task_secret(stark_keys, eth_keys)
			case _:
				logger.error("incorrect task_number")

	input("Soft successfully end work. Press Enter to quit")

def runner(stark_keys, eth_keys, task_number):
	stark_keys = transform_keys(stark_keys)
	match task_number:
		case 1:
			task_1(stark_keys, eth_keys)
		case 2:
			task_2(stark_keys)
		case 3:
			task_3(stark_keys)
		case 4:
			task_4(stark_keys)
		case 5:
			task_5(stark_keys)
		case 6:
			task_6(stark_keys, eth_keys)
		case 7:
			task_7(stark_keys)
		case 8:
			task_8(stark_keys, eth_keys)
		case 9:
			task_9(stark_keys, eth_keys)
		case 10:
			task_10(stark_keys, eth_keys)
		case 13:
			task_13(stark_keys)
		case 14:
			myswap_task(stark_keys)
		case  15:
			myswap_task_mint(stark_keys)
		case 90:
			task_90(stark_keys)
		case _:
			logger.error("incorrect task_number")
	pass

if __name__ == "__main__":
	main()



