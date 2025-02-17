# vanilla-first-setup.in
#
# Copyright 2025 mirkobrombin
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
import subprocess

VERSION = 'testing'

path_of_this_file = os.path.dirname(os.path.realpath(__file__))
pkgdatadir = os.path.join(path_of_this_file)
localedir = os.path.join(path_of_this_file, "build/po")
moduledir = os.path.join(path_of_this_file, "vanilla_first_setup")

if __name__ == '__main__':

    resource_file = os.path.join(moduledir, "vanilla-first-setup.gresource")
    command = ["glib-compile-resources", f"--sourcedir={moduledir}", f"--target={resource_file}", f"{resource_file}.xml"]
    subprocess.run(command, check=True)

    from vanilla_first_setup import main
    sys.exit(main.main(VERSION, pkgdatadir, moduledir, localedir))
