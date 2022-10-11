""" tkinter_demo.py

Created with Python 3.10
"""
#  Copyright (c) 2022-2022. Stephen Rigden.
#  Last modified 10/11/22, 8:44 AM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import concurrent.futures
import functools
import itertools
import queue
import sys
import threading
import time
import tkinter as tk
import tkinter.ttk as ttk
from collections.abc import Iterator
from typing import Optional

from threadsafe_printer import SafePrinter


TASK_ID_ITR = itertools.count(1)

# Global reference to loop allows access from different environments.
aio_loop: Optional[asyncio.AbstractEventLoop] = None


def io_blocker(tk_q: queue.Queue, block: float = 0) -> None:
    """ Block the thread and put a 'Hello World' work package into Tkinter's work queue.
    
    This is a producer for Tkinter's work queue. It will run in a special thread created solely for running this
    function. The statement `time.sleep(block)` can be replaced with any non-awaitable blocking code.
    
    
    Args:
        tk_q: tkinter's work queue.
        block: block time
        
    Returns:
        Nothing. The work package is returned via the threadsafe tk_q.
    """
    safeprint(f'io_blocker starting. {block=}s.')
    time.sleep(block)

    # Exceptions for testing handlers. Uncomment these to see what happens when exceptions are raised.
    # raise IOError('Just testing an expected error.')
    # raise ValueError('Just testing an unexpected error.')

    task_id = next(TASK_ID_ITR)
    work_package = f"Task #{task_id} {block}s: 'Hello Threading World'."
    tk_q.put(work_package)
    safeprint(f'io_blocker ending. {block=}s.')
    
    
def io_exception_handler(tk_q: queue.Queue, block: float = 0) -> None:
    """ Exception handler for non-awaitable blocking callback.
    
    It will run in a special thread created solely for running io_blocker.
    
    Args:
        tk_q: tkinter's work queue.
        block: block time
    """
    safeprint(f'io_exception_handler starting. {block=}s.')
    try:
        io_blocker(tk_q, block)
    except IOError as exc:
        safeprint(f'io_exception_handler: {exc!r} was handled correctly. ')
    finally:
        safeprint(f'io_exception_handler ending. {block=}s.')


async def aio_blocker(tk_q: queue.Queue, block: float = 0) -> None:
    """ Asynchronously block the thread and put a 'Hello World' work package into Tkinter's work queue.
    
    This is a producer for Tkinter's work queue. It will run in the same thread as the asyncio loop. The statement
    `await asyncio.sleep(block)` can be replaced with any awaitable blocking code.
    
    Args:
        tk_q: tkinter's work queue.
        block: block time

    Returns:
        Nothing. The work package is returned via the threadsafe tk_q.
    """
    safeprint(f'aio_blocker starting. {block=}s.')
    await asyncio.sleep(block)

    # Exceptions for testing handlers. Uncomment these to see what happens when exceptions are raised.
    # raise IOError('Just testing an expected error.')
    # raise ValueError('Just testing an unexpected error.')
    
    task_id = next(TASK_ID_ITR)
    work_package = f"Task #{task_id} {block}s: 'Hello Asynchronous World'."
    
    # Put the work package into the tkinter's work queue.
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


def aio_exception_handler(mainframe: ttk.Frame, future: concurrent.futures.Future, block: float,
                          first_call: bool = True) -> None:
    """ Exception handler for future coroutine callbacks.
    
    This non-coroutine function uses tkinter's event loop to wait for the future to finish.
    It runs in the Main Thread.

    Args:
        mainframe: The after method of this object is used to poll this function.
        future: The future running the future coroutine callback.
        block: The block time parameter used to identify which future coroutine callback is being reported.
        first_call: If True will cause an opening line to be printed on stdout.
    """
    if first_call:
        safeprint(f'aio_exception_handler starting. {block=}s')
    poll_interval = 100  # milliseconds
    
    try:
        # Python will not raise exceptions during future execution until `future.result` is called. A zero timeout is
        # required to avoid blocking the thread.
        future.result(0)
    
    # If the future hasn't completed, reschedule this function on tkinter's event loop.
    except concurrent.futures.TimeoutError:
        mainframe.after(poll_interval, functools.partial(aio_exception_handler, mainframe, future, block,
                                                         first_call=False))
    
    # Handle an expected error.
    except IOError as exc:
        safeprint(f'aio_exception_handler: {exc!r} was handled correctly. ')
    
    else:
        safeprint(f'aio_exception_handler ending. {block=}s')


