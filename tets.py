import asyncio
import random
import requests

prices = {
    "USDT": 0,
    "DAI": 0,
    "ETH": 0
}
l = ["USDT", "DAI", "ETH"]

cb = {
    "USDT": "",
    "DAI": "",
    "ETH": ""
}
async def pricer():
    while True:
        for t in l:
            prices["USDT"] += random.uniform(0.1, 10)
            prices["DAI"] += random.uniform(0.1, 10)
            prices["ETH"] += random.uniform(0.1, 10)
        await asyncio.sleep(1)

async def shower():
    while True:
        t = random.choice(l)
        print(f"{t}: {prices[t]}")
        await asyncio.sleep(random.randint(1,3))

loop = asyncio.new_event_loop()
tasks = []
tasks.append(loop.create_task(pricer()))
tasks.append(loop.create_task(shower()))
tasks.append(loop.create_task(shower()))
tasks.append(loop.create_task(shower()))
tasks.append(loop.create_task(shower()))

loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED))


