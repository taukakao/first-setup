# timezone.py
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

import vanilla_first_setup.core.timezones as tz
import vanilla_first_setup.core.backend as backend

@Gtk.Template(resource_path="/org/vanillaos/FirstSetup/gtk/default-timezone.ui")
class VanillaDefaultTimezone(Adw.Bin):
    __gtype_name__ = "VanillaDefaultTimezone"

    status_page = Gtk.Template.Child()
    footer = Gtk.Template.Child()
    current_timezone_label = Gtk.Template.Child()
    current_time_label = Gtk.Template.Child()

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.__window = window

        self.__location_page = VanillaDefaultLocation(window, _("Timezone"), tz.TimezonesDataSource())
        self.status_page.set_child(self.__location_page)

    def set_page_active(self):
        # if not self.__location_page.selected_special and tz.user_timezone:
            # self.__location_page.selected_region = tz.user_region
            # self.__location_page.selected_country_code = tz.user_country_code
            # self.__location_page.selected_special = tz.user_timezone

            # time_string, with_date = tz.get_timezone_preview(tz.user_timezone)
            # self.current_time_label.set_label(time_string)
            # self.current_timezone_label.set_label(tz.user_timezone)

        self.__location_page.set_page_active()

        # TODO: Get current system timezone
        selected_timezone = self.__location_page.selected_special
        if selected_timezone:
            time_string, with_date = tz.get_timezone_preview(selected_timezone)
            self.current_time_label.set_label(time_string)
            self.current_timezone_label.set_label(selected_timezone)
            self.footer.set_visible(True)
        else:
            self.footer.set_visible(False)

    def set_page_inactive(self):
        self.__location_page.set_page_inactive()

    def finish(self):
        self.__location_page.finish()
        timezone = self.__location_page.selected_special
        return backend.set_timezone(timezone)
