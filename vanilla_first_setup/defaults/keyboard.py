# keyboard.py
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

from gettext import gettext as _

from gi.repository import Adw, Gtk

from vanilla_first_setup.defaults.locations import VanillaDefaultLocation

import vanilla_first_setup.core.keyboard as kbd
import vanilla_first_setup.core.timezones as tz
import vanilla_first_setup.core.backend as backend

@Gtk.Template(resource_path="/org/vanillaos/FirstSetup/gtk/default-keyboard.ui")
class VanillaDefaultKeyboard(Adw.Bin):
    __gtype_name__ = "VanillaDefaultKeyboard"

    status_page = Gtk.Template.Child()

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.__window = window

        self.__location_page = VanillaDefaultLocation(window, _("Keyboard"), kbd.KeyboardsDataSource())
        self.status_page.set_child(self.__location_page)

    def set_page_active(self):
        self.__location_page.set_page_active()
        return

    def set_page_inactive(self):
        self.__location_page.set_page_inactive()
        return

    def finish(self):
        self.__location_page.finish()
        keyboard = self.__location_page.selected_special
        success = backend.set_live_keyboard(keyboard)
        if not success:
            return False
        success = backend.set_keyboard(keyboard)
        if not success:
            return False
        return True
