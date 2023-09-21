from BaseClasses import *

async def own_tasks(self):
    tasks = SETTINGS["own_tasks"]
    self.delay = 0
    shuffle(tasks)
    for task in tasks:
        if type(task) == type([1,2,3]):
            for task2 in task:
                self.task_number = task2
                await self.start()
        else:
            self.task_number = task
            await self.start()

