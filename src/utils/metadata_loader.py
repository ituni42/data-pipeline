from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

#reads metadata json file
def load_metadata(path: Optional[str] = None) -> Dict[str, Any]:
    path = path or os.getenv("METADATA_PATH")

    if not path:
        raise ValueError(
            "No metadata path provided. Pass a path or set METADATA_PATH env variable"
        )

    if not os.path.exists(path):
        raise FileNotFoundError(f"Metadata file not found at: {path}")

    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Metadata file is not valid JSON: {e}")

#returns dataflow with wanted name from dictionary 
def get_dataflow(metadata: Dict[str, Any], name: str) -> Dict[str, Any]:
    for dataflow in metadata["dataflows"]:
        if dataflow["name"] == name:
            return dataflow
    raise ValueError(f"No dataflow named '{name}' found in metadata.")
