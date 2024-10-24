import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor


class AsyncThreadsafeSemaphore:
    """
    A threadsafe version of asyncio.Semaphore that can be used in async and sync contexts.
    """

    def __init__(self, value: int = 1):
        self._semaphore = threading.Semaphore(value)
        self._executor = ThreadPoolExecutor()

    # Context manager methods for synchronous usage
    def __enter__(self):
        self._acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    # Async context manager methods for asynchronous usage
    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def release(self):
        self._semaphore.release()

    async def acquire(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._executor, self._acquire)

    def _acquire(self):
        self._semaphore.acquire()
