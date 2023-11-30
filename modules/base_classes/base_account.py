from abc import ABC, abstractmethod
from web3 import AsyncWeb3
from starknet_py.net.account.account import Account as StarkNativeAccount


class BaseAccount(ABC):
    stark_native_account: StarkNativeAccount = None
    stark_address: str = None
    evm_address: str = None
    proxies = None

    @abstractmethod
    async def send_txn_starknet(self, calldata):
        pass

    @abstractmethod
    async def get_balance_starknet(self, token):
        pass

    @abstractmethod
    async def get_balance_evm(self, token):
        pass

    @abstractmethod
    async def send_txn_evm(self, txn, net_name):
        pass

    @abstractmethod
    def get_w3(self, net_name) -> AsyncWeb3:
        pass