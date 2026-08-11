import hashlib
import json
from typing import Dict, Any


def compute_trail_pack_checksum(pack_dict: Dict[str, Any]) -> str:
    """
    Computes a canonical SHA-256 checksum for a trail-pack JSON payload.
    The checksum excludes the `integrity` block itself to prevent recursive hashing.
    Keys are sorted and compact separators are used for deterministic byte encoding.
    """
    # Deep copy or omit integrity block
    payload_copy = {k: v for k, v in pack_dict.items() if k != "integrity"}
    
    # Canonical JSON string serialization
    canonical_json = json.dumps(payload_copy, sort_keys=True, separators=(",", ":"))
    
    # Calculate SHA-256 hash
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
