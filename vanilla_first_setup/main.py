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
import grp
from gettext import gettext as _
from vanilla_first_setup.window import VanillaWindow
import vanilla_first_setup.core.backend as backend

logger = logging.getLogger("FirstSetup::Main")

class FirstSetupApplication(Adw.Application):
    """The main application singleton class."""

    pkgdatadir = ""

    def __init__(self, pkgdatadir: str, *args, **kwargs):

        log_path = "/tmp/first-setup.log"

        self.pkgdatadir = pkgdatadir

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
        self.dry_run = True

        self.__register_arguments()

    def __register_arguments(self):
        """Register the command line arguments."""
        self.add_main_option(
            "dry-run",
            ord("d"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            _("Don't make any changes to the system."),
            None,
        )

    def do_command_line(self, command_line):
        """Handle command line arguments."""
        options = command_line.get_options_dict()

        if options.lookup_value("dry-run"):
            logger.info("Running in dry-run mode.")
            self.dry_run = True
        else:
            self.dry_run = False
        
        backend.set_dry_run(self.dry_run)
            
        self.activate()
        return 0

    def do_activate(self):
        """
        Called when the application is activated.
        We raise the application's main window, creating it if
        necessary.
        """
        all_groups = [g.gr_name for g in grp.getgrall()]
        configure_system_mode = False
        if "vanilla-first-setup" in all_groups and os.getlogin() in grp.getgrnam("vanilla-first-setup").gr_mem:
            print("Detected special first-setup user, running in configure system mode.")
            configure_system_mode = True

        if configure_system_mode:
            backend.disable_lockscreen()
        else:
            backend.setup_system_deferred()
            backend.setup_flatpak_remote()

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
                pkgdatadir=self.pkgdatadir,
                configure_system_mode=configure_system_mode,
            )
        win.present()

    def close(self, *args):
        """Close the application."""
        self.quit()


def main(version, pkgdatadir: str):
    """The application's entry point."""
    if pkgdatadir == "":
        print("Can't continue without a data directory.")
        sys.exit(1)
        return
    backend.set_script_path(os.path.join(pkgdatadir, "scripts"))
    app = FirstSetupApplication(pkgdatadir)
    return app.run(sys.argv)
