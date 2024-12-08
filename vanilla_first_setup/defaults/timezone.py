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
import copy

from gi.repository import Adw, GLib, Gtk

import vanilla_first_setup.core.timezones as tz

logger = logging.getLogger("VanillaInstaller::Timezone")

@Gtk.Template(resource_path="/org/vanillaos/FirstSetup/gtk/widget-timezone-list-page.ui")
class VanillaTimezoneListPage(Adw.Bin):
    __gtype_name__ = "VanillaTimezoneListPage"

    pref_group = Gtk.Template.Child()

    def __init__(self, items: list[str], display_names: list[str], button_callback, active_item: str, **kwargs):
        super().__init__(**kwargs)

        self.__items = items
        self.__button_callback = button_callback
        self.__display_names = display_names
        self.__active_item = active_item

        self.__build_ui()

    def __build_ui(self):
        first_button = None

        for index, item in enumerate(self.__items):
            region_row = Adw.ActionRow()
            region_row.set_use_markup(False)
            region_row.set_title(self.__display_names[index])

            button = Gtk.CheckButton()
            button.set_valign(Gtk.Align.CENTER)
            button.connect("activate", self.__on_button_activated, item)
            button.set_focusable(False)
            if item == self.__active_item:
                button.set_active(True)

            button_active = item == self.__active_item
            button = create_check_button(self.__on_button_activated, item, button_active)

            if first_button:
                button.set_group(first_button)
            else:
                first_button = button

            region_row.add_prefix(button)
            region_row.set_activatable_widget(button)

            self.pref_group.add(region_row)

    def __on_button_activated(self, widget, item):
        if len(self.__items) == 1:
            widget.set_active(True)
        self.__button_callback(widget, item)

    # def update_time_preview(self, *args):
    #     tz_time, tz_date = get_timezone_preview(self.tz_name)
    #     self.set_subtitle(f"{tz_time} • {tz_date}")

@Gtk.Template(resource_path="/org/vanillaos/FirstSetup/gtk/default-timezone.ui")
class VanillaDefaultTimezone(Adw.Bin):
    __gtype_name__ = "VanillaDefaultTimezone"

    entry_search_timezone = Gtk.Template.Child()
    navigation = Gtk.Template.Child()
    region_group = Gtk.Template.Child()

    search_controller = Gtk.EventControllerKey.new()
    
    selected_region = ""
    selected_country_code = ""
    selected_timezone = ""

    __built_already = False

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.__window = window

        self.search_controller.connect("key-released", self.__on_search_key_pressed)
        self.entry_search_timezone.add_controller(self.search_controller)
        tz.register_location_callback(self.__user_location_received)

    def set_page_active(self):
        if self.selected_timezone != "":
            self.__window.set_ready(True)
        
        if self.__built_already:
            return
        self.__built_already = True
        self.__build_ui()

    def set_page_inactive(self):
        return

    def finish(self):
        # TODO: call backend with timezone
        return
    
    def __user_location_received(self, location):
        self.selected_region = tz.user_region
        self.selected_country_code = tz.user_country_code
        self.selected_timezone = tz.user_timezone
        self.__window.set_ready(True)
    
    def __build_ui(self):
        first_button = None

        for region in tz.all_country_codes_by_region:
            region_row = Adw.ActionRow()
            region_row.set_use_markup(False)
            region_row.set_title(region)

            button_active = region == self.selected_region
            button = create_check_button(self.__on_region_button_clicked, region, button_active)

            if first_button:
                button.set_group(first_button)
            else:
                first_button = button

            region_row.add_prefix(button)
            region_row.set_activatable_widget(button)

            self.region_group.add(region_row)

    def __on_region_button_clicked(self, widget, region):
        self.selected_region = region
        self.__build_country_page(region)
    
    def __build_country_page(self, region):
        country_page = Adw.NavigationPage()
        country_page.set_title(_("Country"))

        country_codes = tz.all_country_codes_by_region[region]
        countries = copy.deepcopy(country_codes)
        for idx, country_code in enumerate(countries):
            countries[idx] = tz.all_country_names_by_code[country_code]

        countries_page = VanillaTimezoneListPage(country_codes, countries, self.__on_country_button_clicked, self.selected_country_code)

        country_page.set_child(countries_page)

        self.navigation.push(country_page)

    def __on_country_button_clicked(self, widget, country_code):
        self.selected_country_code = country_code
        self.__build_timezones_page(country_code)

    def __build_timezones_page(self, country_code):
        timezones_view_page = Adw.NavigationPage()
        timezones_view_page.set_title(_("Timezone"))

        timezones = tz.all_timezones_by_country_code[country_code]
        timezones_page = VanillaTimezoneListPage(timezones, timezones, self.__on_timezones_button_clicked, self.selected_timezone)

        timezones_view_page.set_child(timezones_page)

        self.navigation.push(timezones_view_page)

    def __on_timezones_button_clicked(self, widget, timezone):
        self.selected_timezone = timezone
        print("clicked on:", timezone)

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

def create_check_button(callback, item: str, active: bool) -> Gtk.CheckButton:
    button = Gtk.CheckButton()
    button.set_valign(Gtk.Align.CENTER)
    button.connect("activate", callback, item)
    button.set_focusable(False)
    button.set_active(active)

    return button
