# window.py
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

import threading

from gettext import gettext as _
from gi.repository import Gtk, Adw, GLib

import vanilla_first_setup.core.backend as backend

from vanilla_first_setup.dialog import VanillaDialog

@Gtk.Template(resource_path="/org/vanillaos/FirstSetup/gtk/window.ui")
class VanillaWindow(Adw.ApplicationWindow):
    __gtype_name__ = "VanillaWindow"

    stack = Gtk.Template.Child()
    btn_back = Gtk.Template.Child()
    btn_next = Gtk.Template.Child()
    btn_next_spinner = Gtk.Template.Child()
    toasts = Gtk.Template.Child()
    style_manager = Adw.StyleManager().get_default()

    can_continue = False

    __is_finishing_step = False

    pages = []
    __current_page_index = 0

    def __init__(self, pkgdatadir: str, configure_system_mode: bool, **kwargs):
        super().__init__(**kwargs)

        self.pkgdatadir = pkgdatadir
        self.configure_system_mode = configure_system_mode

        self.__build_ui(configure_system_mode)
        self.__connect_signals()

        backend.subscribe_errors(self.__error_received)

    def set_ready(self, ready: bool = True):
        self.__loading_indicator(False)
        self.can_continue = ready
        self.btn_next.set_sensitive(ready)

    def finish_step(self):
        if not self.can_continue or self.__is_finishing_step:
            return
        self.can_continue = False
        self.__is_finishing_step = True
        
        self.__loading_indicator()
        
        thread = threading.Thread(target=self.__finish_step_thread)
        thread.start()

    def __error_received(self, script_name: str, command: list[str], id: int):
        GLib.idle_add(self.__error_toast, _("Setup failed: ") + script_name, id)

    def __error_toast(self, message: str, id: int):
        toast = Adw.Toast.new(message)
        toast.props.timeout = 0
        toast.props.button_label = _("Details")
        toast.connect("button-clicked", self.__error_toast_clicked, id)
        self.toasts.add_toast(toast)
    
    def __error_toast_clicked(self, widget, id: int):
        message = backend.errors[id]
        dialog = VanillaDialog(self, _("Error log"), message)
        dialog.present()

    def set_focus_on_next(self):
        self.btn_next.grab_focus()

    def __connect_signals(self):
        self.btn_back.connect("clicked", self.__on_btn_back_clicked)
        self.btn_next.connect("clicked", self.__on_btn_next_clicked)
        return

    def __build_ui(self, configure_system_mode: bool):

        if configure_system_mode:
            from vanilla_first_setup.defaults.welcome import VanillaDefaultWelcome
            from vanilla_first_setup.defaults.language import VanillaDefaultLanguage
            from vanilla_first_setup.defaults.keyboard import VanillaDefaultKeyboard
            from vanilla_first_setup.defaults.timezone import VanillaDefaultTimezone
            from vanilla_first_setup.defaults.hostname import VanillaDefaultHostname
            from vanilla_first_setup.defaults.user import VanillaDefaultUser
            from vanilla_first_setup.views.logout import VanillaLogout

            self.__view_welcome = VanillaDefaultWelcome(self)
            self.__view_language = VanillaDefaultLanguage(self)
            self.__view_keyboard = VanillaDefaultKeyboard(self)
            self.__view_timezone = VanillaDefaultTimezone(self)
            self.__view_hostname = VanillaDefaultHostname(self)
            self.__view_user = VanillaDefaultUser(self)
            self.__view_logout = VanillaLogout(self)

            # TODO: add accessibility button
            self.pages.append(self.__view_welcome)
            self.pages.append(self.__view_language)
            self.pages.append(self.__view_keyboard)
            self.pages.append(self.__view_timezone)
            self.pages.append(self.__view_hostname)
            self.pages.append(self.__view_user)
            self.pages.append(self.__view_logout)
        else:
            from vanilla_first_setup.defaults.welcome_user import VanillaDefaultWelcomeUser
            from vanilla_first_setup.defaults.conn_check import VanillaDefaultConnCheck
            from vanilla_first_setup.defaults.theme import VanillaDefaultTheme
            from vanilla_first_setup.defaults.applications import VanillaLayoutApplications
            from vanilla_first_setup.views.progress import VanillaProgress

            self.__view_welcome = VanillaDefaultWelcomeUser(self)
            self.__view_conn_check = VanillaDefaultConnCheck(self)
            self.__view_theme = VanillaDefaultTheme(self)
            self.__view_apps = VanillaLayoutApplications(self)
            # TODO: remove back button somehow
            self.__view_progress = VanillaProgress(self)

            self.pages.append(self.__view_welcome)
            self.pages.append(self.__view_conn_check)
            self.pages.append(self.__view_theme)
            self.pages.append(self.__view_apps)
            self.pages.append(self.__view_progress)
            # TODO: add final page

        for page in self.pages:
            self.stack.add_child(page)

        self.stack.set_visible_child(self.__view_welcome)

        self.__on_page_changed()

    def __on_page_changed(self, *args):
        current_page = self.stack.get_visible_child()
        current_page.set_page_active()
    
    def __on_btn_next_clicked(self, widget):
        self.finish_step()

    def __on_btn_back_clicked(self, widget):
        if self.__is_finishing_step:
            return
        self.__last_page()

    def __loading_indicator(self, waiting: bool = True):
        if self.__current_page_index == 0:
            self.btn_next.set_visible(False)
            self.btn_next_spinner.set_visible(False)
            return

        self.btn_next.set_visible(not waiting)
        self.btn_next_spinner.set_visible(waiting)

    def __finish_step_thread(self):
        success = self.stack.get_visible_child().finish()
        if success:
            GLib.idle_add(self.__next_page)
        else:
            GLib.idle_add(self.__fail)

    def __fail(self):
        self.__is_finishing_step = False
        self.__loading_indicator(False)
        self.set_ready(False)

    def __next_page(self):
        target_index = self.__current_page_index + 1
        self.__scroll_page(target_index)
        self.__is_finishing_step = False

    def __last_page(self):
        target_index = self.__current_page_index - 1
        self.__scroll_page(target_index)

    def __scroll_page(self, target_index: int):
        self.set_ready(False)

        old_current_page = self.stack.get_visible_child()
        target_page = self.pages[target_index]

        max_page_index = len(self.pages)-1
        self.btn_back.set_visible(target_index != 0)
        self.btn_next.set_visible(target_index != max_page_index and target_index != 0)

        self.stack.set_visible_child(target_page)
        self.__current_page_index = target_index

        old_current_page.set_page_inactive()
        self.__on_page_changed()
