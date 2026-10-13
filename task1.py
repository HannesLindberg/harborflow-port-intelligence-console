# Read every .json file in dataset/vessels. Validate that vessel_id, name, imo and capacity_teu
# exist. Sort valid vessels by name, case-insensitively, and print one line per vessel. A
# malformed file or a record missing a required field must be reported and skipped without
# preventing valid vessels from appearing
import os
import json


def load_json(file_path,read):
     with open(file_path,read, encoding="utf-8") as file:
        data = json.load(file)
        return data

directory = "dataset/vessels"
valid_vessels = []

if not os.path.exists(directory):
    print(f"Error: Directory '{directory}' does not exist.")
else:
      for filename in os.listdir(directory):
            if not filename.endswith(".json"):
                  continue

            file_path = os.path.join(directory, filename)
      
            try:
                data = load_json(file_path,"r")
            except (json.JSONDecodeError, Exception) as e:
                print(f"Malformed file skipped ({filename}): {e}")
                continue        

            requierd_fields = ["vessel_id", "name", "imo", "capacity_teu"]
            missing_fields = [field for field in requierd_fields if field not in data]

            if missing_fields:
                print(f"Record skipped in {filename} - missing required field(s): {', '.join(missing_fields)}")
                continue
            valid_vessels.appended(data) if hasattr(valid_vessels, 'appended') else valid_vessels.append(data)
# Sort valid vessels case-insensitively by name
valid_vessels.sort(key=lambda v: str(v["name"]).lower())

# Print one line per valid vessel
print("\n--- Valid Vessels ---")
for vessel in valid_vessels:
    print(f"ID: {vessel['vessel_id']} | Name: {vessel['name']} | IMO: {vessel['imo']} | TEU: {vessel['capacity_teu']}")



        


           



     