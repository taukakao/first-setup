import logging
import copy

import gi
gi.require_version("GnomeDesktop", "4.0")
from gi.repository import GnomeDesktop

import vanilla_first_setup.core.timezones as tz

logger = logging.getLogger("FirstSetup::Keyboard")

xkb = GnomeDesktop.XkbInfo()

all_country_codes: list[str] = []
all_country_codes_by_region: dict[str, list[str]] = {}
all_keyboard_layouts: list[str] = sorted(xkb.get_all_layouts(), key=len)
default_keyboard_layouts_by_country_code: dict[str, str] = {}
all_keyboard_layouts_by_country_code: dict[str, list[str]] = {}

def region_from_keyboard(keyboard) -> str:
    return tz.region_from_country_code(country_code_from_keyboard(keyboard))
        
def country_code_from_keyboard(keyboard) -> str:
    for country_code, e_keyboards in all_keyboard_layouts_by_country_code.items():
        for e_keyboard in e_keyboards:
            if keyboard == e_keyboard:
                return country_code
    return None

__keyboards_layouts_without_region: list[str] = copy.deepcopy(all_keyboard_layouts)

for country_code in tz.all_country_codes:
    layouts = xkb.get_layouts_for_country(country_code)
    layouts.sort(key=len)

    if len(layouts) == 0:
        continue

    for layout in layouts:
        if layout in __keyboards_layouts_without_region:
            __keyboards_layouts_without_region.remove(layout)

    region = tz.region_from_country_code(country_code)
    if region not in all_country_codes_by_region:
        all_country_codes_by_region[region] = []

    all_country_codes.append(country_code)
    all_country_codes_by_region[region].append(country_code)
    default_keyboard_layouts_by_country_code[country_code] = layouts
    all_keyboard_layouts_by_country_code[country_code] = layouts

print(__keyboards_layouts_without_region)
