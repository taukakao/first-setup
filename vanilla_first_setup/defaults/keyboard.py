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
import gi
import copy

gi.require_version("GnomeDesktop", "4.0")

from gi.repository import Adw, Gtk
from gettext import gettext as _

from vanilla_first_setup.defaults.timezone import VanillaTimezoneListPage
import vanilla_first_setup.core.keyboard as kbd
import vanilla_first_setup.core.timezones as tz


@Gtk.Template(resource_path="/org/vanillaos/FirstSetup/gtk/default-keyboard.ui")
class VanillaDefaultKeyboard(Adw.Bin):
    __gtype_name__ = "VanillaDefaultKeyboard"

    entry_search_keyboard = Gtk.Template.Child()
    navigation = Gtk.Template.Child()
    search_warning_label = Gtk.Template.Child()

    all_selected_regions = []
    all_selected_country_codes = []
    all_selected_keyboards = []

    __search_results_list_page: VanillaTimezoneListPage|None = None
    __search_results_nav_page: Adw.NavigationPage|None = None

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.__window = window

        self.navigation.connect("popped", self.__on_popped)
        self.entry_search_keyboard.connect("search_changed", self.__on_search_field_changed)

    def set_page_active(self):
        show_location = False
        selected_region = ""
        selected_country_code = ""
        if tz.has_user_preferred_location():
            selected_region, selected_country_code, timezone = tz.get_user_preferred_location()
            show_location = selected_region in kbd.all_country_codes_by_region and selected_country_code in kbd.all_country_codes

        if len(self.all_selected_keyboards) > 0:
            self.__window.set_ready(True)

        if show_location:
            self.__show_location(selected_region, selected_country_code)
        else:
            self.__show_location(None, None)

    def set_page_inactive(self):
        return

    def finish(self):
        # TODO: call backend with keyboard layout
        return
    # def get_finals(self):
    #     variant = self.selected_keyboard["variant"]

    #     # NOTE: we use BACKSPACE=guess here by default
    #     # Ref: <https://manpages.ubuntu.com/manpages/bionic/en/man5/keyboard.5.htmlZ
    #     if variant is None:
    #         return {
    #             "vars": {"confKeyboard": True},
    #             "funcs": [
    #                 {
    #                     "if": "confKeyboard",
    #                     "type": "command",
    #                     "commands": [
    #                         f'echo XKBMODEL="pc105" >> /etc/default/keyboard',
    #                         f'echo XKBLAYOUT="{self.selected_keyboard["layout"]}" >> /etc/default/keyboard',
    #                         f'echo BACKSPACE="guess" >> /etc/default/keyboard',
    #                     ],
    #                 }
    #             ],
    #         }  # fallback
    #     return {
    #         "vars": {"confKeyboard": True},
    #         "funcs": [
    #             {
    #                 "if": "confKeyboard",
    #                 "type": "command",
    #                 "commands": [
    #                     f'echo XKBMODEL="pc105" >> /etc/default/keyboard',
    #                     f'echo XKBLAYOUT="{self.selected_keyboard["layout"]}" >> /etc/default/keyboard',
    #                     f'echo XKBVARIANT="{self.selected_keyboard["variant"]}" >> /etc/default/keyboard',
    #                     f'echo BACKSPACE="guess" >> /etc/default/keyboard',
    #                 ],
    #             }
    #         ],
    #     }

    def __show_location(self, region, country_code):
        pages = [self.__build_ui()]

        if region:
            page = self.__build_country_page(region)
            pages.append(page)
        
        if country_code:
            page = self.__build_keyboards_page(country_code)
            pages.append(page)

        self.navigation.replace(pages)

    def __build_ui(self) -> Adw.NavigationPage:
        keyboards_view_page = Adw.NavigationPage()
        keyboards_view_page.set_title(_("Region"))

        regions = []
        for region in kbd.all_country_codes_by_region:
            regions.append(region)
        regions.append("Extra")
        regions_page = VanillaTimezoneListPage(regions, regions, self.__on_region_button_clicked, "", radio_buttons=False, multiple_active_items=self.all_selected_regions)

        keyboards_view_page.set_child(regions_page)
        return keyboards_view_page

    def __on_region_button_clicked(self, widget, region):
        widget.set_active(False)
        page = None
        if region == "Extra":
            page = self.__build_keyboards_page("Extra")
        else:
            page = self.__build_country_page(region)
        self.navigation.push(page)
    
    def __build_country_page(self, region):
        country_page = Adw.NavigationPage()
        country_page.set_title(_("Country"))

        country_codes_unfiltered = kbd.all_country_codes_by_region[region]
        country_codes = []
        for country_code in country_codes_unfiltered:
            if country_code in kbd.all_keyboard_layouts_by_country_code:
                country_codes.append(country_code)
        countries = copy.deepcopy(country_codes)
        for idx, country_code in enumerate(countries):
            countries[idx] = tz.all_country_names_by_code[country_code]

        countries_page = VanillaTimezoneListPage(country_codes, countries, self.__on_country_button_clicked, "", radio_buttons=False, multiple_active_items=self.all_selected_country_codes)

        country_page.set_child(countries_page)

        return country_page

    def __on_country_button_clicked(self, widget, country_code):
        widget.set_active(False)
        page = self.__build_keyboards_page(country_code)
        self.navigation.push(page)

    def __build_keyboards_page(self, country_code):
        keyboards_view_page = Adw.NavigationPage()
        keyboards_view_page.set_title(_("Keyboard Layout"))

        if country_code == "Extra":
            keyboards = kbd.keyboards_layouts_without_region
            keyboard_names = kbd.keyboards_layout_names_without_region
        else:
            keyboards = kbd.all_keyboard_layouts_by_country_code[country_code]
            keyboard_names = kbd.all_keyboard_layout_names_by_country_code[country_code]
        keyboards_page = VanillaTimezoneListPage(keyboards, keyboard_names, self.__on_keyboards_button_clicked, "", suffixes=keyboards, radio_buttons=False, multiple_active_items=self.all_selected_keyboards)

        keyboards_view_page.set_child(keyboards_page)

        return keyboards_view_page

    def __on_keyboards_button_clicked(self, widget, keyboard):
        selected_region = kbd.region_from_keyboard(keyboard)
        selected_country_code = kbd.country_code_from_keyboard(keyboard)
        if keyboard in self.all_selected_keyboards:
            widget.set_active(False)
            self.all_selected_keyboards.remove(keyboard)
            self.all_selected_regions = []
            self.all_selected_country_codes = []
            for keyboard in self.all_selected_keyboards:
                self.all_selected_regions.append(kbd.region_from_keyboard(keyboard))
                self.all_selected_country_codes.append(kbd.country_code_from_keyboard(keyboard))
            self.selected_keyboard = ""
            self.__window.set_ready(len(self.all_selected_keyboards) > 0)
            
        else:
            self.all_selected_regions.append(selected_region)
            self.all_selected_country_codes.append(selected_country_code)
            self.all_selected_keyboards.append(keyboard)
            self.__window.set_ready()

        if not selected_region:
            selected_region = None
            selected_country_code = "Extra"

        self.__show_location(selected_region, selected_country_code)
        

    def __on_popped(self, nag_view, page, *args):
        if page == self.__search_results_nav_page:
            self.__search_results_list_page.clear_items()
            self.search_warning_label.set_visible(False)

    def __on_search_field_changed(self, *args):
        return
        # max_results = 50

        # search_term: str = self.entry_search_keyboard.get_text().strip()
        
        # if search_term == "":
        #     self.navigation.pop()
        #     return

        # keyboards_filtered = []

        # list_shortened = False

        # for country_codes, keyboards in tz.all_keyboards_by_country_code.items():
        #     if len(keyboards_filtered) > max_results:
        #         list_shortened = True
        #         break
        #     for keyboard in keyboards:
        #         if search_term.replace(" ", "_").lower() in keyboard.lower():
        #             keyboards_filtered.append(keyboard)

        # for country_code, country_name in tz.all_country_names_by_code.items():
        #     if len(keyboards_filtered) > max_results:
        #         list_shortened = True
        #         break
        #     if search_term.lower() in country_name.lower():
        #         for keyboard in tz.all_keyboards_by_country_code[country_code]:
        #             if keyboard not in keyboards_filtered:
        #                 keyboards_filtered.append(keyboard)

        # if len(keyboards_filtered) > max_results:
        #     list_shortened = True
        #     keyboards_filtered = keyboards_filtered[0:max_results]

        # time_previes = [tz.get_keyboard_preview(keyboard)[0] for keyboard in keyboards_filtered]

        # if self.__search_results_list_page:
        #     self.__search_results_list_page.clear_items()
        #     self.__search_results_list_page.rebuild(keyboards_filtered,  keyboards_filtered, self.selected_keyboard, time_previes)
        # else:
        #     self.__search_results_nav_page = Adw.NavigationPage()
        #     self.__search_results_nav_page.set_title(_("Search results"))
        #     self.__search_results_list_page = VanillakeyboardListPage(keyboards_filtered, keyboards_filtered, self.__on_keyboards_button_clicked, self.selected_keyboard, time_previes)
        #     self.__search_results_nav_page.set_child(self.__search_results_list_page)

        # if self.navigation.get_visible_page() != self.__search_results_nav_page:
        #     self.navigation.push(self.__search_results_nav_page)

        # self.search_warning_label.set_visible(list_shortened)

    # def __set_keyboard_layout(self, layout, variant=None):
    #     value = layout

    #     if variant != "":
    #         value = layout + "+" + variant

    #     Gio.Settings.new("org.gnome.desktop.input-sources").set_value(
    #         "sources",
    #         GLib.Variant.new_array(
    #             GLib.VariantType("(ss)"),
    #             [
    #                 GLib.Variant.new_tuple(
    #                     GLib.Variant.new_string("xkb"), GLib.Variant.new_string(value)
    #                 )
    #             ],
    #         ),
    #     )
