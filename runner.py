try:
    from .MainRouter import *
    from .bridger2 import *
    from eth_account import Account as eth_account

    def transform_keys(private_keys, addresses):
        stark_keys = []
        for key in private_keys:
            try:
                int_key = int(key)
            except:
                int_key = int(key, 16)
            stark_keys.append(int_key) 
        return stark_keys

    
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
    
    def run(task_number, args): #(task_number, stark_keys, eth_keys=None, proxy_servers=[]):
        delay = 0
        tasks = []
        #loop = asyncio.new_event_loop()
        match task_number:
            case 1:
                pass##
            case 6:
                asyncio.run(simple_bridge(args['eth_key'], args['argent_address']))
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
                client = FullNodeClient(random.choice(SETTINGS["RPC"]["STARKNET_MAINNET"]))
                asyncio.run(MainRouter(args['argent_key'], 0, task_number, client,  args['wallet_provider'], proxy=args['proxy_server'] if args['proxy_server'] else None).start())
                #for arg in args:
                #    client = FullNodeClient(random.choice(SETTINGS["RPC"]["STARKNET_MAINNET"]), proxy=arg['proxy_server'] if arg['proxy_server'] else None)
                #    tasks.append(loop.create_task(MainRouter(arg['argent_key'], delay, task_number, client).start()))
                #    delay += get_random_value_int(SETTINGS["ThreadRunnerSleep"])
        #loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))
except Exception as e:
    print(f"Unexpected error: {e}")