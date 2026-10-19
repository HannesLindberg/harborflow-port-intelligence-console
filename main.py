"""HarborFlow Assignment 2 starter entry point."""
import math
import json
import data_access
import os
import csv
import datetime
from pathlib import Path
import re
from operations import get_incident_index
from text_tools import longest_stable_sequence

def get_number(prompt, error_message="Invalid input", cast=float, min_value=0, max_value=math.inf):
    """Keep asking until the user enters something that converts with `cast`
    and is >= min_value. Never crashes on bad input."""

    while True:
        raw = input(prompt)
        try:
            value = cast(raw)
        except ValueError:
            print(error_message)
            continue

        if  value < min_value or value > max_value:
            print(error_message)
            continue

        return value

    
#task 1 lists all valid vessels vessels folder
def list_registerd_vessels():
    directory = "dataset/vessels"
    valid_vessels = []
    skipped_count = 0
    requierd_fields = ["vessel_id", "name", "imo", "capacity_teu"]

    if not os.path.exists(directory):
         print(f"Error: Directory {directory} does not exist.")
    else:
         for filename in os.listdir(directory):
                if not filename.endswith(".json"):
                   continue
                file_path = os.path.join(directory, filename)

                try:
                    data = data_access.load_json(file_path) 
                except (json.JSONDecodeError, Exception) as e:
                     skipped_count +=1
                     continue
                if not isinstance(data, dict) or any (field not in data for field in requierd_fields):
                    skipped_count += 1
                    continue
                valid_vessels.append(data)
    valid_vessels.sort(key=lambda v: str(v["name"]).lower())

    #print output
    print("registered Vessels:")
    for vessel in valid_vessels:
        raw_capacity = vessel['capacity_teu']
        if isinstance(raw_capacity, str):
            capacity = int(raw_capacity.replace(",", ""))
        else:
            capacity = int(raw_capacity)
        capacity = capacity/1000
        print(f"- {vessel['name']} | IMO {vessel['imo']} | {capacity} TEU ")
    print(f"Skipped vessel files: {skipped_count}")
    return valid_vessels

#task 2 helper funktion
def validate_date(date_time):
    try:
        datetime.date.fromisoformat(date_time)
        return True
    except ValueError:
        return False
#task 2 helper funktion
def find_vessel(vessel_name, valid_vessels):
    cleaned_name = vessel_name.strip().lower()
    for vessel in valid_vessels:
        if str(vessel.get("name","")).strip().lower() == cleaned_name:
            return vessel
    return None

