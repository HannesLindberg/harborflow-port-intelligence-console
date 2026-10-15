"""HarborFlow Assignment 2 starter entry point."""
import math
import json
import data_access
import os
import re
import datetime

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
    valid_vessels.sort(key=lambda vessel: str(vessel["name"]).lower())
    

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
    return valid_vessels, skipped_count
    





#help funktion for task 2
def validate_date(date_time):
    try:
        datetime.date.fromisoformat(date_time)
        return True
    except ValueError:
        return False
#help funktion for task 2
def find_vessel(vessel_name, valid_vessels):
    cleaned_name = vessel_name.strip().lower()
    for vessel in valid_vessels:
        if str(vessel.get("name","")).strip().lower() == cleaned_name:
            return vessel
    return None


#task 2
def Inspect_a_vessel_manifest(valid_vessels, skipped_count):
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
        return

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
        return

    #sort calls by (earliest first so by date)
    matching_calls.sort()
    earliest_call = matching_calls[0][2]
    call_id = earliest_call["call_id"]
    arrival_date = datetime.date.fromisoformat(earliest_call["arrival_date"])

    manifest_path = (f"dataset/manifest/{call_id}.csv")
    if not os.path.exists(manifest_path):
            print(f"Error: Directory {manifest_path} does not exist.")
            return
    try:
        manifest_data = data_access.load_csv(manifest_path)
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
                    ship_id = ship_data("shipment_id")
                    if ship_id:
                        shipment_dict[ship_id] = ship_id
                except Exception:
                    pass
    formatted_date = arrival_date.strftime("%d %B %Y")
    print(f"\nManifest for {matched_vessel.get("name")} | Call {call_id} | {formatted_date}")

    declared_shipment = len(manifest_data)
    resolved_weight = 0.0
    missing_records = 0

    for index, item in enumerate(manifest_data, start=1):
        shipment_id = item.get("shipment_id")

        if shipment_id in shipment_dict:
            ship = shipment_dict[shipment_id]
            company = ship.get("company_name","")

            try:
                weight = float(ship.get("weight",0.0))
            except ValueError:
                weight = 0.0
            resolved_weight += weight

            cargo_type = ship.get("cargo_type")
            if not cargo_type or cargo_type.strip == (""):
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
               pass
            case 6:
                pass
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
