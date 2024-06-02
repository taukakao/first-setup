# processor.py
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

import os
import shutil
import subprocess
import logging


logger = logging.getLogger("FirstSetup::Processor")


class Processor:
    @staticmethod
    def get_setup_commands(log_path, pre_run, post_run, commands):
        commands = pre_run + commands + post_run
        out_run = ""
        next_boot = []
        commands_script_path = "/etc/org.vanillaos.FirstSetup.commands"
        next_boot_script_path = "/etc/org.vanillaos.FirstSetup.nextBoot"
        next_boot_autostart_path = (
            "/etc/xdg/autostart/org.vanillaos.FirstSetup.nextBoot.desktop"
        )
        user_fs_desktop_path = "/home/$REAL_USER/.local/share/applications/org.vanillaos.FirstSetup.desktop"
        done_file = "/etc/vanilla-first-setup-done"
        pkexec_bin = shutil.which("pkexec")

        logger.info("processing the following commands: \n%s" % "\n".join(commands))

        # Collect all the commands that should be run at the next boot
        for command in commands:
            command = command.strip()

            if not command.startswith("!nextBoot "):
                continue

            command = command.replace("!nextBoot ", "")
            command = command.strip()

            if command.startswith("!noRoot"):
                command = command.replace("!noRoot", "")
                command = command.replace('"', '\\"')
                command = command.replace("'", "\\'")
                command = "systemd-run --user --machine=\"$REAL_USER@.host\" -P -q /usr/bin/bash -c \"%s\"" % command

            next_boot.append(command)

        subprocess.run([pkexec_bin, "/usr/bin/vanilla-first-setup-prepare-files"])

        # generating the commannds and writing them to a file to run them all at once
        with open(commands_script_path, "w") as f:
            f.write("#!/bin/sh\n")
            f.write("# This file was created by FirstSetup\n")
            f.write("# Do not edit this file manually\n\n")

            # fake the process if VANILLA_FAKE is set
            if "VANILLA_FAKE" in os.environ:
                f.write("echo 'VANILLA_FAKE is set, not running commands'\n")
                f.write("exit 0\n")

            # connection test
            f.write("wget -q --spider cloudflare.com\n")
            f.write("if [ $? != 0 ]; then\n")
            f.write("echo 'No internet connection!'\n")
            f.write("exit 1\n")
            f.write("fi\n")

            # nextBoot commands are collected in /etc/org.vanillaos.FirstSetup.nextBoot
            # and executed at the next boot by a desktop entry
            # NOTE: keep black formating disabled for this section
            # fmt: off
            if len(next_boot) > 0:
                f.write("echo '#!/bin/sh' > " + next_boot_script_path + "\n")
                f.write("echo '# This file was created by the Vanilla First Setup' >> " + next_boot_script_path + "\n")
                f.write("echo '# do not edit its content manually' >> " + next_boot_script_path + "\n")

                for command in next_boot:
                    f.write(f"echo '{command}' >> " + next_boot_script_path + "\n")

                f.write(f"echo '[Desktop Entry]' > {next_boot_autostart_path}\n")
                f.write(f"echo 'Name=FirstSetup Next Boot' >> {next_boot_autostart_path}\n")
                f.write(f"echo 'Comment=Run FirstSetup commands at the next boot' >> {next_boot_autostart_path}\n")
                f.write(f"echo 'Exec=vanilla-first-setup --run-post-script \"{pkexec_bin} env REAL_USER=$USER {next_boot_script_path}\"' >> {next_boot_autostart_path}\n")
                f.write(f"echo 'Terminal=false' >> {next_boot_autostart_path}\n")
                f.write(f"echo 'Type=Application' >> {next_boot_autostart_path}\n")
                f.write(f"echo 'X-GNOME-Autostart-enabled=true' >> {next_boot_autostart_path}\n")
            # fmt: on

            for command in commands:
                if command.startswith("!nextBoot"):
                    continue

                if command.startswith("!noRoot"):
                    command = command.replace("!noRoot", "")
                    command = command.replace('"', '\\"')
                    command = command.replace("'", "\\'")
                    command = "systemd-run --user --machine=\"$USER@.host\" -P -q /usr/bin/bash -c \"%s\"" % command

                # outRun bang is used to run a command outside of the main
                # shell script.
                if command.startswith("!outRun"):
                    out_run += command.replace("!outRun", "") + "\n"

                f.write(f"{command}\n")

            # run the outRun commands
            if out_run:
                f.write("if [ $? -eq 0 ]; then")
                f.write(f"{out_run}\n")
                f.write("fi")

            # create the done file
            f.write("if [ $? -eq 0 ]; then\n")
            f.write(f"touch {done_file}\n")
            f.write("fi\n")

            f.flush()
            f.close()

            # setting the file executable
            # os.chmod(f.name, 0o755)

        cmd = [pkexec_bin, f.name]
        print(cmd)
        return cmd

    @staticmethod
    def hide_first_setup(user: str = None):
        if user is None:
            user = os.environ.get("USER")

        autostart_file = (
            "/home/%s/.config/autostart/org.vanillaos.FirstSetup.desktop" % user
        )

        if os.path.exists(autostart_file):
            os.remove(autostart_file)
