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
from gettext import gettext as _
import copy

from gi.repository import Adw, Gtk

import vanilla_first_setup.core.timezones as tz

logger = logging.getLogger("VanillaInstaller::Timezone")

@Gtk.Template(resource_path="/org/vanillaos/FirstSetup/gtk/widget-timezone-list-page.ui")
class VanillaTimezoneListPage(Adw.Bin):
    __gtype_name__ = "VanillaTimezoneListPage"

    pref_group = Gtk.Template.Child()

    def __init__(self, items: list[str], display_names: list[str], button_callback, active_item: str, suffixes: list[str]|None = None, **kwargs):
        super().__init__(**kwargs)

        self.__items = items
        self.__button_callback = button_callback
        self.__display_names = display_names
        self.__suffixes = suffixes
        self.__active_item = active_item

        self.__all_rows = []

        self.__build_ui()

    def clear_items(self):
        for row in self.__all_rows:
            self.pref_group.remove(row)
        self.__all_rows.clear()

    def rebuild(self, items: list[str], display_names: list[str], active_item: str, suffixes: list[str]|None = None):
        self.clear_items()

        self.__items = items
        self.__display_names = display_names
        self.__active_item = active_item
        self.__suffixes = suffixes

        self.__build_ui()

    def __build_ui(self):
        first_button = None

        for index, item in enumerate(self.__items):
            region_row = Adw.ActionRow()
            region_row.set_use_markup(False)
            region_row.set_title(self.__display_names[index])
            if self.__suffixes:
                label = Gtk.Label()
                label.set_label(self.__suffixes[index])
                region_row.add_suffix(label)

            button_active = item == self.__active_item
            button = self.__create_check_button(self.__on_button_activated, item, button_active)

            if first_button:
                button.set_group(first_button)
            else:
                first_button = button

            region_row.add_prefix(button)
            region_row.set_activatable_widget(button)

            self.pref_group.add(region_row)
            self.__all_rows.append(region_row)

    def __on_button_activated(self, widget, item):
        if len(self.__items) == 1:
            widget.set_active(True)
        self.__button_callback(widget, item)

    def __create_check_button(self, callback, item: str, active: bool) -> Gtk.CheckButton:
        button = Gtk.CheckButton()
        button.set_valign(Gtk.Align.CENTER)
        button.connect("activate", callback, item)
        button.set_focusable(False)
        button.set_active(active)

        return button

