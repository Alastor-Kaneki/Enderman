"""Resolve Java blockstate variants and multipart conditions (offline tooling)."""
import json
import random
import zipfile

def matches(condition, state):
    if "OR" in condition:
        return any(matches(x, state) for x in condition["OR"])
    if "AND" in condition:
        return all(matches(x, state) for x in condition["AND"])
    return all(str(state.get(k, "")).lower() in str(v).lower().split("|") for k, v in condition.items())

def select(entry, rng):
    if isinstance(entry, dict):
        return entry
    if not isinstance(entry, list) or not entry:
        raise ValueError("Invalid model variant")
    weights = [max(0, int(x.get("weight", 1))) for x in entry]
    if not any(weights):
        raise ValueError("No positive variant weights")
    return rng.choices(entry, weights=weights, k=1)[0]

def resolve(archive, block, state=None, seed=0):
    state = state or {}
    namespace, name = block.split(":", 1) if ":" in block else ("minecraft", block)
    with zipfile.ZipFile(archive) as z:
        doc = json.loads(z.read(f"assets/{namespace}/blockstates/{name}.json"))
    rng = random.Random(seed)
    result = []
    if "variants" in doc:
        for key, entry in doc["variants"].items():
            criteria = dict(x.split("=", 1) for x in key.split(",") if x)
            if all(str(state.get(k)) == v for k, v in criteria.items()):
                result.append(select(entry, rng))
                break
        else:
            raise ValueError(f"No matching variant: {block} {state}")
    for part in doc.get("multipart", []):
        if "when" not in part or matches(part["when"], state):
            result.append(select(part["apply"], rng))
    return result
