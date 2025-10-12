from asyncio import sleep as async_sleep, create_task, Task
from datetime import timedelta
from typing import Optional
from discord.ui import View


class TimedView(View):
    """A discord.ui.View class that implements a timer.

    The view will call an event (`on_time_update`)
    each seconds until the timer elapsed.
    Once the timer elapsed, another event (`on_timer_elapsed`) is called.

    :param seconds: The time in seconds to display the view,
    default to 900 seconds (15 minutes).

    :type seconds: int
    """

    def __init__(self, seconds: int = 900):
        super().__init__(timeout=None)

        self.seconds: int = seconds
        self.__timer_task: Optional[Task[None]] = None

    @property
    def seconds(self) -> int:
        """Returns the timer's remaining seconds.

        :return: The remaining seconds
        :rtype: int
        """
        return self.__seconds

    @seconds.setter
    def seconds(self, seconds: int):
        """Change the number of seconds for the timer to elapse.

        :param seconds: The new amount of seconds before the timer elapses
        :type: int
        :raises ValueError: Raised if the given value is lower than 1
        """
        if seconds < 1:
            raise ValueError('Value cannot be lower than 1')

        self.__seconds = seconds

    @property
    def remaining_time(self) -> str:
        """Returns the timer's remaining time in HH:MM:SS.

        :return: The timer's remaining time.
        :rtype: str
        """
        return str(timedelta(seconds=self.seconds))

    def start_timer(self):
        """Starts the view's timer task"""
        self.__timer_task = create_task(
            self.__impl_timer_task(), name=f'grace-timed-view-timer-{self.id}'
        )

    def cancel_timer(self):
        """Cancels the view's timer task"""
        self.__timer_task.cancel()

    async def __impl_timer_task(self):
        while not self.has_time_elapsed():
            await self.on_timer_update()

            self.__seconds -= 1
            await async_sleep(1)
        await self.on_timer_elapsed()

    async def on_timer_update(self):
        """A callback that is called at each timer update.

        This callback does nothing by default but can be
        overriden to change its behaviour.
        """
        pass

    async def on_timer_elapsed(self):
        """A callback that is called when the timer elapsed.

        By default, the callback calls `self.stop()` but can be
        overriden to change its behaviour.
        """
        self.stop()

    def has_time_elapsed(self):
        """Returns true if the time has elapsed

        :returns: True if the time has elapsed or False
        :rtype: bool
        """
        return self.seconds <= 0
