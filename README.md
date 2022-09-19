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

*timestamp* Prefix a timestamp with useful diagnostic information. (Default = True)

*reset* Reset the timer to zero. (Default = False)

## Context manager

### SafePrint() 
Usage:
~~~
def func():
    with SafePrint() as safeprint:
        safeprint('my message')
~~~