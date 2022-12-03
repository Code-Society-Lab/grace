import asyncio
from abc import ABCMeta
from datetime import timedelta
from typing import Any

from discord.ui import View


class TimedView(View, metaclass=ABCMeta):
    """

    """
    def __init__(self, seconds: int = 900):
        super().__init__()
        self.__seconds: int = seconds
        self.__running: bool = True

    @property
    def seconds(self) -> int:
        """Returns the seconds until the end of the timer

        :return: The seconds until the end of the timer
        :rtype: int
        """
        return self.__seconds

    @property
    def time(self):
        return str(timedelta(seconds=self.seconds))

    def start_timer(self):
        """Starts the timer task"""
        asyncio.create_task(self.__timer_task())

    async def __timer_task(self):
        while self.seconds > 0:
            await self.on_timer()

            self.__seconds -= 1
            await asyncio.sleep(1)
        await self.on_timer_finished()

    async def on_timer(self) -> Any:
        """A callback that is called at each countdown update"""
        pass

    async def on_timer_finished(self) -> Any:
        """A callback that is called when the timer's time elapses.

        This method has to be overriden by each child of the class.

        :raises NotImplementedError: Timed view need
        """
        raise NotImplementedError("Timed view need to implement `on_timer_finished`.")
