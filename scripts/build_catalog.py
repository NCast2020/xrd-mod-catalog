"""Validates mods/*.json and writes catalog.json (the single file the app downloads).

Run with --check on pull requests: validates only, writes nothing.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODS = os.path.join(ROOT, "mods")
REQUIRED = {"id": str, "name": str, "uploader": str, "version": str, "url": str, "size": int, "sha256": str, "updated": str}

def load(path):
    with open(path, encoding="utf-8-sig") as f:
        e = json.load(f)
    name = os.path.basename(path)
    for key, kind in REQUIRED.items():
        if not isinstance(e.get(key), kind):
            raise ValueError(f"{name}: field '{key}' must be a {kind.__name__}")
    if name != e["id"] + ".json":
        raise ValueError(f"{name}: file name must be <id>.json (id is '{e['id']}')")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", e["id"]):
        raise ValueError(f"{name}: id may only use a-z, 0-9 and '-'")
    if not e["url"].startswith("https://github.com/"):
        raise ValueError(f"{name}: url must point to a GitHub release")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", e["sha256"]):
        raise ValueError(f"{name}: sha256 must be 64 hex characters")
    if e["size"] <= 0:
        raise ValueError(f"{name}: size must be positive")
    return e

def main():
    errors, entries = [], []
    for f in sorted(os.listdir(MODS)):
        if f.endswith(".json"):
            try:
                entries.append(load(os.path.join(MODS, f)))
            except Exception as ex:
                errors.append(str(ex))
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    entries.sort(key=lambda e: e["updated"], reverse=True)
    print(f"{len(entries)} mod(s) OK")
    if "--check" not in sys.argv:
        with open(os.path.join(ROOT, "catalog.json"), "w", encoding="utf-8") as f:
            json.dump({"version": 1, "mods": entries}, f, ensure_ascii=False, indent=1)
            f.write("\n")

main()
