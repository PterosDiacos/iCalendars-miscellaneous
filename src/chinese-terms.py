"""
Generate an .ics file containing:
  - 二十四節氣 (the 24 solar terms), for a given range of (solar) years
  - A handful of lunar-calendar festivals: 元宵 上巳 端午 七夕 中秋 重陽
"""

from datetime import date, datetime, timedelta

from icalendar import Calendar, Event
from borax.calendars.lunardate import LunarDate, TermUtils

UID_DOMAIN = "chinese-terms.local"

# The 24 solar terms, in calendar order (keys as borax expects them).
SOLAR_TERMS = {
    "小寒": "小寒", "大寒": "大寒", "立春": "立春", "雨水": "雨水",
    "惊蛰": "啟蟄", "春分": "春分", "清明": "清明", "谷雨": "穀雨",
    "立夏": "立夏", "小满": "小滿", "芒种": "芒種", "夏至": "夏至",
    "小暑": "小暑", "大暑": "大暑", "立秋": "立秋", "处暑": "處暑",
    "白露": "白露", "秋分": "秋分", "寒露": "寒露", "霜降": "霜降",
    "立冬": "立冬", "小雪": "小雪", "大雪": "大雪", "冬至": "冬至"
}

# Lunar (農曆) festivals: (summary, lunar_month, lunar_day)
LUNAR_FESTIVALS = [
    ("元宵", 1, 15), ("上巳", 3, 3),
    ("端午", 5, 5),  ("七夕", 7, 7),
    ("中秋", 8, 15), ("重陽", 9, 9),
]


def solar_term_date(year: int, term_name: str) -> date:
    """Solar (Gregorian) date of one of the 24 solar terms in `year`."""
    return TermUtils.nth_term_day(year, term_name=term_name)


def lunar_festival_date(year: int, lunar_month: int, lunar_day: int) -> date:
    """Solar (Gregorian) date corresponding to a lunar month/day in lunar `year`."""
    return LunarDate(year, lunar_month, lunar_day).to_solar_date()


def make_event(day: date, summary: str) -> Event:
    event = Event()
    event.add("summary", summary)
    event.add("dtstart", day)
    event.add("dtend", day + timedelta(days=1))
    event.add("dtstamp", datetime.now())
    event.add("uid", f"{day.isoformat()}-{summary}@{UID_DOMAIN}")
    return event


def solar_term_events_for_year(year: int) -> list[Event]:
    return [
        make_event(solar_term_date(year, key), term)
        for key, term in SOLAR_TERMS.items()
    ]


def lunar_festival_events_for_year(year: int) -> list[Event]:
    events = []
    for summary, month, day in LUNAR_FESTIVALS:
        try:
            d = lunar_festival_date(year, month, day)
        except ValueError:
            # In rare edge cases (e.g. requested lunar day doesn't exist
            # that lunar year), just skip it.
            continue
        events.append(make_event(d, summary))
    return events


def events_for_year(year: int) -> list[Event]:
    return solar_term_events_for_year(year) + lunar_festival_events_for_year(year)


def build_calendar(start_year: int, end_year: int) -> Calendar:
    """end_year is inclusive."""
    cal = Calendar()
    cal.add("prodid", "-//Chinese Terms Generator//borax//")
    cal.add("version", "2.0")
    for year in range(start_year, end_year + 1):
        for event in events_for_year(year):
            cal.add_component(event)
    return cal


if __name__ == "__main__":
    START_YEAR = 2022
    END_YEAR = 2031
    OUTPUT_PATH = f"../ics/chinese-terms-{START_YEAR}-{END_YEAR}.ics"

    calendar = build_calendar(START_YEAR, END_YEAR)

    with open(OUTPUT_PATH, "wb") as f:
        f.write(calendar.to_ical())

    print(f"Wrote {OUTPUT_PATH} for years {START_YEAR}-{END_YEAR}")
