from .own_tasks import *
data = {
    1 : [],
    2 : [],
    3 : [],
    4 : [],
    5 : [],
    6 : [],
    7 : [],
    8 : [],
    9 : [],
    10 : [],
}
class qwe:
    task_number = 0
    def __init__(self, i) -> None:
        self.i = i
    async def start(self):
        task_number = self.task_number
        if task_number == 1:
            pass
        elif task_number == 2:
            await self.swaps_handler()
        elif task_number == 0:
            await own_tasks(self)
        elif task_number == 3:
            await self.swap_to_one_token()
        elif task_number == 4:
            await self.liq_handler()
        elif task_number == 5:
            await self.remove_liq()
        elif task_number == 7:
            await self.full()
        elif task_number == 8:
            await self.withdraw()
        elif task_number == 9:
            pass
        elif task_number == 13:
            await self.deployer()
        elif task_number == 16:
            await self.stats()
        elif task_number == 17:
            await self.lend_router()
        elif task_number == 18:
            await self.remove_from_lend()
        elif task_number == 22:
            await self.withdraw(addr_dict[self.account.formatted_hex_address])
        elif task_number == 23:
            await self.dmail()
        elif task_number == 24:
            await self.stark_id()
        elif task_number == 26:
            await self.full_withdraw()
        elif task_number == 27:
            await self.full_withdraw(addr_dict[self.account.formatted_hex_address])
        elif task_number == 28:
            await self.collateral()
        elif task_number == 29:
            await self.braavos_upgrader()
        elif task_number == 30:
            await self.return_borrowed()
        elif task_number == 31:
            await self.argent_upgrader()
        elif task_number == 32:
            await self.new_id()
        elif task_number == 33:
            await self.okx()
        elif task_number == 34:
            await self.bids(True)
        elif task_number == 35:
            await self.bids(False)

    async def bids(self, flex):
        for i in range(get_random_value_int(SETTINGS["bids_amount"])):
            print(f"{self.i}: bid")
            data[self.i].append("bid")
            await asyncio.sleep(1)
    async def liq_handler(self):
        print(f"{self.i}: liq")
        data[self.i].append("liq")
        await asyncio.sleep(1)


    async def remove_liq(self):
        print(f"{self.i}: remove liq")
        data[self.i].append("remove liq")
        await asyncio.sleep(1)


    async def swap_to_one_token(self):
        print(f"{self.i}: swap")
        data[self.i].append("swap")
        await asyncio.sleep(1)

    async def dmail(self):
        print(f"{self.i}: dmail")
        data[self.i].append("dmail")
        await asyncio.sleep(1)

tasks = []
loop = asyncio.new_event_loop()
for i in range(10):
    tasks.append(loop.create_task(qwe(i+1).start()))

loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))
print(json.dumps(data, indent=12))


