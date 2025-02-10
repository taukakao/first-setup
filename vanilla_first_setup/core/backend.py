from enum import Enum

import time

dry_run = True

_progress_subscribers = []

class ProgressState(Enum):
    Initialized = 1
    Running = 2
    Finished = 3
    Failed = 4

def set_keyboard(keyboard: str):
    print(keyboard)
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

_deferred_actions = []

def setup_system_deferred():
    global _deferred_actions
    action_id = "setup_system"
    def setup_system():
        report_progress(action_id, ProgressState.Running)
        try:
            _setup_system()
        except:
            report_progress(action_id, ProgressState.Failed)
        else:
            report_progress(action_id, ProgressState.Finished)

    _deferred_actions.append({"id": action_id, "callback": setup_system})
    report_progress(action_id, ProgressState.Initialized)

def install_flatpak_deferred(id: str, name: str):
    global _deferred_actions
    action_id = "install_flatpak"
    action_info = {"id": id, "name": name}
    def install_flatpak():
        report_progress(action_id, ProgressState.Running, action_info)
        try:
            _install_flatpak(id)
        except:
            report_progress(action_id, ProgressState.Failed, action_info)
        else:
            report_progress(action_id, ProgressState.Finished, action_info)
    _deferred_actions.append({"id": action_id, "callback": install_flatpak, "info": action_info})
    report_progress(action_id, ProgressState.Initialized, action_info)

def clear_flatpak_deferred():
    global _deferred_actions
    new_list = []
    for action in _deferred_actions:
        if action["id"] != "install_flatpak":
            new_list.append(action)
    _deferred_actions = new_list

def start_deferred_actions():
    global _deferred_actions
    for action in _deferred_actions:
        action["callback"]()

def subscribe_progress(callback):
    global _deferred_actions
    _progress_subscribers.append(callback)
    for deferred_action in _deferred_actions:
        info = None
        if "info" in deferred_action:
            info = deferred_action["info"]
        callback(deferred_action["id"], ProgressState.Initialized, info)

def report_progress(id: str, state: ProgressState, info = None):
    for subscriber in _progress_subscribers:
        subscriber(id, state, info)
