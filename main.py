"""HarborFlow Assignment 2 starter entry point."""
import math
import json
import data_access
import os

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
