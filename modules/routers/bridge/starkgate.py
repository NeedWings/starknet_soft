
import json
from random import uniform, choice

from starknet_py.contract import Contract

from modules.base_classes.base_account import BaseAccount
from modules.utils.txn_data_handler import TxnDataHandler
from modules.utils.utils import decimal_to_int, req_post, sleeping
from modules.utils.logger import logger
from modules.utils.token_storage import nets_weth, eth, eth_ethereum
from modules.utils.token import WRAPPED_TOKEN_ABI, STARK_TOKEN_ABI
from modules.config import RPC_LIST


class Starkgate:

    contract_address = "0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419"
    ABI = [{"anonymous":False,"inputs":[],"name":"LogBridgeActivated","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"sender","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":True,"internalType":"uint256","name":"l2Recipient","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"nonce","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"fee","type":"uint256"}],"name":"LogDeposit","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"sender","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":True,"internalType":"uint256","name":"l2Recipient","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"nonce","type":"uint256"}],"name":"LogDepositCancelRequest","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"sender","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":True,"internalType":"uint256","name":"l2Recipient","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"nonce","type":"uint256"}],"name":"LogDepositReclaimed","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"acceptedGovernor","type":"address"}],"name":"LogNewGovernorAccepted","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"nominatedGovernor","type":"address"}],"name":"LogNominatedGovernor","type":"event"},{"anonymous":False,"inputs":[],"name":"LogNominationCancelled","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"removedGovernor","type":"address"}],"name":"LogRemovedGovernor","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"LogSetL2TokenBridge","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"LogSetMaxDeposit","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"LogSetMaxTotalBalance","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"recipient","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"LogWithdrawal","type":"event"},{"inputs":[],"name":"acceptGovernance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"cancelNomination","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"l2Recipient","type":"uint256"}],"name":"deposit","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"l2Recipient","type":"uint256"}],"name":"deposit","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"l2Recipient","type":"uint256"},{"internalType":"uint256","name":"nonce","type":"uint256"}],"name":"depositCancelRequest","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"l2Recipient","type":"uint256"},{"internalType":"uint256","name":"nonce","type":"uint256"}],"name":"depositReclaim","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"identify","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"bytes","name":"data","type":"bytes"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"isActive","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"isFrozen","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"isGovernor","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"maxDeposit","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"maxTotalBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"newGovernor","type":"address"}],"name":"nominateNewGovernor","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"governorForRemoval","type":"address"}],"name":"removeGovernor","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"l2TokenBridge_","type":"uint256"}],"name":"setL2TokenBridge","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"maxDeposit_","type":"uint256"}],"name":"setMaxDeposit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"maxTotalBalance_","type":"uint256"}],"name":"setMaxTotalBalance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"}]

    def __init__(self, account: BaseAccount, recipient: str):
        self.account = account
        self.recipient = recipient

    async def get_fee_for_starkgate(self, amount: int):
        while True:
            try:
                r = await req_post("https://alpha-mainnet.starknet.io/feeder_gateway/estimate_message_fee?blockNumber=pending",
                                data= json.dumps({"from_address":"993696174272377493693496825928908586134624850969",
                                        "to_address":"0x073314940630fd6dcda0d772d4c972c4e0a9946bef9dabf4ef84eda8ef542b82",
                                        "entry_point_selector":"0x2d757788a8d8d6f21d1cd40bce38a8222d70654214e96ff95d8086e684fbee5",
                                        "payload":
                                        [self.recipient,
                                        hex(amount),
                                        "0x0"]}),
                                    headers={
                                        "Content-type": "application/json"
                                    })

                return r["overall_fee"]
            
            except Exception as e:
                logger.error(f"[{self.account.evm_address}] can't get starkgate fees: {e}. Trying again")
                await sleeping(self.account.evm_address, True)


    async def bridge_to_stark(self, amount: float):
        w3 = self.account.get_w3("ethereum")
        txn_data_handler = TxnDataHandler(self.account, "ethereum", w3=w3)

        fee = await self.get_fee_for_starkgate(int(amount*1e18))/1e18

        balance = (await self.account.get_balance_evm(eth_ethereum))[1]
        amount = amount-fee
        if balance < amount+fee:
            logger.error(f"[{self.account.evm_address}] not enough ETH for bridge ")
            return -1, ""
        
        contract = w3.eth.contract(self.contract_address, abi=self.ABI)


        
        txn = await contract.functions.deposit(
            int(amount*1e18),
            int(self.recipient, 16)
        ).build_transaction(await txn_data_handler.get_txn_data(int(amount*1e18)))

        
        return txn
        
