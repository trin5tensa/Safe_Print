"""Usage demo."""
import time

from threadsafe_printer import SafePrint


def main():
    safeprint('main starting')
    safeprint('no timestamp', timestamp=False)
    safeprint('going to sleep')
    time.sleep(0.1)
    safeprint('waking up')
    safeprint(' ')
    safeprint(' ', timestamp=False)
    safeprint('resetting the time', reset=True)
    time.sleep(0.05)
    safeprint('main ending')


if __name__ == '__main__':
    with SafePrint() as safeprint:
        main()
