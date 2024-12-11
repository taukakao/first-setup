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

from gi.repository import Adw, Gtk

import vanilla_first_setup.core.timezones as tz

logger = logging.getLogger("VanillaInstaller::Timezone")

@Gtk.Template(resource_path="/org/vanillaos/FirstSetup/gtk/widget-timezone-list-page.ui")
class VanillaTimezoneListPage(Adw.NavigationPage):
    __gtype_name__ = "VanillaTimezoneListPage"

    pref_group = Gtk.Template.Child()

    def __init__(self, title: str, items: list[str], display_names: list[str], button_callback, active_items: list[str] = [], suffixes: list[str]|None = None, radio_buttons: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.set_title(title)

        self.__items = items
        self.__button_callback = button_callback
        self.__display_names = display_names
        self.__suffixes = suffixes
        self.__active_items = active_items
        self.__radio_buttons = radio_buttons

        self.__buttons = []

        self.__build_ui()

    def update_active(self, items):
        self.__active_items = items

        for button, item in self.__buttons:
            is_active = item in self.__active_items
            button.set_active(is_active)

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

            button_active = item in self.__active_items
            button = self.__create_check_button(self.__on_button_activated, item, button_active)

            if self.__radio_buttons:
                if first_button:
                    button.set_group(first_button)
                else:
                    first_button = button

            region_row.add_prefix(button)
            region_row.set_activatable_widget(button)

            self.pref_group.add(region_row)
            self.__buttons.append((button, item))

    def __on_button_activated(self, widget, item):
        self.__button_callback(widget, item)
        self.update_active(self.__active_items)

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
    
    selected_region = None
    selected_country_code = None
    selected_timezone = None

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.__window = window

        self.navigation.connect("popped", self.__on_popped)
        self.entry_search_timezone.connect("search_changed", self.__on_search_field_changed)

    def set_page_active(self):
        if self.selected_timezone:
            self.__window.set_ready(True)

        if self.selected_timezone:
            self.current_timezone_label.set_label(self.selected_timezone)
            self.current_time_label.set_label(tz.get_timezone_preview(self.selected_timezone)[0])

        if self.selected_region:
            self.__show_location(self.selected_region, self.selected_country_code)
        elif tz.has_user_preferred_location():
            selected_region, selected_country_code, selected_timezone = tz.get_user_preferred_location()
            self.__show_location(selected_region, selected_country_code)
        elif tz.user_region:
            self.__show_location(tz.user_region, tz.user_country_code)
        else:
            self.__show_location(None, None)

    def set_page_inactive(self):
        return

    def finish(self):
        tz.set_user_preferred_location(self.selected_region, self.selected_country_code, self.selected_timezone)
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

    def __show_location(self, region, country_code):
        stack = []
        regions_page = self.__build_ui()
        stack.append(regions_page)

        if region:
            country_page = self.__build_country_page(region)
            stack.append(country_page)
        
        if country_code:
            timezones_page = self.__build_timezones_page(country_code)
            stack.append(timezones_page)

        self.navigation.replace(stack)
    
    def __build_ui(self) -> VanillaTimezoneListPage:
        regions = tz.all_regions
        region_names = tz.all_region_names
        timezones_view_page = VanillaTimezoneListPage(_("Region"), regions, region_names, self.__on_region_button_clicked, [self.selected_region])
        timezones_view_page.set_tag("region")

        return timezones_view_page

    def __on_region_button_clicked(self, widget, region):
        country_page = self.__build_country_page(region)
        self.navigation.push(country_page)
    
    def __build_country_page(self, region) -> VanillaTimezoneListPage:
        country_codes = tz.all_country_codes_by_region[region]
        country_names = tz.retrieve_country_names_by_region(region)

        countries_page = VanillaTimezoneListPage(_("Country"), country_codes, country_names, self.__on_country_button_clicked, [self.selected_country_code])
        countries_page.set_tag("country")

        return countries_page
        

    def __on_country_button_clicked(self, widget, country_code):
        timezones_page = self.__build_timezones_page(country_code)
        self.navigation.push(timezones_page)

    def __build_timezones_page(self, country_code):

        timezones = tz.all_timezones_by_country_code[country_code]
        city_names = [" ".join(timezone.split("/")[1:]) for timezone in timezones]
        time_previes = [tz.get_timezone_preview(timezone)[0] for timezone in timezones]
        timezones_page = VanillaTimezoneListPage(_("Timezone"), timezones, city_names, self.__on_timezones_button_clicked, [self.selected_timezone], time_previes)
        timezones_page.set_tag("timezone")

        return timezones_page

    def __on_timezones_button_clicked(self, widget, timezone):
        self.selected_country_code = tz.country_code_from_timezone(timezone)
        self.selected_region = tz.region_from_timezone(timezone)
        self.selected_timezone = timezone
        self.__refresh_activated_buttons()
        self.__window.set_ready()
        self.__window.finish_step()

    def __on_popped(self, nag_view, page):
        if page.get_tag() == "search":
            self.search_warning_label.set_visible(False)

    def __refresh_activated_buttons(self):
        region_page = self.navigation.find_page("region")
        if region_page:
            region_page.update_active([self.selected_region])

        country_page = self.navigation.find_page("country")
        if country_page:
            country_page.update_active([self.selected_country_code])

        timezone_page = self.navigation.find_page("timezone")
        if timezone_page:
            timezone_page.update_active([self.selected_timezone])

        search_page = self.navigation.find_page("search")
        if search_page:
            search_page.update_active([self.selected_timezone])

    def __retrieve_navigation_stack(self) -> list[VanillaTimezoneListPage]:
        stack = []

        page = self.navigation.get_visible_page()
        while page:
            stack.insert(0, page)
            page = self.navigation.get_previous_page(page)

        return stack

    def __on_search_field_changed(self, *args):
        max_results = 50

        search_term: str = self.entry_search_timezone.get_text().strip()

        if not search_term:
            nav_page = self.navigation.get_visible_page()
            if nav_page and nav_page.get_tag() == "search":
                self.navigation.pop()
            return

        timezones_filtered, list_shortened = tz.search_timezones(search_term, max_results)

        if len(timezones_filtered) < max_results:
            new_timezones_filtered, new_shortened = tz.search_timezones_by_country(search_term, max_results-len(timezones_filtered))
            timezones_filtered += new_timezones_filtered
            list_shortened = list_shortened or new_shortened

        if len(timezones_filtered) > max_results:
            list_shortened = True
            timezones_filtered = timezones_filtered[0:max_results]

        time_previes = [tz.get_timezone_preview(timezone)[0] for timezone in timezones_filtered]

        new_search_nav_page = VanillaTimezoneListPage(_("Search results"), timezones_filtered, timezones_filtered, self.__on_timezones_button_clicked, [self.selected_timezone], time_previes)
        new_search_nav_page.set_tag("search")

        if self.navigation.get_visible_page().get_tag() == "search":
            stack = self.__retrieve_navigation_stack()
            stack.pop()
            stack.append(new_search_nav_page)
            self.navigation.replace(stack)
        else:
            self.navigation.push(new_search_nav_page)

        self.search_warning_label.set_visible(list_shortened)
