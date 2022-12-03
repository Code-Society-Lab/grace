from asyncio import sleep as async_sleep, create_task, Task
from datetime import timedelta
from typing import Any, Optional
from discord.ui import View


class TimedView(View):
    """A discord.ui.View class that implements a timer.

    The view will call an event (`on_time_update`) each seconds until the timer elapsed. Once the timer elapsed,
    another event (`on_timer_elapsed`) is called.

    :param seconds: The time in seconds to display the view, default to 900 seconds (15 minutes).
    :type seconds: int
    """
    def __init__(self, seconds: int = 900, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__seconds: int = seconds
        self.__timer_task: Optional[Task[None]] = None

    @property
    def seconds(self) -> int:
        """Returns the timer's remaining seconds.

        :return: The remaining seconds
        :rtype: int
        """
        return self.__seconds

    @seconds.setter
    def seconds(self, seconds):
        """Change the number of seconds for the timer to elapse."""
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
        self.__timer_task = create_task(self.__impl_timer_task(), name=f"grace-timed-view-timer-{self.id}")

    def cancel_timer(self):
        """Cancels the view's timer task"""
        self.__timer_task.cancel()

    async def __impl_timer_task(self):
        while self.seconds > 0:
            await self.on_timer_update()

            self.__seconds -= 1
            await async_sleep(1)
        await self.on_timer_elapsed()

    async def on_timer_update(self):
        """A callback that is called at each timer update.

        This callback does nothing by default but can be overriden to change its behaviour.
        """
        pass

    async def on_timer_elapsed(self):
        """A callback that is called when the timer elapsed.

        By default, the callback calls `self.stop()` but can be overriden to change its behaviour.
        """
        self.stop()
