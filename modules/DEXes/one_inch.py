import requests

from web3 import AsyncWeb3

from modules.base_classes.base_account import BaseAccount
from modules.utils.txn_data_handler import TxnDataHandler
from modules.utils.token import EVMToken
from modules.utils.token_storage import nets_eth, nets_weth
from modules.utils.logger import logger
from modules.utils.utils import sleeping, req

class OneInch:
    
    base_url = "https://api-defillama.1inch.io"
    base_version = 5
    chain_ids = {
        'avalanche' : 43114,
        'polygon'   : 137,
        'ethereum'  : 1,
        'bsc'       : 56,
        'arbitrum'  : 42161,
        'optimism'  : 10,
        'fantom'    : 250
    }
    headers = {
        'authority': 'api-defillama.1inch.io',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6,pl;q=0.5,cy;q=0.4,fr;q=0.3',
        'cache-control': 'max-age=0',
        'if-none-match': 'W/"881-sjxAEIcDeTIyvhdXc7Xp3XMcK+s"',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        "0x-api-key" : ""
    }

    async def get_data(self, address: str, token1: EVMToken, token2: EVMToken, amount: int):
        try:
            net = token1.net_name
            
            token_out = token2.contract_address
            token_in = token1.contract_address

            url = f'{self.base_url}/v{self.base_version}.0/{self.chain_ids[net]}/swap?fromTokenAddress={token_in}&toTokenAddress={token_out}&amount={amount}&fromAddress={address}&slippage=1'
            while True:
                response = await req(url=url, headers=self.headers)
                if isinstance(response, dict):
                    if "tx" in response.keys():
                        return {
                            "data" : response["tx"]["data"],
                            "to"   : AsyncWeb3.to_checksum_address(response["tx"]["to"])
                        }
                    else:
                        if "Not enough allowance" in str(response):
                            return response
                
                    logger.error(f"[{address}] got error: {response}")
                    await sleeping(address, True)
                else:
                    await sleeping(address, True)
                    
        except Exception as e:
            logger.error(f"[{address}] got error: {e}")
            await sleeping(address, True)

    async def swap_stable(self, token: EVMToken, amount_in: int, sender: BaseAccount):
        net = token.net_name
        w3 = sender.get_w3(net)
        txn_data_handler = TxnDataHandler(sender, net, w3=w3)
        try:
            eth = nets_eth[net]
        except:
            eth = nets_weth[net]
        while True:
            data = await self.get_data(
                    sender.address,
                    token,
                    eth,
                    amount_in
                )
            
            if "Not enough allowance" in str(data):
                inch_address = AsyncWeb3.to_checksum_address(data["description"].split("Spender: ")[1])

                await token.get_approve_txn(sender, inch_address, amount_in, w3=w3)

            else:
                logger.info(f'[{sender.evm_address}] Inch response: {data}')

                txn = await txn_data_handler.get_txn_data()
                txn.update(data)

                return txn
        


        




