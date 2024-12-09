import gi

gi.require_version("GWeather", "4.0")

from datetime import datetime
import logging
import threading

import requests
from gi.repository import GLib, GWeather
import pytz

logger = logging.getLogger("FirstSetup::Timezones")

world = GWeather.Location.get_world()
base = world

all_country_codes: list[str] = []
all_country_codes_by_region: dict[str, list[str]] = {}
all_timezones_by_country_code: dict[str, list[str]] = {}
all_country_names_by_code: dict[str, str] = {}
user_location: GWeather.Location|None = None
user_country: str|None = None
user_country_code: str|None = None
user_city: str|None = None
user_timezone: str|None = None
user_region: str|None = None

def register_location_callback(callback):
    if user_location:
        callback(user_location)
    __location_callbacks.append(callback)

def get_timezone_preview(tzname):
    timezone = pytz.timezone(tzname)
    now = datetime.now(timezone)
    now_str = (
        "%02d:%02d" % (now.hour, now.minute),
        now.strftime("%A, %d %B %Y"),
    )
    return now_str

def region_from_timezone(tzname):
    return tzname.split("/")[0]

for country_code in pytz.country_timezones:
    timezones = pytz.country_timezones[country_code]
    country_name = pytz.country_names[country_code]
    region = region_from_timezone(timezones[0])

    all_country_codes.append(country_code)
    
    if region not in all_country_codes_by_region:
        all_country_codes_by_region[region] = []
    all_country_codes_by_region[region].append(country_code)

    all_timezones_by_country_code[country_code] = timezones

    all_country_names_by_code[country_code] = country_name

__location_callbacks = []

def __update_user_location(location):
    global user_location
    global user_country
    global user_country_code
    global user_city
    global user_timezone
    global user_region
    user_location = location
    user_country = location.get_country_name()
    user_city = location.get_city_name()
    user_timezone = location.get_timezone().get_identifier()
    user_region = region_from_timezone(user_timezone)
    if location.get_country() in all_country_codes:
        user_country_code = location.get_country()

    for callback in __location_callbacks:
        GLib.idle_add(callback, location)

def __retrieve_location_thread():
    logger.info("Trying to retrieve timezone automatically")
    try:
        res = requests.get("http://ip-api.com/json?fields=49344", timeout=10).json()
        if res["status"] != "success":
            raise Exception(
                f"get_location: request failed with message '{res['message']}'"
            )
        nearest = world.find_nearest_city(res["lat"], res["lon"])
    except Exception as e:
        logger.error(f"Failed to retrieve timezone: {e}")
        nearest = None

    if nearest:
        __update_user_location(nearest)

    logger.info("Done retrieving timezone")

thread = threading.Thread(target=__retrieve_location_thread)
thread.start()
