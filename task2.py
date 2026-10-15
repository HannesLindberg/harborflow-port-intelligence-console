# Display registered vessels, ask for a vessel name and a reference date in YYYY-MM-DD
# format. Remove surrounding spaces from the name and match it case-insensitively. Filter
# port calls to that vessel, then locate the earliest call on or after the reference date. Load the
# matching manifest through call_id, then resolve every shipment_id against
# dataset/shipments. Print the call, totals and cargo lines in manifest order. A missing
# shipment is listed as MISSING RECORD and counted separately. If several calls share the
# earliest date, choose the call with the alphabetically smallest call_id. For an invalid date,
# print Error - Date must use YYYY-MM-DD. and repeat only the date prompt. For an unknown
# vessel, print Vessel not found. If no qualifying call exists, print No upcoming port calls found.
# If the selected call has no readable valid manifest, print Manifest unavailable. In these three
# cases, return to the menu.
import data_access
import os
import datetime



def validate_date(date_time):
    try:
        datetime.date.fromisoformat(date_time)
        return True
    except ValueError:
        return False

def find_vessel(vessel_name, valid_vessels):
    cleaned_name = vessel_name.strip().lower()
    for vessel in valid_vessels:
        if str(vessel.get("name","")).strip().lower() == cleaned_name:
            return vessel
    return None


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
    formatted_date = arrival_date.strftime("%d %B % Y")
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


