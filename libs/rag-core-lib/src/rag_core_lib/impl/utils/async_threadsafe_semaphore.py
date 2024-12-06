"""Module containing the AsyncThreadsafeSemaphore class."""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Type


class AsyncThreadsafeSemaphore:
    """A threadsafe version of asyncio.Semaphore that can be used in async and sync contexts."""

    def __init__(self, value: int = 1) -> None:
        """
        Initialize the AsyncThreadsafeSemaphore.

        Parameters
        ----------
        value : int
            The initial value for the semaphore (default 1).
        """
        self._semaphore = threading.Semaphore(value)
        self._executor = ThreadPoolExecutor()

    # Context manager methods for synchronous usage
    def __enter__(self) -> "AsyncThreadsafeSemaphore":
        """Enter the runtime context related to this object."""
        self._acquire()
        return self

    def __exit__(self, *args: Optional[Type[BaseException]]) -> None:
        """Exit the runtime context related to this object."""
        self.release()

    # Async context manager methods for asynchronous usage
    async def __aenter__(self) -> "AsyncThreadsafeSemaphore":
        """Enter the async runtime context related to this object."""
        await self.acquire()
        return self

    async def __aexit__(self, *args: Optional[Type[BaseException]]) -> None:
        """Exit the async runtime context related to this object."""
        self.release()

    def release(self) -> None:
        """
        Release a semaphore, incrementing the internal counter by one.

        This method wakes up one of the threads waiting for the semaphore, if any.

        Returns
        -------
        None
        """
        self._semaphore.release()

    async def acquire(self) -> None:
        """
        Asynchronously acquires a semaphore.

        This method uses the event loop to run the semaphore acquisition in an executor,
        allowing it to be thread-safe.

        Returns
        -------
        None
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._executor, self._acquire)

    def _acquire(self) -> None:
        self._semaphore.acquire()
