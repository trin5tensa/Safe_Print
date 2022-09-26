"""intg_test.py
Created with Python 3.10. Sept 2022
"""
import asyncio
import functools
import itertools
import queue
import threading
import time
import tkinter as tk
import tkinter.ttk as ttk
from collections.abc import Iterator
from typing import Optional

from threadsafe_printer import SafePrint


TASK_ID_ITR = itertools.count(1)
PRINT_Q = queue.Queue()

# Global reference to loop allows access from different environments.
aio_loop: Optional[asyncio.AbstractEventLoop] = None


def io_blocker(tk_q: queue.Queue, block: float = 0):
    """ Block the thread and put a 'Hello World' work package into Tkinter's work queue.
    
    This is a producer for Tkinter's work queue. It will run in a special thread created solely for running this
    function.
    """
    safeprint(f'io_blocker starting. {block=}s.')
    time.sleep(block)

    task_id = next(TASK_ID_ITR)
    work_package = f"Task #{task_id} {block}s: 'Hello Threading World'."
    tk_q.put(work_package)
    safeprint(f'io_blocker ending. {block=}s.')


async def aio_blocker(tk_q: queue.Queue, block: float = 0):
    """ Asynchronously block and put a 'Hello World' work package into Tkinter's work queue.
    
    This is a producer for Tkinter's work queue. It will run in the same thread as the asyncio loop.
    """
    safeprint(f'aio_blocker starting. {block=}s.')
    await asyncio.sleep(block)
    
    task_id = next(TASK_ID_ITR)
    work_package = f"Task #{task_id} {block}s: 'Hello Asynchronous World'."
    
    while True:
        try:
            # Asyncio can't wait for the thread blocking `put` method…
            tk_q.put_nowait(work_package)
            
        except queue.Full:
            # Give control back to asyncio's loop.
            await asyncio.sleep(0)
            
        else:
            # The work package has been placed in the queue so we're done.
            break

    safeprint(f'aio_blocker ending. {block=}s.')


def tk_callback_consumer(tk_q: queue.Queue, mainframe: ttk.Frame, row_itr: Iterator):
    """ Display queued 'Hello world' messages in the Tkinter window.

    This is the consumer for Tkinter's work queue. It runs in the Main Thread.
    
    Returns:
        Never. After starting, it runs continuously until the GUI is closed by the user.
    """
    # Assume a full queue and poll continuously.
    poll_interval = 0
    
    try:
        # Tkinter can't wait for the thread blocking `get` method…
        work_package = tk_q.get_nowait()

    except queue.Empty:
        # …so be prepared for an empty queue and slow the polling rate.
        poll_interval = 40

    else:
        # Process a work package.
        label = ttk.Label(mainframe, text=work_package)
        label.grid(column=0, row=(next(row_itr)), sticky='w', padx=10)

    finally:
        # Have tkinter call this function again after the poll interval.
        mainframe.after(poll_interval, functools.partial(tk_callback_consumer, tk_q, mainframe, row_itr))


def tk_callbacks(mainframe: ttk.Frame, row_itr: Iterator):
    """ 'Hello world' callbacks.

    This runs in the Main Thread.
    """
    safeprint('tk_callbacks starting')
    
    # Create the job queue and start its consumer.
    tk_q = queue.Queue()
    safeprint('tk_callback_consumer starting')
    tk_callback_consumer(tk_q, mainframe, row_itr)

    # Schedule the asyncio blocker.
    for block in [1.1, 3.1]:
        asyncio.run_coroutine_threadsafe(aio_blocker(tk_q, block), aio_loop)
    
    # Run the thread blocker.
    for block in [1.2, 3.2]:
        threading.Thread(target=io_blocker, args=(tk_q, block)).start()
        
    safeprint('tk_callbacks ending - All blocking callbacks have been scheduled.')


def tk_main():
    """ Run tkinter.

    This runs in the Main Thread.
    """
    safeprint('tk_main starting\n')
    row_itr = itertools.count()
    
    # Create the Tk root and mainframe.
    root = tk.Tk()
    mainframe = ttk.Frame(root, padding="15 15 15 15")
    mainframe.grid(column=0, row=0)
    
    # Add a _close button
    button = ttk.Button(mainframe, text='Shutdown', command=root.destroy)
    button.grid(column=0, row=next(row_itr), sticky='w')
    
    # Add an information widget.
    label = ttk.Label(mainframe, text=f'\nWelcome to hello_world*4.py.\n')
    label.grid(column=0, row=next(row_itr), sticky='w')
    
    # Schedule the 'Hello World' callbacks
    root.after(0, functools.partial(tk_callbacks, mainframe, row_itr))
    
    # The asyncio loop must start before the tkinter event loop.
    while not aio_loop:
        time.sleep(0)
    
    root.mainloop()
    safeprint(' ', timestamp=False)
    safeprint('tk_callback_consumer ending')
    safeprint('tk_main ending')


async def manage_aio_loop(aio_initiate_shutdown: threading.Event):
    """ Keep the loop running until the shutdown event is signalled.

    This runs in Asyncio's thread and in asyncio's loop.
    """
    safeprint('manage_aio_loop starting')
    
    # Tkinter needs to know about the asyncio loop. A global variable is the easiest way to communicate this.
    global aio_loop
    aio_loop = asyncio.get_running_loop()
    
    # The usual wait command — Event.wait() — would block the current thread and the asyncio loop.
    while not aio_initiate_shutdown.is_set():
        await asyncio.sleep(0)
        
    safeprint('manage_aio_loop ending')


def aio_main(aio_initiate_shutdown: threading.Event):
    """ Start the asyncio loop.

    This non-coroutine function runs in Asyncio's thread.
    """
    safeprint('aio_initiate_shutdown starting')
    asyncio.run(manage_aio_loop(aio_initiate_shutdown))
    safeprint('aio_initiate_shutdown ending')


def main():
    """Set up working environments for asyncio and tkinter.

    This runs in the Main Thread.
    """
    safeprint('main starting')

    # Start the asyncio permanent loop in a new thread.
    # aio_shutdown is signalled between threads. `asyncio.Event()` is not threadsafe.
    aio_initiate_shutdown = threading.Event()
    aio_thread = threading.Thread(target=aio_main, args=(aio_initiate_shutdown,), name="Asyncio's Thread")
    aio_thread.start()
    
    tk_main()
    
    # Close the asyncio permanent loop and join the thread in which it runs.
    aio_initiate_shutdown.set()
    aio_thread.join()
    
    safeprint('main ending')


if __name__ == '__main__':
    with SafePrint() as safeprint:
        main()
 