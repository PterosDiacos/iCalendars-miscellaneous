from datetime import date, timedelta, datetime
from icalendar import Calendar, Event
from dateutil.easter import easter

# https://github.com/mattsmi/Python_Calendar_Calcs
import MattaCalendarCalculations as mcc

def create_orthodox_feasts_ics(start_date, end_date, filename="orthodox_feasts.ics"):
    # Initialize the calendar
    cal = Calendar()
    cal.add("prodid", "-//Greek Orthodox Feast Days//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")

    # Fixed Feasts Dictionary (Revised Julian Month, Revised Julian Day: Name)
    fixed_feasts = {
        (1, 6): "Theophany",
        (2, 2): "Presentation of Christ",
        (3, 25): "Annunciation",
        (8, 6): "Transfiguration of Christ",
        (8, 15): "Dormition of the Theotokos",
        (9, 8): "Nativity of the Theotokos",
        (9, 14): "Elevation of the Holy Cross",
        (11, 21): "Presentation of the Theotokos",
        (12, 25): "Nativity of Christ"
    }

    # 1. Process Fixed Feasts by converting each Gregorian day to Revised Julian
    current_date = start_date
    while current_date <= end_date:
        # Convert Gregorian day to CJDN (Chronological Julian Day Number)
        cjdn = mcc.pGregorianToCJDN(current_date.year, current_date.month, current_date.day)

        # Convert CJDN to Revised Julian (Milanković) to extract month and day
        rj_month = mcc.pCJDNToMilankovic(cjdn, False, True, False)
        rj_day = mcc.pCJDNToMilankovic(cjdn, False, False, True)

        # Check if the Revised Julian month and day match any of our fixed feasts
        if (rj_month, rj_day) in fixed_feasts:
            feast_name = fixed_feasts[(rj_month, rj_day)]
            _add_event(cal, feast_name, current_date)

        current_date += timedelta(days=1)

    # 2. Process Movable Feasts (Pascha-based)
    # We iterate through the unique years present in the date range
    for year in range(start_date.year, end_date.year + 1):
        # dateutil.easter method=2 uses the Orthodox (Julian) calculation but returns a Gregorian date
        pascha_date = easter(year, method=2)

        movable_feasts = [
            (pascha_date - timedelta(days=48), "Clean Monday"),
            (pascha_date - timedelta(days=7), "Palm Sunday"),
            (pascha_date, "Pascha"),
            (pascha_date + timedelta(days=39), "Ascension of Christ"),
            (pascha_date + timedelta(days=49), "Holy Pentecost")
        ]

        for event_date, name in movable_feasts:
            # Only add the movable feast if it falls within the requested date range
            if start_date <= event_date <= end_date:
                _add_event(cal, name, event_date)

    # Write the calendar to a file
    with open(filename, "wb") as f:
        f.write(cal.to_ical())

    print(f"Successfully generated '{filename}' from {start_date} to {end_date}.")

def _add_event(cal, summary, event_date):
    """Helper function to create an all-day event and add it to the calendar."""
    event = Event()
    event.add("summary", summary)
    event.add("dtstart", event_date)
    event.add("dtend", event_date + timedelta(days=1))
    event.add("dtstamp", datetime.now())
    event.add("uid", f"{event_date.isoformat()}@orthodox-feasts.local")

    cal.add_component(event)

if __name__ == "__main__":
    start_dt = date(2026, 1, 1)
    end_dt = date(2030, 12, 31)
    output = f"../ics/orthodox-feasts-{start_dt.year}-{end_dt.year}.ics"

    create_orthodox_feasts_ics(start_dt, end_dt, output)
