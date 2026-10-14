# Read every .json file in dataset/vessels. Validate that vessel_id, name, imo and capacity_teu
# exist. Sort valid vessels by name, case-insensitively, and print one line per vessel. A
# malformed file or a record missing a required field must be reported and skipped without
# preventing valid vessels from appearing
import os
import json

#file loader funktion for json file 
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
          return json.load(file)

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
                    data = load_json(file_path) 
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

list_registerd_vessels()