# hostname.py
#
# Copyright 2023 mirkobrombin
#
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

import re
from gi.repository import Gtk, Adw


@Gtk.Template(resource_path="/org/vanillaos/FirstSetup/gtk/default-hostname.ui")
class VanillaDefaultHostname(Adw.Bin):
    __gtype_name__ = "VanillaDefaultHostname"

    hostname_entry = Gtk.Template.Child()
    hostname_error = Gtk.Template.Child()

    hostname = ""

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.__window = window

        # signals
        self.hostname_entry.connect("changed", self.__on_hostname_entry_changed)
        self.hostname_entry.connect("entry-activated", self.__on_activate)

        self.reactivate()

    def reactivate(self):
        self.__verify_continue()

    def finish(self):
        # TODO: call backend with hostname
        import time
        time.sleep(0.5)

    def __on_activate(self, widget):
        self.__window.finish_step()

    def __on_hostname_entry_changed(self, *args):
        _hostname = self.hostname_entry.get_text()

        if self.__validate_hostname(_hostname):
            self.hostname = _hostname
            self.hostname_entry.remove_css_class("error")
            self.hostname_error.set_opacity(0.0)
            self.__verify_continue()
            return

        self.hostname_entry.add_css_class("error")
        self.hostname = ""
        self.hostname_error.set_opacity(1.0)
        self.__verify_continue()

    def __validate_hostname(self, hostname):
        if len(hostname) > 50:
            return False

        allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split("."))

    def __verify_continue(self):
        ready = self.hostname != ""
        self.__window.set_ready(ready)
