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