import json
from typing import Union


def write_json(data: Union[list, dict], filepath: str):
    # Convert dictionary to JSON string
    json_data = json.dumps(data)

    # Write JSON string to file
    with open(filepath, "w") as outfile:
        outfile.write(json_data)
