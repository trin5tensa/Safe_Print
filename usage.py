"""Usage demo."""
#  Copyright (c) 2022-2022. Stephen Rigden.
#  Last modified 10/14/22, 8:44 AM by stephen.
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import time

from threadsafe_printer import SafePrinter


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
    with SafePrinter() as safeprint:
        sys.exit(main())
