"""HarborFlow operational business rules.

Keep calculations and record-processing logic separate from user interaction
where practical.
"""

import datetime

#for task 8
def ask_valid_date():
    #repeats only the date prompt until the input is a valid YYYY-MM-DD date.
    while True:
        date = input("Date: ").strip()
        try:
            d = datetime.date.fromisoformat(date)
            return d
        except ValueError:
            print("Error - Date must use YYYY-MM-DD.")

#for task 8
def find_vessel_by_name(name, vessels):
    #strips spaces and matches the name case-insensitively.
    name = name.strip().lower()
    for vessel in vessels:
        if vessel["name"].strip().lower() == name:
            return vessel
    return None

#for task 8
def find_upcoming_calls(calls, vessel_id, reference_date):
    #keeps the vessel’s calls on or after the reference date and skips rows with invalid dates (reporting them).
    upcoming = []
    for row in calls:
        if row["vessel_id"] != vessel_id:
            continue
        try:
            arrival = datetime.date.fromisoformat(row["arrival_date"])
        except ValueError:
            print(f"Skipped call {row['call_id']}: invalid date {row['arrival_date']}")
            continue
        if arrival >= reference_date:
            upcoming.append(row)
    return upcoming


#for task 8
def build_forecast_lookup(weather_rows):
    #builds a dict keyed by (port_code, date).
    lookup = {}
    for row in weather_rows:
        lookup[(row["port_code"], row["date"])] = row
    return lookup

#for task 8
def read_forecast(row):
    #converts wind, rain and waves to floats.
    """Return (wind, rain, waves) as floats, or None if a value is malformed."""
    try:
        wind = float(row["wind_kmh"])
        rain = float(row["precipitation_mm"])
        waves = float(row["wave_height_m"])
    except ValueError:
        print(f"Skipped weather row {row['port_code']} {row['date']}: invalid data")
        return None
    return wind, rain, waves


#for task 8
def recommend(wind, rain, waves):
    #is a pure function returning every matching recommendation in table order, or Normal operating plan.
    recommendations = []
    if wind >= 45:
        recommendations.append("Suspend crane operations.")
    if waves >= 2.5:
        recommendations.append("Arrange tug assistance.")
    if rain >= 8 and wind < 45:
        recommendations.append("Prepare covered handling.")
    if not recommendations:
        recommendations.append("Normal operating plan.")
    return recommendations

#for task 8
def print_forecast(vessel_name, port_code, arrival, wind, rain, waves):
    #prints the three-line forecast.
    print(f"{vessel_name} | {port_code} | {arrival.strftime('%d %B %Y')}")
    print(f"Wind: {wind:.1f} km/h | Rain: {rain:.1f} mm | Waves: {waves:.1f} m")

    recommendations = recommend(wind, rain, waves)
    print(f"Recommendation: {' '.join(recommendations)}")




from data_access import load_cached_index, load_incidents, save_index
from text_tools import build_index

#for task 9
def get_incident_index():
    #uses the cache when valid.
    cached = load_cached_index()
    if cached is not None:
        return cached

    incidents = load_incidents()
    index, titles = build_index(incidents)
    save_index(index, titles)
    return index, titles


