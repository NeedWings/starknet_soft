from BaseClasses import *

async def own_tasks(self):
    tasks = SETTINGS["own_tasks"]
    self.delay = 0
    shuffle(tasks)
    for task in tasks:
        if type(task) == type([1,2,3]):
            for task2 in task:
                print(task2)
                self.task_number = task2
                await self.start()
        else:
            print(task)
            self.task_number = task
            await self.start()
    if random.choice(SETTINGS["SwapAtTheEnd"]):
        await self.swap_to_one_token(random.choice(SETTINGS["toSaveFunds"]))

