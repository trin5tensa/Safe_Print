# threadsafe_printer

This module `threadsafe_printer` creates a single thread from which all printing will take place. It avoids the race 
conditions which can occur with Python's regular `print` statement. An optional timestamp with useful diagnostic 
information is prefixed. The timer can be reset.

The module was designed to support the coding of programs with multiple threads and an asyncio loop. 


## Context manager

### SafePrint() 
Usage
~~~
import time

from threadsafe_printing import SafePrint


def main():
    safeprint('main starting')
    safeprint('no timestamp', timestamp=False)
    safeprint('going to sleep')
    time.sleep(0.1)
    safeprint('waking up')
    safeprint('resetting the time', reset=True)
    time.sleep(0.05)
    safeprint('main ending')


if __name__ == '__main__':
    with SafePrint() as safeprint:
        main()

~~~

Output

~~~
0.003s In Print Thread of 2 with no running event loop: The Safeprinter is open for output.
0.004s In MainThread of 2 with no running event loop --- main starting
no timestamp
0.004s In MainThread of 2 with no running event loop --- going to sleep
0.109s In MainThread of 2 with no running event loop --- waking up
0.000s In MainThread of 2 with no running event loop --- resetting the time
0.055s In MainThread of 2 with no running event loop --- main ending
0.055s In Print Thread of 2 with no running event loop: The Safeprinter has closed.

Process finished with exit code 0
~~~

A more advanced demonstration can be seen in the `tkinter_demo` program.

Output from `tkinter_demo`

~~~
0.001s In Print Thread of 2 without a loop: The SafePrinter is open for output.
0.002s In MainThread of 2 without a loop --- main starting
0.002s In Asyncio's Thread of 3 without a loop --- aio_main starting
0.003s In MainThread of 3 without a loop --- tk_main starting

0.328s In Asyncio's Thread of 3 with a loop --- manage_aio_loop starting
0.371s In MainThread of 3 without a loop --- tk_callbacks starting
0.371s In MainThread of 3 without a loop --- tk_callback_consumer starting
0.371s In MainThread of 3 without a loop --- aio_exception_handler starting. block=3.1s
0.372s In Asyncio's Thread of 3 with a loop --- aio_blocker starting. block=3.1s.
0.372s In MainThread of 3 without a loop --- aio_exception_handler starting. block=1.1s
0.372s In Asyncio's Thread of 3 with a loop --- aio_blocker starting. block=1.1s.
0.372s In IO Block Thread (3.2s) of 4 without a loop --- io_exception_handler starting. block=3.2s.
0.372s In IO Block Thread (3.2s) of 4 without a loop --- io_blocker starting. block=3.2s.
0.372s In IO Block Thread (1.2s) of 5 without a loop --- io_exception_handler starting. block=1.2s.
0.372s In IO Block Thread (1.2s) of 5 without a loop --- io_blocker starting. block=1.2s.
0.372s In MainThread of 5 without a loop --- tk_callbacks ending - All blocking callbacks have been scheduled.

1.472s In Asyncio's Thread of 5 with a loop --- aio_blocker ending. block=1.1s.
1.476s In MainThread of 5 without a loop --- aio_exception_handler ending. block=1.1s
1.577s In IO Block Thread (1.2s) of 5 without a loop --- io_blocker ending. block=1.2s.
1.577s In IO Block Thread (1.2s) of 5 without a loop --- io_exception_handler ending. block=1.2s.
3.472s In Asyncio's Thread of 4 with a loop --- aio_blocker ending. block=3.1s.
3.485s In MainThread of 4 without a loop --- aio_exception_handler ending. block=3.1s
3.577s In IO Block Thread (3.2s) of 4 without a loop --- io_blocker ending. block=3.2s.
3.577s In IO Block Thread (3.2s) of 4 without a loop --- io_exception_handler ending. block=3.2s.
 
3.902s In MainThread of 3 without a loop --- tk_callback_consumer ending
3.902s In MainThread of 3 without a loop --- tk_main ending
3.903s In MainThread of 3 without a loop --- main ending
3.903s In Print Thread of 3 without a loop: The SafePrinter has closed.
~~~