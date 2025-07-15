"""Module for the base class of uploader API endpoints."""

from threading import Thread


class UploaderBase:
    """Base class for uploader API endpoints."""

    def __init__(self):
        """
        Initialize the UploaderBase.
        """
        self._background_threads = []

    def _prune_background_threads(self) -> list[Thread]:
        """
        Prune background threads that are no longer running.

        Returns
        -------
        list[Thread]
            A list of background threads that are still alive.
        """
        tmp_background_threads = []
        for thread in self._background_threads:
            if not thread.is_alive():
                thread.join()
            else:
                tmp_background_threads.append(thread)
        self._background_threads = tmp_background_threads
