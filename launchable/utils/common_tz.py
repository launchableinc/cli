from dateutil.tz import gettz

# The dateutil library does not recognize timezone abbreviations (like "PDT" or "JST") by default.
# To handle these, we manually map common abbreviations to their corresponding timezones.
# See: https://github.com/dateutil/dateutil/issues/932
COMMON_TIMEZONES = {
    "UTC": gettz("UTC"),
    # https://time.now/timezones/pdt/
    "PDT": gettz("America/Los_Angeles"),
    # https://time.now/timezones/jst/
    "JST": gettz("Asia/Tokyo"),
}
