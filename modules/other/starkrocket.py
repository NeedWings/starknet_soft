from aiohttp import ClientSession
from starknet_py.net.client_models import Call

from modules.base_classes.base_account import BaseAccount
from modules.utils.utils import sleeping
from modules.utils.logger import logger

class StarkRocket:
    def __init__(self, account: BaseAccount) -> None:
        self.account = account

    async def get_proof(self):
        while True:
            try:
                session: ClientSession = self.account.session
                async with session.request("GET", f"https://starkrocket.xyz/api/get_proof?address={self.account.stark_address}", headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}) as resp:
                    data = await resp.json()
                    return data["result"]["proof"]
            except Exception as e:
                logger.error(f"[{self.account.stark_address}] got error: {e}")
                await sleeping(self.account.stark_address)
    
    async def get_points(self):
        while True:
            try:
                session: ClientSession = self.account.session
                async with session.request("GET", f"https://starkrocket.xyz/api/check_wallet?address={self.account.stark_address}", headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}) as resp:
                    data = await resp.json()
                    return int(data["result"]["points"])
            except Exception as e:
                logger.error(f"[{self.account.stark_address}] got error: {e}")
                await sleeping(self.account.stark_address)

    async def get_txn(self, ref = "0x3c86520094a9c74c6c88b6e41711cb2f51b68edee8a8a9aa5fffcbc5ae336b8"):
        proof = list(map(lambda x: int(x, 16), await self.get_proof()))
        points = await self.get_points()
        call = Call(
            to_addr=0x01c50d0cd1ee43c43e0d9059cb707bfabe532564431fe8badb9c8b79ef928bed,
            selector=0xb758361d5e84380ef1e632f89d8e76a8677dbc3f4b93a4f9d75d2a6048f312,
            calldata=[
                points,
                len(proof),
                *proof,
                int(ref, 16)
            ]
        )

        return [call]


