"""Usage demo.

This shows the low level API of safepritn
"""
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
