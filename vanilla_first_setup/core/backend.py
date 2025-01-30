from enum import Enum

import time

dry_run = True

_progress_subscribers = []

class ProgressState(Enum):
    Running = 1
    Finished = 2
    Failed = 3

def set_keyboard(keyboard: str):
    time.sleep(1)

# sets the currently used keyboard of the desktop environment
def set_live_keyboard(keyboard: str):
    print(keyboard)
    time.sleep(1)

def set_locale(locale: str):
    print(locale)
    time.sleep(1)

def set_timezone(timezone: str):
    print(timezone)
    time.sleep(1)

def set_hostname(hostname: str):
    print(hostname)
    time.sleep(1)

def set_theme(theme: str):
    print(theme)
    time.sleep(1)

def add_user(username: str, full_name: str):
    print(username, full_name)
    time.sleep(1)

def logout():
    print("logging out...")
    time.sleep(1)

def open_network_settings():
    print("opening network settings...")
    time.sleep(1)

def _setup_system():
    print("setting up system...")
    time.sleep(3)

def _install_flatpak(id: str):
    print(id)
    time.sleep(3)

_deferred_setup_system_actions = []

def setup_system_deferred():
    _deferred_setup_system_actions = []
    def setup_system():
        report_progress("setup_system", ProgressState.Running)
        try:
            _setup_system()
        except:
            report_progress("setup_system", ProgressState.Failed)
        else:
            report_progress("setup_system", ProgressState.Finished)

    _deferred_setup_system_actions.append(setup_system)

_deferred_install_flatpak_actions = []

def install_flatpak_deferred(id: str, name: str):
    _deferred_install_flatpak_actions = []

    def install_flatpak():
        report_progress("install_flatpak", ProgressState.Running, {id: id, name: name})
        try:
            _install_flatpak(id)
        except:
            report_progress("install_flatpak", ProgressState.Failed, {id: id, name: name})
        else:
            report_progress("install_flatpak", ProgressState.Finished, {id: id, name: name})
    _deferred_install_flatpak_actions.append(install_flatpak)
    print("deferred install of flatpak", name)

def start_deferred_actions():
    _deferred_actions = _deferred_setup_system_actions + _deferred_install_flatpak_actions
    for action in _deferred_actions:
        action()

def subscribe_progress(callback):
    _progress_subscribers.append(callback)

def report_progress(id: str, state: ProgressState, info = None):
    for subscriber in _progress_subscribers:
        subscriber(id, state, info)
