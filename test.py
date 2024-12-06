#!@PYTHON@

# vanilla-first-setup.in
#
# Copyright 2023 mirkobrombin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundationat version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import signal
import locale
import gettext

VERSION = 'testing'

path_of_this_file = os.path.dirname(os.path.realpath(__file__))
pkgdatadir = os.path.join(path_of_this_file, 'vanilla_first_setup')
localedir = '/usr/share/locale'

sys.path.insert(1, pkgdatadir)
signal.signal(signal.SIGINT, signal.SIG_DFL)
locale.bindtextdomain('vanilla_first_setup', localedir)
locale.textdomain('vanilla_first_setup')
gettext.install('vanilla_first_setup', localedir)

if __name__ == '__main__':
    from gi.repository import Gio
    resource = Gio.Resource.load(os.path.join(pkgdatadir, 'vanilla-first-setup.gresource'))
    resource._register()

    from vanilla_first_setup import main
    sys.exit(main.main(VERSION))
