from asyncio import Event, sleep
from random import choice

from modules.utils.account import Account
from modules.routers.activity.own_tasks_router import OwnTasks
from modules.routers.activity.swaps_handler import SwapsHandler
from modules.routers.activity.liquidity_handler import LiquidityHandler
from modules.routers.activity.lending_handler import LendingHandler
from modules.routers.activity.other_handler import OtherHandler, ARGENT, BRAAVOS
from modules.routers.bridge.bridge_router import BridgeRouter, ORBITER_BRIDGE, ORBITER_WITHDRAW, STARKGATE
from modules.routers.bridge.OKX_helper import OKXHelper
from modules.other.stats import stat
from modules.utils.logger import logger
from modules.utils.utils import get_pair_for_address_from_file
from modules.config import SETTINGS

class MainRouter():
    def __init__(self, private_key: str, delay: int, task_number: int, proxy=None) -> None:
        self.task_number = task_number

        self.account = Account(private_key, proxy=proxy)
        self.delay = delay

    
    async def start(self, gas_lock: Event = None, one_thread_lock: Event = None):
        one_thread_mode = SETTINGS["one thread mode"]
        if not self.account.is_set:
            await self.account.setup_account()
        if self.delay != 0:
            for i in range(100):
                await sleep(self.delay/100)
                while gas_lock.is_set() or one_thread_lock.is_set():
                    await sleep(10)
        
        if one_thread_mode and one_thread_lock is not None:
            one_thread_lock.set()

        if self.task_number == 110:
            bridger = BridgeRouter(self.account, self.account.stark_address)
            await bridger.bridge(STARKGATE)

        elif self.task_number == 111:
            rec = get_pair_for_address_from_file("EVM_stark_pairs.txt", self.account.evm_address)
            if rec is None:
                logger.error(f"[{self.account.evm_address}] can't find pair. Skip")
                if one_thread_mode and one_thread_lock:
                    one_thread_lock.clear()
                return
            bridger = BridgeRouter(self.account, rec)
            await bridger.bridge(STARKGATE)

        elif self.task_number == 120:
            bridger = BridgeRouter(self.account, self.account.stark_address)
            await bridger.bridge(ORBITER_BRIDGE)

        elif self.task_number == 121:
            rec = get_pair_for_address_from_file("EVM_stark_pairs.txt", self.account.evm_address)
            if rec is None:
                logger.error(f"[{self.account.evm_address}] can't find pair. Skip")
                if one_thread_mode and one_thread_lock:
                    one_thread_lock.clear()
                return
            bridger = BridgeRouter(self.account, rec)
            await bridger.bridge(ORBITER_BRIDGE)

        elif self.task_number == 130:
            bridger = BridgeRouter(self.account, self.account.evm_address)
            await bridger.bridge(ORBITER_WITHDRAW)

        elif self.task_number == 131:
            rec = get_pair_for_address_from_file("EVM_stark_pairs.txt", self.account.stark_address)
            if rec is None:
                logger.error(f"[{self.account.stark_address}] can't find pair. Skip")
                if one_thread_mode and one_thread_lock:
                    one_thread_lock.clear()
                return
            bridger = BridgeRouter(self.account, rec)
            await bridger.bridge(ORBITER_WITHDRAW)

        elif self.task_number == 21:
            swap_handler = SwapsHandler(self.account)
            await swap_handler.random_swaps()
       
        elif self.task_number == 22:
            swap_handler = SwapsHandler(self.account)
            await swap_handler.save_assets(choice(SETTINGS["toSaveFunds"]))

        elif self.task_number == 31:
            liquidity_handler = LiquidityHandler(self.account)
            await liquidity_handler.add_liq()

        elif self.task_number == 32:
            liquidity_handler = LiquidityHandler(self.account)
            await liquidity_handler.remove_liq()
        
        elif self.task_number == 41:
            lend_handler = LendingHandler(self.account)
            await lend_handler.lend_actions()

        elif self.task_number == 42:
            lend_handler = LendingHandler(self.account)
            await lend_handler.remove_from_lend()

        elif self.task_number == 43:
            lend_handler = LendingHandler(self.account)
            await lend_handler.return_borrowed()

        elif self.task_number == 44:
            lend_handler = LendingHandler(self.account)
            await lend_handler.collateral()

        elif self.task_number == 51:
            other_handler = OtherHandler(self.account)
            await other_handler.dmail()

        elif self.task_number == 52:
            other_handler = OtherHandler(self.account)
            await other_handler.starkstars()
        
        elif self.task_number == 53:
            other_handler = OtherHandler(self.account)
            await other_handler.starknet_id()

        elif self.task_number == 541:
            other_handler = OtherHandler(self.account)
            await other_handler.bids(1)

        elif self.task_number == 542:
            other_handler = OtherHandler(self.account)
            await other_handler.bids(2)

        elif self.task_number == 543:
            other_handler = OtherHandler(self.account)
            await other_handler.bids(3)

        elif self.task_number == 551:
            other_handler = OtherHandler(self.account)
            await other_handler.upgrade(ARGENT)

        elif self.task_number == 552:
            other_handler = OtherHandler(self.account)
            await other_handler.upgrade(BRAAVOS)
        
        elif self.task_number == 56:
            other_handler = OtherHandler(self.account)
            await other_handler.deployer()

        elif self.task_number == 61:
            api_key = SETTINGS["api_key"]
            secret = SETTINGS["secret"]
            password = SETTINGS["password"]
            okx_helper = OKXHelper(api_key, secret, password, self.account)
            await okx_helper.withdraw_handl()
        
        elif self.task_number == 62:
            api_key = SETTINGS["api_key"]
            secret = SETTINGS["secret"]
            password = SETTINGS["password"]
            okx_helper = OKXHelper(api_key, secret, password, self.account)
            await okx_helper.deposit_handl()

        elif self.task_number == 71:
            await stat(self.account)

        elif self.task_number == 0:
            own_tasks_router = OwnTasks(self.account)
            await own_tasks_router.main(self)

        
        if one_thread_mode and one_thread_lock:
            one_thread_lock.clear()
    