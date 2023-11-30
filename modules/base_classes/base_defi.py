from random import choice

from abc import ABC, abstractmethod
from loguru import logger as console_log

from modules.config import SETTINGS

class BaseDEX(ABC):
    name = None
    supported_tokens = []
    lpts = []
    contract_address = None
    abi = []

    def __init__(self) -> None:
        new_supported_tokens = []
        for token in self.supported_tokens:
            if token in SETTINGS["Supported_tokens"]:
                new_supported_tokens.append(token)
        self.supported_tokens = new_supported_tokens

    @abstractmethod
    async def get_token1_for_token2_price(self, token1, token2, amount_in, sender):
        pass

    @abstractmethod
    async def create_txn_for_swap(self, amount_in, token1, amount_out, token2, sender, full):
        pass

    @abstractmethod
    async def create_txn_for_liq(self, amount1, token1, amount2, token2, sender):
        pass

    @abstractmethod
    async def create_txn_for_remove_liq(self, lptoken, sender):
        pass

    

    def get_pair_for_token(self, token: str):
        for i in range(20):
            pair = choice(self.supported_tokens)
            if token != pair:
                return pair
        console_log.error("Can't find pair for token")
        return -5
    
class BaseLend(ABC):
    contract_address = None
    name = None
    supported_tokens = []
    lend_tokens = []

    @abstractmethod
    async def create_txn_for_adding_token(self, token, amount, sender):
        pass

    @abstractmethod
    async def create_txn_for_removing_token(self, amount, token, sender):
        pass

    @abstractmethod
    async def create_txn_for_borrow(self, amount, token, sender):
        pass
    
    @abstractmethod
    async def create_txn_for_return(self, token, sender):
        pass

    