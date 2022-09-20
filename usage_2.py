"""Usage demo.

This shows the high level API of safeprint
"""
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
