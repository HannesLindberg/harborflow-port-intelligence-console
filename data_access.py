"""File loading and path-handling functions for HarborFlow.

Create reusable JSON and CSV loaders here. Do not hard-code sample records.
"""
import json
import csv
from pathlib import Path


#file loader funktion for json file 
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
          return json.load(file)


#file loader for csv files that returns a list where every element is one dict row
def load_csv(file_path):
    data_list = []
    with open(file_path, mode="r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data_list.append(dict(row))
    return data_list



#for task 7
def find_manifest(call_id):
    #loops over dataset/manifests/*.json, skips malformed files, 
    # and returns the manifest whose call_id field matches (case-insensitive)
    for path in Path("dataset/manifests").glob("*.json"):
        try: 
            data = load_json(path)
        except json.JSONDecodeError:
            continue

        if not isinstance(data, dict):
            continue

        file_call_id = data.get("call_id")
        if isinstance(file_call_id, str) and file_call_id.upper() == call_id.upper():
            return data      

    return None



#for task 9
def load_incidents(directory="dataset/incidents"):
    #reads valid incident JSON files and skips malformed ones.
    incidents = []
    required = ["incident_id", "call_id", "title", "report"]
    for path in Path(directory).glob("*.json"):
        try:
            data = load_json(path)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        if not all(field in data for field in required):
            continue
        if not isinstance(data["report"], str):
            continue
        incidents.append(data)
    return incidents


#for task 9
def save_index(index, titles, path="dataset/incident-index.json"):
    #writes both to dataset/incident-index.json with sorted keys and sorted ID lists.
    for word in index:
        index[word].sort()
    data = {"index": index, "titles": titles}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)



#for task 9
def load_cached_index(path="dataset/incident-index.json",
                      incidents_dir="dataset/incidents"):
    #returns the cache only if the file exists, 
    #is valid JSON with index and titles, and is newer than every incident file.
    try:
        cache_time = Path(path).stat().st_mtime
        data = load_json(path)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    if not isinstance(data, dict) or "index" not in data or "titles" not in data:
        return None

    for incident_path in Path(incidents_dir).glob("*.json"):
        if incident_path.stat().st_mtime > cache_time:
            return None

    return data["index"], data["titles"]




#for task 7
def call_exists(call_id):
    #Checks port_calls.csv for the call.
    rows = load_csv("dataset/port_calls.csv")
    call_id = call_id.strip().lower()
    for row in rows:
        if row.get("call_id", "").strip().lower() == call_id:
            return True
    return False
