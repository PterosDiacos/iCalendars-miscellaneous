from datetime import date, timedelta, datetime
from borax.calendars.lunardate import LunarDate
from icalendar import Calendar, Event

def generate_liuren_ics(start_date: date, end_date: date, filename: str = "liuren.ics"):
    """
    Generates an iCalendar (.ics) file with Chinese Liu Ren states
    for a given Gregorian date range using the "icalendar" library.
    """

    # Liu Ren mapping based on your provided logic
    liuren_states = {
        1: "大安",
        2: "留連",
        3: "速喜",
        4: "赤口",
        5: "将吉",
        6: "空亡"
    }

    # Initialize the calendar and add required metadata
    c = Calendar()
    c.add("prodid", "-//Xiao Liu Ren Calendar Generator//mxm.dk//")
    c.add("version", "2.0")

    # Iterate through every day in the date range
    current_date = start_date
    while current_date <= end_date:
        # Convert Gregorian date to Lunar date
        lunar_date = LunarDate.from_solar_date(
            current_date.year,
            current_date.month,
            current_date.day
        )

        # Extract Lunar month and day 
        x = lunar_date.month
        y = lunar_date.day
        z = (x + y - 2) % 6 + 1
        state = liuren_states[z]

        # Create an event component
        e = Event()
        e.add("summary", f"{state}")
        e.add("dtstart", current_date)
        e.add("dtend", current_date + timedelta(days=1))
        e.add("dtstamp", datetime.now())
        e.add("uid", f"{current_date.isoformat()}@liuren.local")
        c.add_component(e)

        # Move to the next day
        current_date += timedelta(days=1)

    # Write the calendar data to a binary .ics file
    with open(filename, "wb") as f:
        f.write(c.to_ical())

    print(f"Successfully generated '{filename}' from {start_date} to {end_date}.")


if __name__ == "__main__":
    start = date(2026, 1, 1)
    end = date(2030, 12, 31)
    generate_liuren_ics(start, end, f"../ics/xiao-liuren-{start.year}-{end.year}.ics")
