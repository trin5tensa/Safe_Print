"""safeprint.py"""
import asyncio
import queue
import threading
import time
from typing import Callable, Optional


# Used by get_timestamp to measure elapsed time.
_TIME_0 = time.perf_counter()
PRINT_Q = queue.Queue()

_print_thread: Optional[threading.Thread] = None


def get_timestamp() -> str:
    """Create a timestamp with useful status information.
    
    This is a support function for the print queue producers. It runs in the same thread as the producer.
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
    return f'{secs:.3f}s  In {threading.current_thread().name} of {threading.active_count()} with {loop_name}  --- '


def start():
    """ Start the print queue.
    
    Returns:
        print queue
        timestamp
    """
    global _print_thread
    _print_thread = threading.Thread(target=_print_queue_consumer, name='Print Thread')
    _print_thread.start()


def close(msg: str = None):
    """ Close the print queue.
    
    Add final messages to the print queue. Join the thread in which it runs.
    
    Args:
        msg: Closedown message
    """
    if msg:
        PRINT_Q.put(f'{get_timestamp()} {msg}')
    PRINT_Q.put(None)
    _print_thread.join()


def _print_queue_consumer():
    """Consume and print tasks from the print queue.

    The print statement is not threadsafe, so it must run in its own thread.
    """
    queue_size = len(PRINT_Q.queue)
    print(f'{get_timestamp()} _print_queue_consumer is about to start with {queue_size} item(s) already in queue.')
    while True:
        msg = PRINT_Q.get()
        
        # Exit function when any producer function places 'None' into the queue.
        if not msg:
            break
        else:
            print(msg)
    print(f'{get_timestamp()} _print_queue_consumer is ending.')


def main():
    """Set up working environments for asyncio, tkinter, and printing.

    This runs in the Main Thread
    """
    PRINT_Q.put(f'{get_timestamp()} main() starting.')
    start()
    
    PRINT_Q.put(f'{get_timestamp()} Off doing some main programmy stuff.')
    time.sleep(0.5)
    
    # Add final messages to the print queue. Join the thread in which it runs.
    close(f'main() ending.')


if __name__ == '__main__':
    main()
