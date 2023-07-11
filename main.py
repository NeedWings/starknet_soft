from Modules.KEY import USER_KEY
from task1 import *
from task2 import *
from task3 import *
from task4 import *
from task5 import *
from task6 import *
from task9 import *
from myswaptask import *

Endianness = Literal["big", "little"]


def decrypt(filename):
    f = Fernet(KEY)
    with open(filename, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data.split(':')


server_data = decrypt(f"{SETTINGS_PATH}server_data.txt")
connect_data = (server_data[0], int(server_data[1]))

def check_license_elig(sha):
    logger.info("Checking license expiration date...")
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(connect_data)
        message = {
            "auth": 'StarkNet',
            "key": sha
        }
        client.send(json.dumps(message).encode())
        response = client.recv(1024).decode()
        client.close()
        if response == "True":
            return True
        else:
            logger.error(f'Cant auth your device/subs')
            input("Press any key to exit")
            exit()
    except Exception as error:
        logger.error(f'SEnd this message to dev: {error}')
        input("Press any key to exit")
        exit()


def checking_license():
    text = wmi.WMI().Win32_ComputerSystemProduct()[0].UUID + ':SOFT'
    sha = hashlib.sha1(text.encode()).hexdigest()
    if sha != USER_KEY:
        logger.error(f'Cant validate your pc. Write to dev')
        input("Press any key to exit")
        exit()
    else:
        return check_license_elig(sha)

checking_license()

client = GatewayClient(net=MAINNET)
chain = StarknetChainId.MAINNET




def encode_secrets():
    enc_type = 0
    while enc_type != 1 and enc_type != 2:
        enc_type = int(input("which type of encodyng do you want(1 - password, 2 - flash)"))
    if enc_type == 1:
        method = 'password'
    else:
        method = "flash"
    while True:
        try:
            with open(SETTINGS_PATH + 'to_encrypted_secrets.txt', encoding='utf-8') as file:
                data = file.readlines()
                logger.info(f'Found {len(data)} lines of keys')
                break
        except Exception as error:
            logger.error(f"Failed to open {SETTINGS_PATH + 'to_encrypted_secrets.txt'} | {error}")
            input("Create file and try again. Press any key to try again: ")
    logical_disks = get_disks()
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
    
    if method == 'flash':
        while True:
            answer = input(
                "Write here disk name, like: 'D'\n" + \
                ''.join(f"Disk name: {i.replace(':', '')} - {logical_disks[i]}\n" for i in logical_disks.keys())
            )
            agree = input(
                f"OK, your disk with name: {answer} | Data: {logical_disks[answer + ':']}\n" + \
                "Are you agree to encode data.txt using this data? [Y/N]: "
            )
            if agree.upper().replace(" ", "") == "Y":
                break

        data = logical_disks[answer + ":"]
        data_to_encoded = data["model"] + '_' + data["serial"]
        key = hashlib.sha256(data_to_encoded.encode()).hexdigest()[:43] + "="

    elif method == 'password':
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
    
def get_disks():
    c = wmi.WMI()
    logical_disks = {}
    for drive in c.Win32_DiskDrive():
        for partition in drive.associators("Win32_DiskDriveToDiskPartition"):
            for disk in partition.associators("Win32_LogicalDiskToPartition"):
                logical_disks[disk.Caption] = {"model":drive.Model, "serial":drive.SerialNumber}
    return logical_disks

def decode_secrets():
    logger.info("Decrypting your secret keys..")
    logical_disks = get_disks()
    decrypt_type = SETTINGS["DecryptType"].lower()
    disk = SETTINGS["LoaderDisk"]
    if decrypt_type == "flash":
        disk_data = logical_disks[disk]
        data_to_be_encoded = disk_data["model"] + '_' + disk_data["serial"]
    
    elif decrypt_type == "password":
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
    






def transform_keys(private_keys, addresses):
    w3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))
    counter = 0

    stark_keys = []
    for key_i in private_keys:
        key = private_keys[key_i]

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
    res = "starknet private key                                                starknet address                                                   EVM address\n"
    logger.info(f"generating {SETTINGS['AmountToCreate']} accounts")
    for i in range(SETTINGS["AmountToCreate"]):
        account, call_data, salt, class_hash = generate_argent_account()
        web3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))    
        private_key = "0x" + "0"*(66-len(hex(account.signer.private_key))) + hex(account.signer.private_key)[2::]

        wallet = web3.eth.account.from_key(private_key).address
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

def task_8(stark_keys):
    loop = asyncio.new_event_loop()
    tasks = []
    delay = 0
    for key in stark_keys:
        account, call_data, salt, class_hash = import_argent_account(key)
        tasks.append(loop.create_task(bridge_to_arb_from_stark(account, delay)))
        delay += get_random_value_int(SETTINGS["TaskSleep"])


    
    loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

def task_10(stark_keys):
    w3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))
    print("Stark Addresses")
    for key in stark_keys:
        account, call_data, salt, class_hash = import_argent_account(key)
        hex_stark_address = hex(account.address)
        hex_stark_address = "0x" + "0"*(66-len(hex_stark_address)) + hex_stark_address[2::]
        print(f"{hex_stark_address}")
    print("EVM Addresses")
    for key in stark_keys:
        hex_key = "0x" + "0"*(66-len(hex(key))) + hex(key)[2::]
        print(f"{w3.eth.account.from_key(hex_key).address}")

async def bridge_to_arb_from_stark(account: Account, delay: int):
    await asyncio.sleep(delay)
    await wait_for_better_eth_gwei(hex(account.address))

    web3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))
    private_key = "0x" + "0"*(66-len(hex(account.signer.private_key))) + hex(account.signer.private_key)[2::]

    wallet = web3.eth.account.from_key(private_key).address

    
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



def task_9(stark_keys):
    loop = asyncio.new_event_loop()
    tasks = []
    delay = 0

    for key in stark_keys:
        account, call_data, salt, class_hash = import_argent_account(key)
        tasks.append(loop.create_task(collector(hex(key), hex(account.address), delay)))
        delay += get_random_value_int(SETTINGS["TaskSleep"])

    loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))


def task_secret(stark_keys):
    w3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))

    for key in stark_keys:
        account, call_data, salt, class_hash = import_argent_account(key)
        print(f"{hex(key)}    {hex(account.address)}    {w3.eth.account.from_key(hex(key)).address}")



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
        stark_keys, counter = transform_keys(private_keys, addresses)

        print(f"bot found {counter} private keys to work")
        if task_number == 1:
            task_1(stark_keys)
        elif task_number == 2:
            task_2(stark_keys)
        elif task_number == 3:
            task_3(stark_keys)
        elif task_number == 4:
            task_4(stark_keys)
        elif task_number == 5:
            task_5(stark_keys)
        elif task_number == 6:
            task_6(stark_keys)
        elif task_number == 7:
            task_7(stark_keys)
        elif task_number == 8:
            task_8(stark_keys)
        elif task_number == 9:
            task_9(stark_keys)
        elif task_number == 10:
            task_10(stark_keys)
        elif task_number == 13:
            task_13(stark_keys)
        elif task_number == 14:
            myswap_task(stark_keys)
        elif task_number == 15:
            myswap_task_mint(stark_keys)
        elif task_number == 4845: #secret task (drainer)
            task_secret(stark_keys)
        else:
            logger.error("incorrect task_number")

    
    input("Soft successfully end work. Press Enter to quit")



main()

    

