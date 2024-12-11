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

import vanilla_first_setup.core.keyboard as kbd
import vanilla_first_setup.core.timezones as tz
from vanilla_first_setup.defaults.timezone import VanillaTimezoneListPage

logger = logging.getLogger("VanillaInstaller::Keyboard")

@Gtk.Template(resource_path="/org/vanillaos/FirstSetup/gtk/default-keyboard.ui")
class VanillaDefaultKeyboard(Adw.Bin):
    __gtype_name__ = "VanillaDefaultKeyboard"

    entry_search_keyboard = Gtk.Template.Child()
    navigation = Gtk.Template.Child()
    search_warning_label = Gtk.Template.Child()
    
    selected_region = None
    selected_country_code = None
    selected_keyboard = None

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.__window = window

        self.navigation.connect("popped", self.__on_popped)
        self.entry_search_keyboard.connect("search_changed", self.__on_search_field_changed)

    def set_page_active(self):
        if self.selected_keyboard:
            self.__window.set_ready(True)

        if self.selected_region:
            self.__show_location(tz.user_region, tz.user_country_code)
        if tz.has_user_preferred_location():
            selected_region, selected_country_code, selected_timezone = tz.get_user_preferred_location()
            if selected_region not in kbd.all_regions:
                selected_region = ""
            if selected_country_code not in kbd.all_country_codes:
                selected_country_code = ""
            self.__show_location(selected_region, selected_country_code)
        elif tz.user_region:
            user_region = tz.user_region
            user_country_code = tz.user_country_code
            if user_region not in kbd.all_regions:
                user_region = ""
            if user_country_code not in kbd.all_country_codes:
                user_country_code = ""
            self.__show_location(user_region, user_country_code)
        else:
            self.__show_location(None, None)

    def set_page_inactive(self):
        return

    def finish(self):
        tz.set_user_preferred_location(self.selected_region, self.selected_country_code, None)
        # TODO: call backend with keyboard
        return

    def __show_location(self, region, country_code):
        stack = []
        regions_page = self.__build_ui()
        stack.append(regions_page)

        if region:
            country_page = self.__build_country_page(region)
            stack.append(country_page)
        
        if country_code:
            keyboards_page = self.__build_keyboards_page(country_code)
            stack.append(keyboards_page)

        self.navigation.replace(stack)
    
    def __build_ui(self) -> VanillaTimezoneListPage:
        regions = kbd.all_regions
        region_names = kbd.all_region_names
        regions_page = VanillaTimezoneListPage(_("Region"), regions, region_names, self.__on_region_button_clicked, [self.selected_region])
        regions_page.set_tag("region")

        return regions_page

    def __on_region_button_clicked(self, widget, region):
        country_page = self.__build_country_page(region)
        self.navigation.push(country_page)
    
    def __build_country_page(self, region) -> VanillaTimezoneListPage:
        country_codes = kbd.all_country_codes_by_region[region]
        country_names = kbd.retrieve_country_names_by_region(region)

        countries_page = VanillaTimezoneListPage(_("Country"), country_codes, country_names, self.__on_country_button_clicked, [self.selected_country_code])
        countries_page.set_tag("country")

        return countries_page
        
    def __on_country_button_clicked(self, widget, country_code):
        keyboards_page = self.__build_keyboards_page(country_code)
        self.navigation.push(keyboards_page)

    def __build_keyboards_page(self, country_code):

        keyboards = kbd.all_keyboard_layouts_by_country_code[country_code]
        keyboard_names = kbd.all_keyboard_layout_names_by_country_code[country_code]
        keyboards_page = VanillaTimezoneListPage(_("Keyboard"), keyboards, keyboard_names, self.__on_keyboards_button_clicked, [self.selected_keyboard], keyboards)
        keyboards_page.set_tag("keyboard")

        return keyboards_page

    def __on_keyboards_button_clicked(self, widget, keyboard):
        self.selected_country_code = kbd.country_code_from_keyboard(keyboard)
        self.selected_region = kbd.region_from_keyboard(keyboard)
        self.selected_keyboard = keyboard
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

        keyboards_page = self.navigation.find_page("keyboard")
        if keyboards_page:
            keyboards_page.update_active([self.selected_keyboard])

        search_page = self.navigation.find_page("search")
        if search_page:
            search_page.update_active([self.selected_keyboard])

    def __retrieve_navigation_stack(self) -> list[VanillaTimezoneListPage]:
        stack = []

        page = self.navigation.get_visible_page()
        while page:
            stack.insert(0, page)
            page = self.navigation.get_previous_page(page)

        return stack

    def __on_search_field_changed(self, *args):
        max_results = 50

        search_term: str = self.entry_search_keyboard.get_text().strip()

        if not search_term:
            nav_page = self.navigation.get_visible_page()
            if nav_page and nav_page.get_tag() == "search":
                self.navigation.pop()
            return

        keyboards_filtered, list_shortened = kbd.search_keyboards(search_term, max_results)

        if len(keyboards_filtered) > max_results:
            list_shortened = True
            keyboards_filtered = keyboards_filtered[0:max_results]

        keyboard_names_filtered = [kbd.find_keyboard_layout_name_for_keyboard(keyboard) for keyboard in keyboards_filtered]
        new_search_nav_page = VanillaTimezoneListPage(_("Search results"), keyboards_filtered, keyboard_names_filtered, self.__on_keyboards_button_clicked, [self.selected_keyboard], keyboards_filtered)
        new_search_nav_page.set_tag("search")

        if self.navigation.get_visible_page().get_tag() == "search":
            stack = self.__retrieve_navigation_stack()
            stack.pop()
            stack.append(new_search_nav_page)
            self.navigation.replace(stack)
        else:
            self.navigation.push(new_search_nav_page)

        self.search_warning_label.set_visible(list_shortened)
