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

import logging
import re
import threading
import unicodedata
from gettext import gettext as _

from gi.repository import Adw, GLib, Gtk

import vanilla_first_setup.core.timezones as tz

logger = logging.getLogger("VanillaInstaller::Timezone")


@Gtk.Template(resource_path="/org/vanillaos/FirstSetup/gtk/default-timezone.ui")
class VanillaDefaultTimezone(Adw.Bin):
    __gtype_name__ = "VanillaDefaultTimezone"

    entry_search_timezone = Gtk.Template.Child()
    navigation = Gtk.Template.Child()
    region_group = Gtk.Template.Child()

    search_controller = Gtk.EventControllerKey.new()
    selected_timezone = {}

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.__window = window

        self.search_controller.connect("key-released", self.__on_search_key_pressed)
        self.entry_search_timezone.add_controller(self.search_controller)

        self.__build_ui()

    def set_page_active(self):
        return

    def set_page_inactive(self):
        return

    def finish(self):
        # TODO: call backend with timezone
        return
    
    def __build_ui(self):
        for region in tz.all_country_codes_by_region:
            region_row = Adw.ActionRow()
            region_row.set_use_markup(False)
            region_row.set_title(region)

            button = Gtk.Button()
            button.add_css_class("flat")
            button.set_valign(Gtk.Align.CENTER)
            button.set_icon_name("go-next-symbolic")
            button.connect("clicked", self.__on_region_button_clicked, region)
            button.set_focusable(False)

            region_row.add_suffix(button)
            region_row.set_activatable_widget(button)

            self.region_group.add(region_row)

    def __on_region_button_clicked(self, widget, region):
        self.__build_country_page(region)
    
    def __build_country_page(self, region):
        country_page = Adw.NavigationPage()
        country_page.set_title(_("Country"))

        country_group = Adw.PreferencesGroup()

        for country_code in tz.all_country_codes_by_region[region]:
            country_row = Adw.ActionRow()
            country_row.set_use_markup(False)
            country_row.set_title(tz.all_country_names_by_code[country_code])

            button = Gtk.Button()
            button.add_css_class("flat")
            button.set_valign(Gtk.Align.CENTER)
            button.set_icon_name("go-next-symbolic")
            button.connect("clicked", self.__on_country_button_clicked, country_code)
            button.set_focusable(False)

            country_row.add_suffix(button)
            country_row.set_activatable_widget(button)

            country_group.add(country_row)

        country_page.set_child(country_group)

        self.navigation.push(country_page)

    def __on_country_button_clicked(self, widget, country_code):
        self.__build_timezones_page(country_code)

    def __build_timezones_page(self, country_code):
        timezones_page = Adw.NavigationPage()
        timezones_page.set_title(_("Timezones"))

        timezones_group = Adw.PreferencesGroup()

        first_button = None

        for timezone in tz.all_timezones_by_country_code[country_code]:
            timezones_row = Adw.ActionRow()
            timezones_row.set_use_markup(False)
            timezones_row.set_title(timezone)

            button = Gtk.CheckButton()
            button.set_valign(Gtk.Align.CENTER)
            button.connect("activate", self.__on_timezones_button_clicked, timezone)
            button.set_focusable(False)

            if first_button:
                button.set_group(first_button)
            else:
                first_button = button

            timezones_row.add_prefix(button)
            timezones_row.set_activatable_widget(button)

            timezones_group.add(timezones_row)

        timezones_page.set_child(timezones_group)

        self.navigation.push(timezones_page)

    def __on_timezones_button_clicked(self, widget, timezone):
        print("clicked on:", timezone)

    # def timezone_verify(self, carousel=None, idx=None):
    #     if idx is not None and idx != self.__step_num:
    #         return

    #     def timezone_verify_callback(result, *args):
    #         if result:
    #             current_city = result.get_city_name()
    #             current_country = result.get_country_name()
    #             for entry in self.__tz_entries:
    #                 if (
    #                     current_city == entry.title
    #                     and current_country == entry.subtitle
    #                 ):
    #                     self.selected_timezone["zone"] = current_city
    #                     self.selected_timezone["region"] = current_country
    #                     entry.select_button.set_active(True)
    #                     return
    #             self.btn_next.set_sensitive(True)

    #     thread = threading.Thread(target=get_location, args=(timezone_verify_callback,))
    #     thread.start()

    # def get_finals(self):
    #     try:
    #         return {
    #             "vars": {"setTimezone": True},
    #             "funcs": [
    #                 {
    #                     "if": "setTimezone",
    #                     "type": "command",
    #                     "commands": [
    #                         f'echo "{self.selected_timezone["region"]}/{self.selected_timezone["zone"]}" > /etc/timezone',
    #                         f"ln -sf /usr/share/zoneinfo/{self.selected_timezone['region']}/{self.selected_timezone['zone']} /etc/localtime",
    #                     ],
    #                 }
    #             ],
    #         }
    #     except IndexError:
    #         return {
    #             "vars": {"setTimezone": True},
    #             "funcs": [
    #                 {
    #                     "if": "setTimezone",
    #                     "type": "command",
    #                     "commands": [
    #                         f'echo "Europe/London" > /etc/timezone',
    #                         f"ln -sf /usr/share/zoneinfo/Europe/London /etc/localtime",
    #                     ],
    #                 }
    #             ],
    #         }

    def __on_search_key_pressed(self, *args):
        return
        # def remove_accents(msg: str):
        #     out = (
        #         unicodedata.normalize("NFD", msg)
        #         .encode("ascii", "ignore")
        #         .decode("utf-8")
        #     )
        #     return str(out)

        # search_entry = self.entry_search_timezone.get_text().lower()
        # keywords = remove_accents(search_entry)

        # if len(keywords) <= 1:
        #     for expander in self.__expanders:
        #         expander.set_visible(True)
        #         expander.set_expanded(False)
        #     return

        # current_expander = 0
        # current_country = self.__tz_entries[0].subtitle
        # visible_entries = 0
        # for entry in self.__tz_entries:
        #     row_title = remove_accents(entry.get_title().lower())
        #     match = re.search(keywords, row_title, re.IGNORECASE) is not None
        #     entry.set_visible(match)
        #     if entry.subtitle != current_country:
        #         self.__expanders[current_expander].set_expanded(True)
        #         self.__expanders[current_expander].set_visible(visible_entries != 0)
        #         visible_entries = 0
        #         current_country = entry.subtitle
        #         current_expander += 1
        #     visible_entries += match

    # def __on_row_toggle(self, __check_button, widget):
    #     tz_split = widget.tz_name.split("/", 1)
    #     self.selected_timezone["region"] = tz_split[0]
    #     self.selected_timezone["zone"] = tz_split[1]
    #     self.current_tz_label.set_label(widget.tz_name)
    #     self.current_location_label.set_label(
    #         _("(at %s, %s)") % (widget.title, widget.subtitle)
    #     )
    #     self.btn_next.set_sensitive(True)

    # def __generate_timezone_list_widgets(self):
    #     def __populate_expander(expander, region, country, *args):
    #         for city, tzname in all_timezones[region][country].items():
    #             timezone_row = TimezoneRow(
    #                 city, country, tzname, self.__on_row_toggle, expander
    #             )
    #             self.__tz_entries.append(timezone_row)
    #             if len(self.__tz_entries) > 0:
    #                 timezone_row.select_button.set_group(
    #                     self.__tz_entries[0].select_button
    #                 )
    #             expander.add_row(timezone_row)

    #     for country, region in self.expanders_list.items():
    #         if len(all_timezones[region][country]) > 0:
    #             expander = Adw.ExpanderRow.new()
    #             expander.set_title(country)
    #             expander.set_subtitle(region)
    #             self.all_timezones_group.add(expander)
    #             self.__expanders.append(expander)
    #             GLib.idle_add(__populate_expander, expander, region, country)

    # @property
    # def step_id(self):
    #     return self.__key
