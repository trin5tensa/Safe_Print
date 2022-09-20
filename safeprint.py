"""safeprint.py"""
import asyncio
import queue
import threading
import time
from contextlib import AbstractContextManager
from types import TracebackType
from typing import Type


# Used by _timestamp to measure elapsed time.
_TIME_0 = time.perf_counter()
_PRINT_Q = queue.Queue()

_print_thread: threading.Thread | None = None


def start():
    """ Start the print queue.
    
    Returns:
        print queue
        timestamp
    """
    global _print_thread
    _print_thread = threading.Thread(target=_safe_print_consumer, name='Print Thread')
    _print_thread.start()


def safeprint(msg: str, timestamp: bool = True, reset: bool = False):
    """Print a string on stdout from an exclusive Print Thread.
    
    The exclusive thread and a threadsafe print queue ensure race free printing.
    This is the producer in the print queue's producer/consumer pattern.
    It runs in the same thread as the calling function
    
    Args:
        msg: The message to be printed.
        timestamp: Print a timestamp (Default = True).
        reset: Reset the time to zero (Default = False).
    """
    if reset:
        global _TIME_0
        _TIME_0 = time.perf_counter()
    if timestamp:
        _PRINT_Q.put(f'{_timestamp()} --- {msg}')
    else:
        _PRINT_Q.put(msg)


def close():
    """ Close the print queue. Join the thread in which it runs.
    """
    _PRINT_Q.put(None)
    _print_thread.join()


class SafePrint(AbstractContextManager):
    def __enter__(self):
        start()
        return safeprint
        
    def __exit__(self, __exc_type: Type[BaseException] | None, __exc_value: BaseException | None,
                 __traceback: TracebackType | None) -> bool | None:
        close()
        return False


def _safe_print_consumer():
    """Consume and print tasks from the print queue.

    The print statement is not threadsafe, so it must run in its own thread.
    This is the consumer in the print queue's producer/consumer pattern.
    """
    print(f'{_timestamp()}: The Safeprinter is open for output.')
    while True:
        msg = _PRINT_Q.get()
        
        # Exit function when any producer function places 'None' into the queue.
        if msg:
            print(msg)
        else:
            break
    print(f'{_timestamp()}: The Safeprinter has closed.')


def _timestamp() -> str:
    """Create a timestamp with useful status information.

    This is a support function for the print queue producers. It runs in the same thread as the calling function.
    Consequently, the returned data does not cross between threads.

    Returns:
        timestamp
    """
    secs = time.perf_counter() - _TIME_0
    try:
        asyncio.get_running_loop()
    except RuntimeError as exc:
        if exc.args[0] == 'no running event loop':
            loop_name = exc.args[0]
        else:
            raise
    else:
        loop_name = 'the asyncio loop'
    return f'{secs:.3f}s  In {threading.current_thread().name} of {threading.active_count()} with {loop_name}'


def main():
    """Set up working environments for asyncio, tkinter, and printing.

    This runs in the Main Thread
    """
    _PRINT_Q.put(f'{_timestamp()} main() starting.')
    start()
    
    _PRINT_Q.put(f'{_timestamp()} Off doing some main programmy stuff.')
    time.sleep(0.5)
    
    # Add final messages to the print queue. Join the thread in which it runs.
    close()


if __name__ == '__main__':
    main()
