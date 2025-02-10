# main.py
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

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Vte", "3.91")

from gi.repository import Gtk, Gdk, Gio, GLib, Adw

import os
import sys
import logging
import core.backend as backend
from gettext import gettext as _
from vanilla_first_setup.window import VanillaWindow

logger = logging.getLogger("FirstSetup::Main")

class FirstSetupApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self, *args, **kwargs):

        log_path = "/tmp/first-setup.log"

        if not os.path.exists(log_path):
            try:
                open(log_path, "a").close()
                os.chmod(log_path, 0o666)
                logging.basicConfig(level=logging.DEBUG,
                            filename=log_path,
                            filemode='a',
                            )
            except OSError as e:
                logger.warning(f"failed to create log file: {log_path}: {e}")
                logging.warning("No log will be stored.")


        super().__init__(
            *args,
            application_id="org.vanillaos.FirstSetup",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs
        )
        self.create_new_user = False

        self.__register_arguments()

    def __register_arguments(self):
        """Register the command line arguments."""
        self.add_main_option(
            "create-new-user",
            ord("n"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            _("Create a new user and log out"),
            None,
        )

    def do_command_line(self, command_line):
        """Handle command line arguments."""
        options = command_line.get_options_dict()

        if options.contains("create-new-user"):
            logger.info("Creating a new user")
            self.create_new_user = options.lookup_value("create-new-user")
            
        self.activate()
        return 0

    def do_activate(self):
        """
        Called when the application is activated.
        We raise the application's main window, creating it if
        necessary.
        """
        # TODO: maybe do this in the installer or the default user?
        # # disable the lock screen and password for the default user
        # if self.create_new_user:
        #     logging.info("disabling screen saver and lock screen")
        #     subprocess.run(
        #         [
        #             "/usr/bin/gsettings",
        #             "set",
        #             "org.gnome.desktop.lockdown",
        #             "disable-lock-screen",
        #             "true",
        #         ]
        #     )
        #     subprocess.run(
        #         [
        #             "/usr/bin/gsettings",
        #             "set",
        #             "org.gnome.desktop.screensaver",
        #             "lock-enabled",
        #             "false",
        #         ]
        #     )

        provider = Gtk.CssProvider()
        provider.load_from_resource("/org/vanillaos/FirstSetup/style.css")
        Gtk.StyleContext.add_provider_for_display(
            display=Gdk.Display.get_default(),
            provider=provider,
            priority=Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
        win = self.props.active_window
        if not win:
            win = VanillaWindow(
                application=self,
                create_new_user=self.create_new_user,
            )
        win.present()

    def close(self, *args):
        """Close the application."""
        self.quit()


def main(version):
    """The application's entry point."""
    backend.setup_system_deferred()
    app = FirstSetupApplication()
    return app.run(sys.argv)