#task 2
def Inspect_a_vessel_manifest(valid_vessels):
    print("Registered Vessels:")
    for vessel in valid_vessels:
        print(vessel)

    vessel_name_input = input("Vessel name: ").strip()
    matched_vessel = find_vessel(vessel_name_input, valid_vessels)

    if not matched_vessel:
        print("Vessel not found")
        return


    while True:
        refrence_date = input(f"Enter Refrence date in YYYY-MM-DD").strip()
        if not validate_date(refrence_date):
            print("Error- Date must use YYYY-MM-DD")
        else:
            refrence_date = datetime.date.fromisoformat(refrence_date)
            break

    port_calls_path = "dataset/port_calls.csv"
    if not os.path.exists(port_calls_path):
        print(f"Error: Directory {port_calls_path} does not exist.")

    try:
        port_calls_list = data_access.load_csv(port_calls_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    matching_calls = []
    vessel_id = matched_vessel["vessel_id"]

    for call in port_calls_list:
        if call.get("vessel_id") == vessel_id:
            try:
                call_date = datetime.date.fromisoformat(call.get("arrival_date"))
                if call_date >= refrence_date:
                    matching_calls.append((call_date, call.get("call_id"), call))
            except ValueError:
                continue
    if not matching_calls:
        print("No upcoming port calls found")

    #sort calls by (earliest first so by date)
    matching_calls.sort()
    earliest_call = matching_calls[0][2]
    call_id = earliest_call["call_id"].lower()
    arrival_date = datetime.date.fromisoformat(earliest_call["arrival_date"])

    manifest_path = (f"dataset/manifests/{call_id}.json")
    if not os.path.exists(manifest_path):
            print(f"Error: Directory {manifest_path} does not exist.")
            return
    try:
        manifest_data = data_access.load_json(manifest_path)
    except Exception:
        print("Manifest unavalible.")
        return

    shipment_dict = {}
    shipments_folder = "dataset/shipments"

    if os.path.exists(shipments_folder) and os.path.isdir(shipments_folder):
        for filename in os.listdir(shipments_folder):
            if filename.endswith(".json"):
                shipment_path = os.path.join(shipments_folder, filename)
                try:
                    ship_data = data_access.load_json(shipment_path)
                    ship_id = ship_data.get("shipment_id")
                    if ship_id:
                        shipment_dict[ship_id] = ship_data
                except Exception:
                    pass
    formatted_date = arrival_date.strftime("%d %B %Y")
    print(f"\nManifest for {matched_vessel.get("name")} | Call {call_id} | {formatted_date}")

    shipment_id = manifest_data.get("shipment_ids",[])
    declared_shipment = len(manifest_data)
    resolved_weight = 0.0
    missing_records = 0

    for index, shipment_id in enumerate(shipment_id, start=1):
        if shipment_id in shipment_dict:
            ship = shipment_dict[shipment_id]
            company = ship.get("customer","")

            try:
                weight = float(ship.get("weight_kg",0.0))
            except ValueError:
                weight = 0.0
            resolved_weight += weight

            cargo_type = ship.get("cargo_type")
            if not cargo_type or cargo_type.strip == "":
                cargo_type = "NOT PROVIDED"
            else:
                cargo_type = cargo_type.upper()
            print(f"{index}. {shipment_id} | {company} | {weight:.1f} kg | {cargo_type}")
        else:
            print(f"{index}. {shipment_id} | MISSING RECORD")
            missing_records +=1

    print(f"\nDeclared shipment: {declared_shipment}")
    print(f"\nResolved weight: {resolved_weight:.2f} kg")
    print(f"\nMissing shipment records: {missing_records}")





#Task 5

#builds a dict from vessel ID to vessel names, skips broken files    
def load_vessel_names():
    vessel_names = {}

    for vessel_files in Path("dataset/vessels").glob("*.json"):
        try:
            with open(vessel_files, "r") as file:
                vessel = json.load(file)
            vessel_names[vessel["vessel_id"]] = vessel["name"]
        except (json.JSONDecodeError, KeyError):
            pass
    return vessel_names
                    
#Asks for a month from 1-12
def ask_month():
    valid = False
    while not valid:
        try:
            month = int(input("Month (1-12): "))
            if month > 12 or month < 1:
                print("Error - Enter a month from 1 to 12.")
            else:
                valid = True
        except ValueError:
            print("Error - Enter a month from 1 to 12.")
    return month

#Return valid port calls in month and sorts (date, vessel name, port, call id) in tuples
#Need to import date from datetime to check invalid dates
#date.fromisoformat makes the date of format YYYY-MM-DD
def find_port_calls_by_month(month, vessel_names):
    port_calls = data_access.load_csv("dataset/port_calls.csv")
    calls = []
    for row in port_calls:
        try:
            arrival = datetime.date.fromisoformat(row["arrival_date"])
            if arrival.month == month:
                if row["vessel_id"] in vessel_names:
                    call = (arrival, vessel_names[row["vessel_id"]], row["port_code"], row["call_id"])
                    calls.append(call)
                else:
                    print(f"Skipped call {row["call_id"]}: unknown vessel {row["vessel_id"]}")
        except ValueError:
            print(f"Skipped call {row["call_id"]}: invalid date {row["arrival_date"]}")
    calls.sort()
    return calls

#Prints port calls for month in format
def print_calls_in(month, calls):
    if len(calls) == 0:
        print("No port calls found.")
    else:
        month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        print(f"Port calls in {month_names[month - 1]}:")
        for arrival, vessel_name, port_code, call_id in calls:
            print(f"- {arrival.strftime("%d %B %Y")} | {vessel_name} | {port_code} | {call_id}")

#Task 6
def load_incidents():
    incidents = []
    for incident_file in Path("dataset/incidents").glob("*.json"):
        try:
            with open(incident_file, "r") as file:
                incident = json.load(file)
            if "incident_id" in incident and  "title" in incident and "report" in incident:
                incidents.append(incident)
        except json.JSONDecodeError:
            pass
    return incidents        

#Sort helper
def title_key(incident):
    return incident["title"].lower()

#prints incident titles in numbers from 1
def print_incident_titles(incidents):
    for number, incident in enumerate(incidents, start=1):
        print(f"{number}. {incident["title"]}")

#asks for incident number (whole number from 1)
def ask_incident(count):
    valid = False
    while not valid:
        try:
            choice = int(input("Select incident: "))
            if choice < 1 or choice > count:
                print("Error - Select a listed incident.")
            else:
                valid = True
        except ValueError:
            print("Error - Select a listed incident.")
    return choice

#Replace container ID, SEAL numbers and emails, returns text and if something changed
def sanitize_report(text):
    new_text = re.sub(r"[A-Za-z]{4}\d{7}", "[CONTAINER]", text)
    new_text = re.sub(r"SEAL-\d{6}", "[SEAL]", new_text, flags=re.IGNORECASE)
    new_text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[EMAIL]", new_text)
    changed = new_text != text
    return new_text, changed 

#Create the output directory when necessary
def save_sanitized_report(incident_id, text):
    folder = Path("exports/sanitized")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder/f"{incident_id}-sanitized.txt"
    with open(path, "w") as file:
        file.write(text)

    print(f"Sanitized report saved: {path}")
    
def main():
    """Start the terminal based application and prompt the user with options for calling other programs or closing the console.
    The cases are where the programs will be called. its based on the programs id.
    """

    run = True
    while run:
        program_id = get_number("""
        HARBORFLOW PORT INTELLIGENCE
        1. List registered vessels
        2. Inspect a vessel manifest
        3. Identify priority cargo
        4. Export a customer operations profile
        5. Find port calls by month
        6. Sanitize an incident report
        7. Analyze the longest stable event sequence
        8. Assess weather risk for upcoming calls
        9. Search incident reports
        10. Close console
        Select service: """, "Error - Select a service from 1 to 10.", int, 1, 10)

        match program_id:
            case 1:
                valid_vessels = list_registerd_vessels()
            case 2:
                Inspect_a_vessel_manifest(valid_vessels)
            case 3:
                identify_priority_cargo()
            case 4:
                pass
            case 5:
                month = ask_month()
                vessel_names = load_vessel_names()
                calls = find_port_calls_by_month(month, vessel_names)
                print_calls_in(month, calls)               
            case 6:
                incidents = load_incidents()
                incidents.sort(key=title_key)
                print_incident_titles(incidents)
                choice = ask_incident(len(incidents))
                incident = incidents[choice -1]
                    
                clean_text, changed = sanitize_report(incident["report"])
                if not changed:
                    print("Incident contains no share-sensitive identifiers.")
                else:
                    save_sanitized_report(incident["incident_id"], clean_text)
            case 7:
                run_event_sequence()
            case 8:
                run_weather_risk()
            case 9:
                run_incident_search()
            case 10:
                print("Console closed. Dispatch data remains safe.")
                run = False

def identify_priority_cargo():
    """Takes a port call and identifies the priority shipment catefories for each shipment"""

    call_id = input("Call id: ").strip().lower()

    calls = load_csv("dataset/port_calls.csv")
    call = next((c for c in calls if c["call_id"].strip().lower() == call_id), None)

    if call is None:
        print("Port call not found")
        return

    count = get_count(call["call_id"])
    print(f"Category totals: CONTROLLED={count["CONTROLLED"]}, COLD CHAIN={count["COLD CHAIN"]}, EXPEDITE={count["EXPEDITE"]}, STANDARD={count["STANDARD"]}")

def get_count(call_id):
    """Takes a call id, prints shippment id, priority category and reason for each attached shipment.
    ARGUMENTS:
    call_id (string): the port call id
    RETURNS:
    count (dict): the number of each category for the call id
    """
    count = {"CONTROLLED": 0, "COLD CHAIN": 0, "EXPEDITE": 0, "STANDARD": 0}
    manifest = data_access.load_json(f"dataset/manifests/{call_id}.json")
    for shipment_id in manifest["shipment_ids"]:
        file_name = "shipment-" + shipment_id[-4:]
        shipment = data_access.load_json(f"dataset/shipments/{file_name}.json")
        category, reason = classify_shipment(shipment)
        print(f"{shipment_id.upper()} | {category} | {reason}")

        count[category] += 1
    return count

def classify_shipment(shipment):
    """Classifys the shipments priority and reason'
    ARGUMENTS:
    shipment (dict)
    RETURNS:
    category (string)
    reason (string)
    """
    if shipment.get("hazardous", False):
        return "CONTROLLED", "hazardous cargo"
    if shipment.get("temperature_controlled", False):
        return "COLD CHAIN", "temperature controlled"
    if shipment["priority"] == "EXPRESS":
        return "EXPEDITE", "express service"
    if shipment["weight_kg"] >= 5000:
        return "EXPEDITE", "heavy cargo"
    return "STANDARD", "standard handling"

# Task 7
from text_tools import longest_stable_sequence
from data_access import find_manifest, call_exists


def run_event_sequence():
    call_id = input("Call ID: ").strip()

    if not call_exists(call_id):
        print("Port call not found.")
        return

    manifest = find_manifest(call_id)
    if manifest is None:
        print("Manifest unavailable.")
        return

    event_codes = manifest.get("event_codes")
    if not isinstance(event_codes, list) or not all(isinstance(e, str) for e in event_codes):
        print("Manifest unavailable.")
        return

    sequence = longest_stable_sequence(event_codes)

    print("Event codes: " + ",".join(event_codes))
    print("Longest stable sequence length: " + str(len(sequence)))
    print("Sequence: " + " -> ".join(sequence))


#task 8

from operations import (
    find_vessel_by_name,
    ask_valid_date,
    find_upcoming_calls,
    build_forecast_lookup,
    read_forecast,
    print_forecast,
)

def run_weather_risk():
    # TODO: temporary. list_registerd_vessels() also prints the vessel list.
    #       Replace with load_vessels() (returns the list without printing) once Task 1 splits it.
    #I will explain in meeting.
    vessels = list_registerd_vessels()

    name = input("Vessel name: ")
    vessel = find_vessel_by_name(name, vessels)
    if vessel is None:
        print("Vessel not found.")
        return

    reference_date = ask_valid_date()

    calls = load_csv("dataset/port_calls.csv")
    upcoming = find_upcoming_calls(calls, vessel["vessel_id"], reference_date)
    if not upcoming:
        print("No upcoming port calls found.")
        return

    upcoming.sort(key=lambda row: (row["arrival_date"], row["call_id"]))

    lookup = build_forecast_lookup(load_csv("dataset/weather.csv"))

    for call in upcoming:
        arrival = datetime.date.fromisoformat(call["arrival_date"])
        port = call["port_code"]

        forecast_row = lookup.get((port, call["arrival_date"]))
        if forecast_row is None:
            print(f"{vessel['name']} | {port} | {arrival.strftime('%d %B %Y')}")
            print("Forecast unavailable")
            continue

        values = read_forecast(forecast_row)
        if values is None:
            continue

        wind, rain, waves = values
        print_forecast(vessel["name"], port, arrival, wind, rain, waves)



#task 9
from operations import get_incident_index
from text_tools import search_incidents


def run_incident_search():
    index, titles = get_incident_index()
    query = input("Search incident reports: ")
    results = search_incidents(query, index, titles)

    print(f"Matches for '{query}':")
    for incident_id, score, title in results:
        print(f"- {incident_id} | score {score} | {title}")



if __name__ == "__main__":
    main()
