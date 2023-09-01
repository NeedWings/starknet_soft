from utils import *
from task9 import *
from task6 import *
from task5 import *
from task3 import *
try:  
    

    async def stark_stats(account: Account, delay: int):
        await asyncio.sleep(delay)
        global starkstats
        txns = await get_contract_txns(account.address)
        swap_value = await get_total_swap_value(txns, account.client)
        while True:
            try:
                eth_balance = await account.get_balance()/1e18
                break
            except Exception as e:
                logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] can't get balance of ETH. Error: {e}")
                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
        while True:
            try:
                usdc_balance = await account.get_balance(USDC_TOKEN_CONTRACT)/1e6
                break
            except Exception as e:
                logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] can't get balance of USDC. Error: {e}")
                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
        while True:
            try:
                usdt_balance = await account.get_balance(USDT_TOKEN_CONTRACT)/1e6
                break
            except Exception as e:
                logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] can't get balance of USDT. Error: {e}")
                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
        while True:
            try:
                txn_count = await account.get_nonce()
                break
            except Exception as e:
                logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] can't get nonce. Error: {e}")
                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
        

        data = f"{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]};{txn_count};{eth_balance};{usdc_balance};{usdt_balance};{swap_value['myswap']['wsteth']};{swap_value['myswap']['usdc']};{swap_value['myswap']['usdt']};{swap_value['jediswap']['usdc']};{swap_value['jediswap']['usdt']};{swap_value['sithswap']['usdc']};{swap_value['sithswap']['usdt']};{swap_value['10kswap']['usdc']};{swap_value['10kswap']['usdt']};{swap_value['avnu']['usdc']};{swap_value['avnu']['usdt']}\n"
        starkstats += data.replace(".",",")
        logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] data:\ntxn count: {txn_count}\nETH: {eth_balance}\nUSDC: {usdc_balance}\nUSDT: {usdt_balance}")

    def task_stats(stark_keys):
        loop = asyncio.new_event_loop()
        tasks = []
        delay = 0
        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            account, call_data, salt, class_hash = import_argent_account(key, client)
            
            tasks.append(loop.create_task(stark_stats(account, delay)))
            delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])

        loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

        with open(f"{SETTINGS_PATH}starkstats.csv", "w") as f:
            f.write(starkstats)

    def remove_from_lend_task(stark_keys):
        loop = asyncio.new_event_loop()
        tasks = []
        delay = 0

        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            account, call_data, salt, class_hash = import_argent_account(key, client)
            tasks.append(loop.create_task(remove_from_lends(account, delay)))
            delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])

        loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

    async def remove_from_lends(account: Account, delay: int):
        await asyncio.sleep(delay)
        if SETTINGS["Lend"] == "zklend":

            while True:
                try:
                    lend_bal = await account.get_balance(0x01b5bd713e72fdc5d63ffd83762f81297f6175a5e0a4771cdadbc1dd5fe72cb1)
                    break
                except Exception as e:
                    logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] can't get balance: {e}")
                    await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])
            if lend_bal == 0:
                return
            lend_contract = Contract(ZKLEND_CONTRACT, ZKLEND_ABI, account)
            call2 = lend_contract.functions["withdraw"].prepare(
                    ETH_TOKEN_CONTRACT,
                    lend_bal
                )
            calldata = [call2]

        elif SETTINGS["Lend"].lower() == "nostra":
            lend_contract = Contract(0x070f8a4fcd75190661ca09a7300b7c93fab93971b67ea712c664d7948a8a54c6, NOSTRA_ABI, account)
            while True:
                try:
                    amount = await account.get_balance(0x070f8a4fcd75190661ca09a7300b7c93fab93971b67ea712c664d7948a8a54c6)
                    break
                except Exception as e:
                    logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] can't get balance of lend token. Error: {e}")
                    await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
            call = lend_contract.functions["burn"].prepare(
                account.address,
                account.address,
                amount
            )
            calldata = [call]
        else:
            logger.error(f"selected usupported lend({SETTINGS['Lend']})")
            input()
            exit()
        await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])
        logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] going to remove ETH from lend")
        return await execute_function(account, calldata)

    def mint_turkey_nft_task(stark_keys):
        loop = asyncio.new_event_loop()
        tasks = []
        delay = 0

        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            account, call_data, salt, class_hash = import_argent_account(key, client)
            tasks.append(loop.create_task(mint_turkey_nft(account, delay)))
            delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])

        loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

    async def mint_turkey_nft(account: Account, delay):
        await asyncio.sleep(delay)

        nft_numb = SETTINGS["NFTNumbTurkey"]
        i = 0
        while retries_limit > i:
            resp = req(f"https://api.starknetturkiye.org/eligibility?address={hex(account.address)}&campaign_id={nft_numb}")
            try:
                a = resp['eligible']
                if a:
                    break
                else:
                    logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] starknetturkiye sent bad data :( trying again")
                    await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
            except:
                logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] starknetturkiye sent bad data :( trying again")
                await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
            i+=1
        if retries_limit <= i:
            logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] max retries limit reached")
            return MAX_RETRIES_LIMIT_REACHED

        mint_contract = Contract(0x0106c94dc954944b3893e2102d9ad5065d04a0ec9b08910891d8eedb75965334, STARKNET_TURKEY_ABI, account)

        call = mint_contract.functions["mint"].prepare(
            nft_numb,

            {
                "wallet_address": account.address,
                "signer": 0x26128e6c0821347d2eea17548431dee2c66d9654cd3b9637447e2a91505d1df,
                "campaign_id": nft_numb,
                "amount": 1,
                "expiry": 1691596800,
                "strategy": 0x4f7e61fa8adab9e958f8c832868f77b149803834daa00491a1f2fbcd5dc5fb4,
                "collection": 0x106c94dc954944b3893e2102d9ad5065d04a0ec9b08910891d8eedb75965334
            },
            0x16ed14bf62427f6a87189a1855df2c6a467b93bf94cb8cf405482e4a670e982,
            [int(resp["sig_r"]),
            int(resp["sig_s"])]
        )

        calldata = [call]
        await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])
        logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] going to mint nft")
        return await execute_function(account, calldata)

    def test_prox(stark_keys):
        loop = asyncio.new_event_loop()
        tasks = []
        delay = 0

        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            account, call_data, salt, class_hash = import_argent_account(key, client)
            tasks.append(loop.create_task(bal(account, delay)))
            delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])

        loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

    async def bal(account: Account, delay: int):
        await asyncio.sleep(delay)
        
        for i in range(20):
            while True:
                try:
                    eth_balacne = await account.get_balance()
                    break
                except Exception as e:
                    logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got error while trying to get balance: {e}")
                    await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)
            logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] balance: {eth_balacne}")
            await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])

    def off_bridge_different_wallet(stark_keys):
        loop = asyncio.new_event_loop()
        tasks = []
        delay = 0
        with open(f"{SETTINGS_PATH}EVM_stark_pairs.txt", "r") as f:
            addresses = f.read().split("\n")

        addresses2 = {}

        for address in addresses:
            stark_int = int(address.split(";")[0], 16)
            addresses2[address.split(";")[1]] = '0x' + '0'*(66-len(hex(stark_int))) + hex(stark_int)[2::]

        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            web3 = Web3(Web3.HTTPProvider(random.choice(RPC_OTHER["ARBITRUM_MAINNET"])))
            wallet = web3.eth.account.from_key('0x' + '0'*(66-len(hex(key))) + hex(key)[2::]).address
            account, call_data, salt, class_hash = import_argent_account(key, client)
            tasks.append(loop.create_task(eth_bridge_official(hex(key), addresses2[wallet], delay)))
            delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])
        
        loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

    async def bridge_to_arb_from_stark(account: Account, delay: int, wallet: str = None):
        await asyncio.sleep(delay)
        await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])

        web3 = Web3(Web3.HTTPProvider(random.choice(RPC_FOR_LAYERSWAP["ARBITRUM_MAINNET"])))
        private_key = "0x" + "0"*(66-len(hex(account.signer.private_key))) + hex(account.signer.private_key)[2::]
        if wallet == None:
            wallet = web3.eth.account.from_key(private_key).address


        amount = get_random_value(SETTINGS["EtherToWithdraw"])

        while True:
                try:
                    balance = await account.get_balance()/1e18
                    break
                except Exception as e:
                    logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] got error while trying to get balance: {e}")
                    await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::], True)

        balance = balance - get_random_value(SETTINGS["WithdrawSaving"])

        if amount > balance:
            amount = balance

        if amount < 0.006:
            logger.error(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] amount to bridge less than minimal amount")
            return

        if SETTINGS["DistNet"].lower() == "arbitrum":
            amount = int((get_orbiter_value(amount) * decimal.Decimal(1e18)) - 2)
        elif SETTINGS["DistNet"].lower() == "zksync":
            amount = int((get_orbiter_value(amount) * decimal.Decimal(1e18)) + 10)
        elif SETTINGS["DistNet"].lower() == "ethereum":
            amount = int((get_orbiter_value(amount) * decimal.Decimal(1e18)) - 3)
        elif SETTINGS["DistNet"].lower() == "linea":
            amount = int((get_orbiter_value(amount) * decimal.Decimal(1e18)) + 19)
        else:
            logger.error("wrong value in DistNet")
            input()
            exit()
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

        logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] going to bridge {amount/1e18} ETH to {wallet}")
        calldata = [approve_call, call]
        return await execute_function(account, calldata)
    
    def bridge_to_stark_from_different_address(stark_keys):
        loop = asyncio.new_event_loop()
        tasks = []
        delay = 0
        with open(f"{SETTINGS_PATH}EVM_stark_pairs.txt", "r") as f:
            addresses = f.read().split("\n")
        addresses2 = {}
        for address in addresses:
            stark_int = int(address.split(";")[0], 16)
            addresses2[address.split(";")[1]] = '0x' + '0'*(66-len(hex(stark_int))) + hex(stark_int)[2::]
        
        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            web3 = Web3(Web3.HTTPProvider(random.choice(RPC_OTHER["ARBITRUM_MAINNET"])))
            wallet = web3.eth.account.from_key('0x' + '0'*(66-len(hex(key))) + hex(key)[2::]).address
            tasks.append(Thread(target=start_collector, args=(hex(key), addresses2[wallet], delay)))
            delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])

        for i in tasks:
            i.start()
        for k in tasks:
            k.join()

    def bridge_from_stark_to_different_wallet(stark_keys):
        loop = asyncio.new_event_loop()
        tasks = []
        delay = 0
        with open(f"{SETTINGS_PATH}EVM_stark_pairs.txt", "r") as f:
            addresses = f.read().split("\n")
        addresses2 = {} 
        for address in addresses:
            stark_int = int(address.split(";")[0], 16)
            addresses2['0x' + '0'*(66-len(hex(stark_int))) + hex(stark_int)[2::]] = address.split(";")[1]
        
        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            account, call_data, salt, class_hash = import_argent_account(key, client)
            tasks.append(loop.create_task(bridge_to_arb_from_stark(account, delay, wallet = addresses2['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]])))
            delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])

        loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

    def dmail_task(stark_keys):
        loop = asyncio.new_event_loop()
        tasks = []
        delay = 0

        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            account, call_data, salt, class_hash = import_argent_account(key, client)
            tasks.append(loop.create_task(dmail(account, delay)))
            delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])

        loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

    async def dmail(account, delay):
        await asyncio.sleep(delay)
        
        amount = get_random_value_int(SETTINGS["dmail_messages_amount"])
        for qawe in range(amount):
            l = "1234567890abcdefghijklmnopqrstuvwxyz"
            t = [random.choice(l) for i in range(get_random_value_int([3,9]))]
            text = ""
            for i in t:
                text += i
            
            addr_raw = [random.choice(l) for i in range(get_random_value_int([3,9]))]
            addr = ""
            for i in addr_raw:
                addr += i
            
            addr += "@gmail.com"

            felt_text = str_to_felt(text)
            felt_rec = str_to_felt(addr)
            await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])
            logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] going to send message({text}) to {addr}")

            dmail_contract = Contract(0x0454f0bd015e730e5adbb4f080b075fdbf55654ff41ee336203aa2e1ac4d4309, [{"data":[{"name":"from_address","type":"felt"},{"name":"to","type":"felt"},{"name":"theme","type":"felt"}],"keys":[],"name":"send","type":"event"},{"name":"transaction","type":"function","inputs":[{"name":"to","type":"felt"},{"name":"theme","type":"felt"}],"outputs":[]}], account)

            call = dmail_contract.functions["transaction"].prepare(
                felt_rec,
                felt_text
            )
            calldata = [call]

            await execute_function(account, calldata)

            await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])

    def starknet_id_task(stark_keys):
        loop = asyncio.new_event_loop()
        tasks = []
        delay = 0

        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            account, call_data, salt, class_hash = import_argent_account(key, client)
            tasks.append(loop.create_task(starknet_id(account, delay)))
            delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])

        loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))


    async def starknet_id(account, delay):
        await asyncio.sleep(delay)

        amount = get_random_value_int(SETTINGS["starknet_id_amount"])
        for i in range(amount):
            await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])

            id_contract = Contract(0x05dbdedc203e92749e2e746e2d40a768d966bd243df04a6b712e222bc040a9af, [{"name":"mint","type":"function","inputs":[{"name":"starknet_id","type":"felt"}],"outputs":[]}], account)
            logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] going to mint starknet id")
            call = id_contract.functions["mint"].prepare(
                random.randint(0, 999999999999)
            )
            calldata = [call]

            await execute_function(account, calldata)
            await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])

    def withdraw_all_task(stark_keys, other):
        loop = asyncio.new_event_loop()
        tasks = []
        delay = 0
        with open(f"{SETTINGS_PATH}EVM_stark_pairs.txt", "r") as f:
            addresses = f.read().split("\n")
        addresses2 = {} 
        for address in addresses:
            stark_int = int(address.split(";")[0], 16)
            addresses2['0x' + '0'*(66-len(hex(stark_int))) + hex(stark_int)[2::]] = address.split(";")[1]
        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            account, call_data, salt, class_hash = import_argent_account(key, client)
            out_wallets_result['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]] = ""
            if other:
                tasks.append(loop.create_task(withdraw_all(account, delay, addresses2['0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]])))
            else:
                tasks.append(loop.create_task(withdraw_all(account, delay)))

            delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])

        loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

    async def withdraw_all(account: Account, delay, wallet = None):
        SETTINGS["toSaveFunds"] = ["ETH"]
        await asyncio.sleep(delay)
        await remove_liq_task(account, 0)
        await swap_to_eth(account, 0)
        await bridge_to_arb_from_stark(account, 0, wallet)

    def colateral_task(stark_keys):
        loop = asyncio.new_event_loop()
        tasks = []
        delay = 0

        for key in stark_keys:
            if SETTINGS["UseProxies"] and key in proxy_dict_cfg.keys():
                client = GatewayClient(net=MAINNET, proxy=proxy_dict_cfg[key])
            else:
                client = GatewayClient(net=MAINNET)
            account, call_data, salt, class_hash = import_argent_account(key, client)
            tasks.append(loop.create_task(colateral(account, delay)))
            delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])

        loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))

    async def colateral(account: Account, delay):
        await asyncio.sleep(delay)
        for i in range(get_random_value_int(SETTINGS["zklend_collateral_amount"])):
            lend_contract = Contract(ZKLEND_CONTRACT, ZKLEND_ABI, account)
            call3 = lend_contract.functions["enable_collateral"].prepare(
                    ETH_TOKEN_CONTRACT
                )
            calldata = [call3]
            await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])
            logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] enabling collateral")
            await execute_function(account, calldata)
            await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])
            lend_contract = Contract(ZKLEND_CONTRACT, ZKLEND_ABI, account)
            call3 = lend_contract.functions["disable_collateral"].prepare(
                    ETH_TOKEN_CONTRACT
                )
            calldata = [call3]
            await wait_for_better_eth_gwei('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])
            logger.info(f"[{'0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::]}] disabling collateral")
            await execute_function(account, calldata)
            await sleeping('0x' + '0'*(66-len(hex(account.address))) + hex(account.address)[2::])


finally:
    pass
    