def tk_callback_consumer(tk_q: queue.Queue, mainframe: ttk.Frame, row_itr: Iterator):
    """ Display queued 'Hello world' messages in the Tkinter window.

    This is the consumer for Tkinter's work queue. It runs in the Main Thread. After starting, it runs
    continuously until the GUI is closed by the user.
    """
    # Poll continuously while queue has work needing processing.
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
    """ Set up 'Hello world' callbacks.

    This runs in the Main Thread.
    
    Args:
        mainframe: The mainframe of the GUI used for displaying results from the work queue.
        row_itr: A generator of line numbers for displaying items from the work queue.
    """
    safeprint('tk_callbacks starting')
    
    # Create the job queue and start its consumer.
    tk_q = queue.Queue()
    safeprint('tk_callback_consumer starting')
    tk_callback_consumer(tk_q, mainframe, row_itr)

    # Schedule the asyncio blocker.
    for block in [1.1, 3.1]:
        # This is not an asyncio.Future because they are not threadsafe. Also, they do not have a wait with timeout
        # which we shall need.
        future: concurrent.futures.Future = asyncio.run_coroutine_threadsafe(aio_blocker(tk_q, block), aio_loop)

        # Can't use Future.add_done_callback here. It doesn't return until the future is done and that would block
        # tkinter's event loop.
        aio_exception_handler(mainframe, future, block)
        
    # Run the thread blocker.
    for block in [1.2, 3.2]:
        threading.Thread(target=io_exception_handler, args=(tk_q, block), name=f'IO Block Thread ({block}s)').start()

    safeprint('tk_callbacks ending - All blocking callbacks have been scheduled.\n')


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
    
    # Add a close button
    button = ttk.Button(mainframe, text='Shutdown', command=root.destroy)
    button.grid(column=0, row=next(row_itr), sticky='w')
    
    # Add an information widget.
    label = ttk.Label(mainframe, text=f'\nWelcome to hello_world*4.py.\n')
    label.grid(column=0, row=next(row_itr), sticky='w')
    
    # Schedule the 'Hello World' callbacks
    mainframe.after(0, functools.partial(tk_callbacks, mainframe, row_itr))
    
    # The asyncio loop must start before the tkinter event loop.
    while not aio_loop:
        time.sleep(0)
    
    root.mainloop()
    safeprint(' ', timestamp=False)
    safeprint('tk_callback_consumer ending')
    safeprint('tk_main ending')


async def manage_aio_loop(aio_initiate_shutdown: threading.Event):
    """ Run the asyncio loop.
    
    This provides an always available asyncio service for tkinter to make any number of simultaneous blocking IO
    calls. 'Any number' includes zero.

    This runs in Asyncio's thread and in asyncio's loop.
    """
    safeprint('manage_aio_loop starting')
    
    # Communicate the asyncio loop status to tkinter via a global variable.
    global aio_loop
    aio_loop = asyncio.get_running_loop()
    
    # If there are no awaitables left in the queue asyncio will close.
    # The usual wait command — Event.wait() — would block the current thread and the asyncio loop.
    while not aio_initiate_shutdown.is_set():
        await asyncio.sleep(0)
    
    safeprint('manage_aio_loop ending')


def aio_main(aio_initiate_shutdown: threading.Event):
    """ Start the asyncio loop.

    This non-coroutine function runs in Asyncio's thread.
    """
    safeprint('aio_main starting')
    asyncio.run(manage_aio_loop(aio_initiate_shutdown))
    safeprint('aio_main ending')


def main():
    """Set up working environments for asyncio and tkinter.

    This runs in the Main Thread.
    """
    safeprint('main starting')

    # Start the permanent asyncio loop in a new thread.
    # aio_shutdown is signalled between threads. `asyncio.Event()` is not threadsafe.
    aio_initiate_shutdown = threading.Event()
    aio_thread = threading.Thread(target=aio_main, args=(aio_initiate_shutdown,), name="Asyncio's Thread")
    aio_thread.start()
    
    tk_main()
    
    # Close the asyncio permanent loop and join the thread in which it runs.
    aio_initiate_shutdown.set()
    # aio_thread.join()
    
    safeprint('main ending')


if __name__ == '__main__':
    with SafePrinter() as safeprint:
        sys.exit(main())
 