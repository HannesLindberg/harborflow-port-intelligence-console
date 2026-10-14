"""File loading and path-handling functions for HarborFlow.

Create reusable JSON and CSV loaders here. Do not hard-code sample records.
"""
import json


#file loader funktion for json file 
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
          return json.load(file)

