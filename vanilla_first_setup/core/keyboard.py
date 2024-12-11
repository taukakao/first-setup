import logging
import copy

import gi
gi.require_version("GnomeDesktop", "4.0")
from gi.repository import GnomeDesktop

import vanilla_first_setup.core.timezones as tz

logger = logging.getLogger("FirstSetup::Keyboard")

xkb = GnomeDesktop.XkbInfo()

all_regions: list[str] = []
all_region_names: list[str] = []
all_country_codes: list[str] = []
all_country_codes_by_region: dict[str, list[str]] = {}
all_keyboard_layouts: list[str] = []
all_keyboard_layout_names: list[str] = []
all_keyboard_layouts_by_country_code: dict[str, list[str]] = {}
all_keyboard_layout_names_by_country_code: dict[str, list[str]] = {}
keyboards_layouts_without_region: list[str] = copy.deepcopy(all_keyboard_layouts)
keyboards_layout_names_without_region: list[str] = []

def region_from_keyboard(keyboard) -> str:
    return tz.region_from_country_code(country_code_from_keyboard(keyboard))
        
def country_code_from_keyboard(keyboard) -> str:
    for country_code, e_keyboards in all_keyboard_layouts_by_country_code.items():
        for e_keyboard in e_keyboards:
            if keyboard == e_keyboard:
                return country_code
    return ""

def retrieve_country_names_by_region(region) -> list[str]:
    country_codes = all_country_codes_by_region[region]
    countries = copy.deepcopy(country_codes)
    for idx, country_code in enumerate(countries):
        countries[idx] = tz.all_country_names_by_code[country_code]
    return countries

def search_keyboards(search_term: str, limit: int) -> tuple[list[str], bool]:
    '''
        search_keyboards looks for all keyboard names with substring search_term

        search is not case sensitive
    
        returns a list of all matching keyboard names and a bool if the list is shortened due to the limit
    '''
    clean_search_term = search_term.lower()

    keyboards_filtered = []
    list_shortened = False
    for index, keyboard_layout_name in enumerate(all_keyboard_layout_names):
        if len(keyboards_filtered) >= limit:
            list_shortened = True
            break
        if clean_search_term in keyboard_layout_name.lower():
            keyboards_filtered.append(all_keyboard_layouts[index])
    return (keyboards_filtered, list_shortened)

def find_keyboard_layout_name_for_keyboard(keyboard: str) -> str:
    index = all_keyboard_layouts.index(keyboard)
    return all_keyboard_layout_names[index]

for country_code in tz.all_country_codes:
    layouts = xkb.get_layouts_for_country(country_code)
    layouts.sort(key=len)

    if len(layouts) == 0:
        continue

    names = []
    for layout in layouts:
        info = xkb.get_layout_info(layout)
        names.append(info.display_name)
        
        if layout in keyboards_layouts_without_region:
            keyboards_layouts_without_region.remove(layout)

    region = tz.region_from_country_code(country_code)
    if region not in all_country_codes_by_region:
        all_country_codes_by_region[region] = []

    all_country_codes.append(country_code)
    all_country_codes_by_region[region].append(country_code)
    all_keyboard_layouts_by_country_code[country_code] = layouts
    all_keyboard_layout_names_by_country_code[country_code] = names

    for layout in layouts:
        if layout not in all_keyboard_layouts:
            all_keyboard_layouts.append(layout)

for country_code in all_country_codes:
    region = tz.region_from_country_code(country_code)
    if region not in all_regions:
        all_regions.append(region)

all_regions.sort()
for region in all_regions:
    index_in_tz = tz.all_regions.index(region)
    region_name = tz.all_region_names[index_in_tz]
    all_region_names.append(region_name)

all_keyboard_layouts.sort(key=len)
for keyboard_layout in all_keyboard_layouts:
    info = xkb.get_layout_info(keyboard_layout)
    all_keyboard_layout_names.append(info.display_name)

# TODO: use keyboards_layouts_without_region in keyboard page
for layout in keyboards_layouts_without_region:
    info = xkb.get_layout_info(layout)
    keyboards_layout_names_without_region.append(info.display_name)
