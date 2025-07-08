import json
import os
import sys

# Ensure the current working directory is the src/api folder,
# and make sure imports work correctly regardless of where the script runs from.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from main import app

# Get the OpenAPI schema
openapi_schema = app.openapi()

# Write to file
output_dir = os.path.abspath(os.path.join(current_dir, "../../interfaces"))
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "openapi.json")

with open(output_path, "w") as f:
    json.dump(openapi_schema, f, indent=2)
