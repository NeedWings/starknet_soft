try:
    from MainRouter import *
    from bridger2 import *
    from eth_account import Account as eth_account
    def decrypt(filename):
        f = Fernet(KEY)
        with open(filename, 'rb') as file:
            encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data).decode()
        return decrypted_data.split(':')

    def decode_secrets():
        console_log.info("Decrypting your secret keys..")
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
                console_log.error(f'Error with trying to open file encoded_secrets.txt! {error}')
                input("Fix it and press enter: ")
        try:
            return json.loads(f.decrypt(file_data).decode())
        except :
            console_log.error("Key to Decrypt files is incorrect!")
            return decode_secrets()

    def transform_keys(private_keys, addresses):
        stark_keys = []
        for key in private_keys:
            try:
                int_key = int(key)
            except:
                int_key = int(key, 16)
            stark_keys.append(int_key) 
        return stark_keys

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
                try:
                    k = int(k)
                except:
                    k = int(k, 16)
                k = "0x" + (66-len(hex(k)))*"0" + hex(k)[2::]
                address = eth_account.from_key(k).address
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
                    "swap stables from chains and bridge to stark",
                    "starkgate",
                    "withdraw from stark",
                    "full withdraw(remove liquidity, swap to eth, bridge to chain)",
                    "send to stark off bridge different wallet(EVM)",
                    "send from stark to different wallet(EVM)",
                    "send to stark from different wallet(EVM)",
                    "full withdraw to different wallet(EVM)",
                    "",
                    "full module",
                    "",
                    "random swaps",
                    "swap to eth",
                    "",
                    "add liquidity",
                    "remove liquidity",
                    "",
                    "lending task",
                    "remove from lend",
                    "return borrowed tokens",
                    "",
                    "show addresses",
                    "encrypt_secrets",
                    "deploy accounts",
                    "universal braavos upgrader",
                    "universal argent upgrader",
                    "stats",
                    "",
                    "dmail",
                    "starknet_id",
                    "collateral zklend",
                    "mint cheap domain"
                ],
            )
        ]
        action = inquirer.prompt(question, theme=loadth(theme))['action']
        return action

    
    def task_1(stark_keys):

        tasks = []
        delay = 0

        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            account, call_data, salt, class_hash = import_argent_account(key, client)
            private_key = "0x" + "0"*(66-len(hex(key))) + hex(key)[2::]
            web3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))
            wallet = web3.eth.account.from_key(private_key).address
            indexes.append(wallet)
            tasks.append(Thread(target=start_eth_bridge_no_off, args=(hex(key), '0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], delay)))
            
            delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])
        for i in tasks:
            i.start()
        for k in tasks:
            k.join()

    

    def main():
        routers = []
        


        print(autosoft)
        print(subs_text)
        print("\n")
        f = open(f"{SETTINGS_PATH}to_run_addresses.txt", "r")
        addresses = f.read().lower().split("\n")
        f.close()
        action = get_action()
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
        elif action == "lending task":
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
        elif action == "universal braavos upgrader":
            task_number = 29
        elif action == "return borrowed tokens":
            task_number = 30
        elif action == "universal argent upgrader":
            task_number = 31
        elif action == "mint cheap domain":
            task_number = 32

        for i in range(len(addresses)):
            if len(addresses[i]) < 50:
                addresses[i] = "0x" + "0"*(42-len(addresses[i])) + addresses[i][2::]
            else:
                addresses[i] = "0x" + "0"*(66-len(addresses[i])) + addresses[i][2::]
        if task_number == 11:
            encode_secrets()
        else:    
            private_keys = decode_secrets()
            accounts = transform_keys(private_keys, addresses)
            tasks = []

            if task_number != 10 and task_number != 16:
                shuffle(accounts)
                if SETTINGS["delayed_start"]:
                    console_log.info(f"waiting delayed start: {SETTINGS['delayed_start_time']} hours")
                    time.sleep(SETTINGS['delayed_start_time']*3600)

            if task_number in [27, 22]:
                with open(f"{SETTINGS_PATH}EVM_stark_pairs.txt", "r") as f:
                    addrs = f.read().lower().split("\n")
                
                for address in addrs:
                    pair = address.split(";")
                    pair[0] = "0x" + "0"* (66-len(hex(int(pair[0], 16)))) + hex(int(pair[0], 16))[2::]
                    addr_dict[pair[0]] = pair[1]
            print(f"Bot found {counter} private keys to work")
            if task_number in [1, 9, 6, 21, 25]:
                if task_number == 1:
                    task_1(accounts)
                elif task_number == 9:
                    task_9(accounts)
                elif task_number == 6:
                    task_6(accounts)
                elif task_number == 21:
                    bridge_to_stark_from_different_address(accounts)
                elif task_number == 25:
                    off_bridge_different_wallet(accounts)
            else:
                if SETTINGS["UseProxies"]:
                    loop = asyncio.new_event_loop()

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
                            proxy_dict[f"http://{proxy[0]}@{proxy[1]}"].append(('0x' + '0'*(66-len(proxy[2])) + proxy[2][2::]).lower())
                        else:
                            proxy_dict[f"http://{proxy[0]}@{proxy[1]}"] = [('0x' + '0'*(66-len(proxy[2])) + proxy[2][2::]).lower()]

                    client = GatewayClient(MAINNET)
                    counter = 1
                    delay = 0
                    for proxy in proxy_dict:

                        addresses = proxy_dict[proxy]
                        for key in accounts:
                            account, call_data, salt, class_hash = import_argent_account(key, client)
                            
                            if ('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]) in addresses:
                                client = FullNodeClient(random.choice(SETTINGS["RPC"]["STARKNET_MAINNET"]), proxy=proxy)
                                print(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] connected to proxy: {proxy}")
                                tasks.append(loop.create_task(MainRouter(key, delay, task_number, client).start()))
                                delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])
                    
                else:
                    loop = asyncio.new_event_loop()

                    client = FullNodeClient(random.choice(SETTINGS["RPC"]["STARKNET_MAINNET"]))
                    delay = 0
                    for account in accounts:
                        tasks.append(loop.create_task(MainRouter(account, delay, task_number, client).start()))
                        delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])
                    
                loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))
    
    def run(task_number, stark_keys, eth_keys=None, proxy_servers=[]):
        delay = 0
        tasks = []
        loop = asyncio.new_event_loop()
        match task_number:
            case 1:
                pass##
            case 6:
                pass##
            case 9:
                pass##
            case 10:
                pass##
            case 21:
                pass##
            case 22:
                print('Not ready yet')
            case 25:
                pass##
            case 26:
                pass
            case 27:
                print('Not ready yet')
            case _:
                for i in range(len(stark_keys)):
                    client = FullNodeClient(random.choice(SETTINGS["RPC"]["STARKNET_MAINNET"]), proxy=proxy_servers[i] if proxy_servers else None)
                    tasks.append(loop.create_task(MainRouter(stark_keys[i], delay, task_number, client).start()))
                    delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])
        loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

except Exception as e:
    print(f"Unexpected error: {e}")