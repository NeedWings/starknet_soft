from random import shuffle, choice

from modules.base_classes.base_account import BaseAccount
from modules.config import SETTINGS

class OwnTasks:

    modes = {
        "standart": 1,
        "invert": -1
    }

    def __init__(self, account: BaseAccount) -> None:
        self.account = account

    async def main(self, main_router, tasks = None, mode = None):
        if mode:
            mode = 0-mode
        else:
            mode = self.modes[SETTINGS["own tasks mode"]]

        if mode == 1:

            if not tasks:
                tasks = SETTINGS["own tasks"].copy()
                shuffle(tasks)
            for task in tasks:
                if isinstance(task, list):
                    await self.main(main_router, tasks = task, mode = mode)
                elif isinstance(task, str):
                    to_do = int(choice(task.split(",")))
                    main_router.delay = 0
                    main_router.task_number = to_do
                    await main_router.start()
                else:
                    main_router.delay = 0
                    main_router.task_number = task
                    await main_router.start()
        elif mode == -1:
            if not tasks:
                tasks = SETTINGS["own tasks"].copy()
            for task in tasks:
                if isinstance(task, list):
                    shuffle(task)
                    await self.main(main_router, tasks = task, mode=mode)
                elif isinstance(task, str):
                    to_do = int(choice(task.split(",")))
                    main_router.delay = 0
                    main_router.task_number = to_do
                    await main_router.start()
                else:
                    main_router.delay = 0
                    main_router.task_number = task
                    await main_router.start()