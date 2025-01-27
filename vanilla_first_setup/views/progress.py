# progress.py
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

from gi.repository import Gtk, Adw

@Gtk.Template(resource_path="/org/vanillaos/FirstSetup/gtk/progress.ui")
class VanillaProgress(Adw.Bin):
    __gtype_name__ = "VanillaProgress"

    # carousel_tour = Gtk.Template.Child()

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)

    def set_page_active(self):
        return

    def set_page_inactive(self):
        return

    def finish(self):
        return
