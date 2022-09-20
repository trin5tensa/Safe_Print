# safeprint

SafePrint creates a single thread from which all printing will take place. This avoids the race conditions which can occur with Python's regular `print` statement. It can provide a timestamp with useful diagnostic information.

## Functions
### `safeprint.start()`

It creates a print queue and starts a thread. In the thread it starts a continuous loop which looks for print jobs in the queue and `print`s them. Initializes a timer to zero using time.perf_counter. 

### `safeprint.close()`

Closes the queue and the thread.
> Important Note: If close is not called the thread will not be shut down and the Python program will not close.

### `safeprint.print(*msg*: str, *timestamp*: bool = True, *reset*: bool = False)`

Prints *msg* on `sys.stdout`. 

*msg* Text to be printed.

*timestamp* Prefix the message with useful diagnostic information (Default = True). The message includes:
</br>Time since start in seconds.
</br>Name of thread.
</br>Count of running threads.
</br>Whether that thread has a running asyncio loop.
The timestamp is created when this function is called and before the message is put into the print queue. 

*reset* Reset the timer to zero. (Default = False)

Usage:

~~~
import sys
import time

import safeprint as sp


def main():
    sp.start()
    sp.safeprint('main starting')
    sp.safeprint('no timestamp', timestamp = False)
    sp.safeprint('going to sleep')
    time.sleep(1)
    sp.safeprint('waking up')
    sp.safeprint('resetting the time', reset = True)
    sp.safeprint('main ending')
    sp.close()


if __name__ == '__main__':
    sys.exit(main())

~~~

Output

~~~
0.000s  In Print Thread of 2 with no running event loop: The Safeprinter is open for output.
0.000s  In MainThread of 2 with no running event loop --- main starting
no timestamp
0.000s  In MainThread of 2 with no running event loop --- going to sleep
1.004s  In MainThread of 2 with no running event loop --- waking up
0.000s  In MainThread of 2 with no running event loop --- resetting the time
0.000s  In MainThread of 2 with no running event loop --- main ending
0.000s  In Print Thread of 2 with no running event loop: The Safeprinter has closed.

Process finished with exit code 0
~~~
## Context manager

### SafePrint() 
Usage:

~~~
import time

import safeprint as sp


def main():
    with sp.SafePrint() as ts_print:
        ts_print('main starting')
        ts_print('no timestamp', timestamp = False)
        ts_print('going to sleep')
        time.sleep(1)
        ts_print('waking up')
        ts_print('resetting the time', reset = True)
        ts_print('main ending')


if __name__ == '__main__':
    main()

~~~

Output

~~~
0.001s  In Print Thread of 2 with no running event loop: The Safeprinter is open for output.
0.001s  In MainThread of 2 with no running event loop --- main starting
no timestamp
0.001s  In MainThread of 2 with no running event loop --- going to sleep
1.005s  In MainThread of 2 with no running event loop --- waking up
0.000s  In MainThread of 2 with no running event loop --- resetting the time
0.000s  In MainThread of 2 with no running event loop --- main ending
0.000s  In Print Thread of 2 with no running event loop: The Safeprinter has closed.

Process finished with exit code 0
~~~