@Gtk.Template(resource_path="/org/vanillaos/FirstSetup/gtk/default-timezone.ui")
class VanillaDefaultTimezone(Adw.Bin):
    __gtype_name__ = "VanillaDefaultTimezone"

    entry_search_timezone = Gtk.Template.Child()
    navigation = Gtk.Template.Child()
    search_warning_label = Gtk.Template.Child()
    current_timezone_label = Gtk.Template.Child()
    current_time_label = Gtk.Template.Child()
    
    selected_region = ""
    selected_country_code = ""
    selected_timezone = ""

    __search_results_list_page: VanillaTimezoneListPage|None = None
    __search_results_nav_page: Adw.NavigationPage|None = None

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.__window = window

        self.navigation.connect("popped", self.__on_popped)
        self.entry_search_timezone.connect("search_changed", self.__on_search_field_changed)
        tz.register_location_callback(self.__user_location_received)

    def set_page_active(self):
        if self.selected_timezone != "":
            self.__window.set_ready(True)

        region_page = self.__build_ui()
        self.navigation.replace([region_page])

        if self.selected_timezone:
            self.current_timezone_label.set_label(self.selected_timezone)
            self.current_time_label.set_label(tz.get_timezone_preview(self.selected_timezone)[0])

    def set_page_inactive(self):
        return

    def finish(self):
        # TODO: call backend with timezone
        return
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

    def __user_location_received(self, location):
        self.selected_region = tz.user_region
        self.selected_country_code = tz.user_country_code
        self.selected_timezone = tz.user_timezone
        self.__window.set_ready(True)
    
    def __build_ui(self) -> Adw.NavigationPage:
        timezones_view_page = Adw.NavigationPage()
        timezones_view_page.set_title(_("Region"))

        regions = []
        for region in tz.all_country_codes_by_region:
            regions.append(region)
        regions_page = VanillaTimezoneListPage(regions, regions, self.__on_region_button_clicked, self.selected_region)

        timezones_view_page.set_child(regions_page)
        return timezones_view_page

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
        self.__set_region_from_country_code(country_code)
        self.selected_country_code = country_code
        self.__build_timezones_page(country_code)

    def __build_timezones_page(self, country_code):
        timezones_view_page = Adw.NavigationPage()
        timezones_view_page.set_title(_("Timezone"))

        timezones = tz.all_timezones_by_country_code[country_code]
        city_names = [" ".join(timezone.split("/")[1:]) for timezone in timezones]
        time_previes = [tz.get_timezone_preview(timezone)[0] for timezone in timezones]
        timezones_page = VanillaTimezoneListPage(timezones, city_names, self.__on_timezones_button_clicked, self.selected_timezone, time_previes)

        timezones_view_page.set_child(timezones_page)

        self.navigation.push(timezones_view_page)

    def __on_timezones_button_clicked(self, widget, timezone):
        self.__set_country_code_from_timezone(timezone)
        self.__set_region_from_timezone(timezone)
        self.selected_timezone = timezone
        self.__window.set_ready()
        self.__window.finish_step()

    def __set_region_from_country_code(self, country_code):
        for region, tz_country_code in tz.all_country_codes_by_region.items():
            if country_code == tz_country_code:
                self.selected_region = region
                return
            
    def __set_country_code_from_timezone(self, timezone):
        for country_code, tzcc_timezones in tz.all_timezones_by_country_code.items():
            for tzcc_timezone in tzcc_timezones:
                if timezone == tzcc_timezone:
                    self.selected_country_code = country_code
                    return
            
    def __set_region_from_timezone(self, timezone):
        self.selected_region = tz.region_from_timezone(timezone)

    def __on_popped(self, nag_view, page, *args):
        if page == self.__search_results_nav_page:
            self.__search_results_list_page.clear_items()
            self.search_warning_label.set_visible(False)


    def __on_search_field_changed(self, *args):
        max_results = 50

        search_term: str = self.entry_search_timezone.get_text().strip()
        
        if search_term == "":
            self.navigation.pop()
            return

        timezones_filtered = []

        list_shortened = False

        for country_codes, timezones in tz.all_timezones_by_country_code.items():
            if len(timezones_filtered) > max_results:
                list_shortened = True
                break
            for timezone in timezones:
                if search_term.replace(" ", "_").lower() in timezone.lower():
                    timezones_filtered.append(timezone)

        for country_code, country_name in tz.all_country_names_by_code.items():
            if len(timezones_filtered) > max_results:
                list_shortened = True
                break
            if search_term.lower() in country_name.lower():
                for timezone in tz.all_timezones_by_country_code[country_code]:
                    if timezone not in timezones_filtered:
                        timezones_filtered.append(timezone)

        if len(timezones_filtered) > max_results:
            list_shortened = True
            timezones_filtered = timezones_filtered[0:max_results]

        time_previes = [tz.get_timezone_preview(timezone)[0] for timezone in timezones_filtered]

        if self.__search_results_list_page:
            self.__search_results_list_page.clear_items()
            self.__search_results_list_page.rebuild(timezones_filtered,  timezones_filtered, self.selected_timezone, time_previes)
        else:
            self.__search_results_nav_page = Adw.NavigationPage()
            self.__search_results_nav_page.set_title(_("Search results"))
            self.__search_results_list_page = VanillaTimezoneListPage(timezones_filtered, timezones_filtered, self.__on_timezones_button_clicked, self.selected_timezone, time_previes)
            self.__search_results_nav_page.set_child(self.__search_results_list_page)

        if self.navigation.get_visible_page() != self.__search_results_nav_page:
            self.navigation.push(self.__search_results_nav_page)

        self.search_warning_label.set_visible(list_shortened)
