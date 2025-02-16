from enum import Enum

import time
import os
import subprocess

script_base_path = None

dry_run = True

_progress_subscribers = []
_error_subscribers = []

errors = []

class ProgressState(Enum):
    Initialized = 1
    Running = 2
    Finished = 3
    Failed = 4

def set_keyboard(keyboard: str):
    keyboard_parts = keyboard.split("+", 1)
    layout = keyboard_parts[0]
    variant = ""
    if len(keyboard_parts) > 1:
        variant = keyboard_parts[1]
    return run_script("keyboard", ["pc105", layout, variant])

# sets the currently used keyboard of the desktop environment
def set_live_keyboard(keyboard: str):
    return run_script("live-keyboard", [keyboard])

def set_locale(locale: str):
    return run_script("locale", [locale])

def set_timezone(timezone: str):
    return run_script("timezone", [timezone])

def set_hostname(hostname: str):
    return run_script("hostname", [hostname])

def set_theme(theme: str) -> str|None:
    return run_script("theme", [theme])

def add_user(username: str, full_name: str):
    return run_script("user", [username, full_name])

def logout():
    return run_script("logout", [])

def open_network_settings():
    return run_script("open-network-settings", [])

def _setup_system():
    return run_script("setup-system", [])

def _install_flatpak(id: str):
    return run_script("flatpak", [id])


def run_script(name: str, args: list[str]) -> bool:
    if dry_run:
        print("dry-run", name, args)
        time.sleep(0.5)
        return True
    if script_base_path == None:
        print("Could not run operation", name, args, "due to missing script base path")
        return True
    script_path = os.path.join(script_base_path, name)
    command = [script_path] + args
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    result, _ = process.communicate()

    if process.returncode != 0:
        report_error(name, command, result)
        print(name, args, "returned an error:")
        print(result)
        return False
    
    return True

_error_count = 0
_lock_error_count = False

def report_error(script_name: str, command: list[str], message: str):
    global _error_count
    global _lock_error_count
    while(_lock_error_count):
        time.sleep(0.5)
    _lock_error_count = True

    errors.append(message)
    
    for callback in _error_subscribers:
        callback(script_name, command, _error_count)

    _error_count = _error_count + 1
    _lock_error_count = False

_deferred_actions = []

def setup_system_deferred():
    global _deferred_actions
    action_id = "setup_system"
    uid = action_id
    def setup_system():
        _run_function_with_progress(action_id, uid, None, _setup_system)
    _deferred_actions.append({"action_id": action_id, "uid": uid, "callback": setup_system})
    report_progress(action_id, uid, ProgressState.Initialized)

def install_flatpak_deferred(id: str, name: str):
    global _deferred_actions
    action_id = "install_flatpak"
    uid = action_id+id
    action_info = {"app_id": id, "app_name": name}
    def install_flatpak():
        _run_function_with_progress(action_id, uid, action_info, _install_flatpak, id)
    _deferred_actions.append({"action_id": action_id, "uid": uid, "callback": install_flatpak, "info": action_info})
    report_progress(action_id, uid, ProgressState.Initialized, action_info)

def _run_function_with_progress(action_id: str, uid: str, action_info: dict, function, *args):
    report_progress(action_id, uid, ProgressState.Running, action_info)
    success = function(*args)
    if not success:
        report_progress(action_id, uid, ProgressState.Failed, action_info)
    else:
        report_progress(action_id, uid, ProgressState.Finished, action_info)

def clear_flatpak_deferred():
    global _deferred_actions
    new_list = []
    for action in _deferred_actions:
        if action["action_id"] != "install_flatpak":
            new_list.append(action)
    _deferred_actions = new_list

def start_deferred_actions():
    global _deferred_actions
    for action in _deferred_actions:
        action["callback"]()
    id = "all_actions"
    report_progress(id, id, ProgressState.Finished)

def subscribe_progress(callback):
    global _deferred_actions
    global _progress_subscribers
    _progress_subscribers.append(callback)
    for deferred_action in _deferred_actions:
        info = None
        if "info" in deferred_action:
            info = deferred_action["info"]
        callback(deferred_action["action_id"], deferred_action["uid"], ProgressState.Initialized, info)

def report_progress(id: str, uid: str, state: ProgressState, info = None):
    global _progress_subscribers
    for subscriber in _progress_subscribers:
        subscriber(id, uid, state, info)

def set_script_path(path: str):
    global script_base_path
    script_base_path = path

def set_dry_run(dry: bool):
    global dry_run
    dry_run = dry

def subscribe_errors(callback):
    global _error_subscribers
    _error_subscribers.append(callback)
