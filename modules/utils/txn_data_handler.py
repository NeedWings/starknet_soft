import random

from web3 import AsyncWeb3

from modules.config import RPC_LIST, SETTINGS
from modules.utils.logger import logger
from modules.utils.utils import sleeping


class TxnDataHandler:
      
    def __init__(self, sender, net_name, w3 = None) -> None:
        self.address = sender.evm_address
        self.net_name = net_name
        if w3:
            self.w3 = w3
        else:
            self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(random.choice(RPC_LIST[net_name])))
    
    async def get_gas_price(self):
        
        max_gas = AsyncWeb3.to_wei(SETTINGS.get("GWEI").get(self.net_name), 'gwei')

        while True:
            try:
                gas_price = await self.w3.eth.gas_price
                if gas_price > max_gas:
                    h_gas, h_max = AsyncWeb3.from_wei(gas_price, 'gwei'), AsyncWeb3.from_wei(max_gas, 'gwei')
                    logger.error(f'[{self.address}] Sender net: {self.net_name}. Current gasPrice: {h_gas} | Max gas price: {h_max}')
                    await sleeping(f'[{self.address}] Waiting best gwei. Update after ')
                else:
                    return round(gas_price)
                
            except Exception as error:
                logger.error(f'[{self.address}] Error: {error}')
                await sleeping(f'[{self.address}] Error fault. Update after ')


    async def get_txn_data(self, value=0):
        gas_price = await self.get_gas_price()

        data = {
            'chainId': await self.w3.eth.chain_id, 
            'nonce': await self.w3.eth.get_transaction_count(self.address),  
            'from': self.address, 
            "value": value
        }


        if self.net_name in ["avalanche", "polygon", "arbitrum", "ethereum", "base", "optimism"]:
            data["type"] = "0x2"


        if self.net_name not in ['arbitrum', "avalanche", "polygon", "ethereum", "base", "optimism"]:
            data["gasPrice"] = gas_price

        else:
            data["maxFeePerGas"] = gas_price
            if self.net_name == "polygon":
                data["maxPriorityFeePerGas"] = AsyncWeb3.to_wei(30, "gwei")
            elif self.net_name == "avalanche" or self.net_name == "base" or self.net_name == "optimism":
                data["maxPriorityFeePerGas"] = gas_price
            elif self.net_name == "ethereum":
                data["maxPriorityFeePerGas"] = AsyncWeb3.to_wei(0.05, "gwei")
            elif self.net_name == "arbitrum":
                data["maxPriorityFeePerGas"] = AsyncWeb3.to_wei(0.01, "gwei")
        
    
        return data