"""HarborFlow Assignment 2 starter entry point."""
import math
import json
import data_access
import os
import csv
from datetime import date
from pathlib import Path
import re

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

#Task 5
#Reads CSV file and returns rows as a list of dict
def load_csv(path):
    with open(path, "r", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        return rows

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
    port_calls = load_csv("dataset/port_calls.csv")
    calls = []
    for row in port_calls:
        try:
            arrival = date.fromisoformat(row["arrival_date"])
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
                print("Console closed. Dispatch data remains safe.")
                run = False
            case 2:
                pass
            case 3:
                pass
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
                pass
            case 8:
                pass
            case 9:
                pass
            case 10:
                pass
                
if __name__ == "__main__":
    main()
