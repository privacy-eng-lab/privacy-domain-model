import yaml
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "domain"

def load_yaml(name: str):
    path = BASE / name
    with open(path, "r") as f:
        return yaml.safe_load(f)

def test_unique_ids():
    """Check that IDs are unique within each YAML file."""
    for file in BASE.glob("*.yaml"):
        data = load_yaml(file.name)
        if not isinstance(data, list):
            continue
        seen = set()
        for item in data:
            if "id" in item:
                assert item["id"] not in seen, f"Duplicate id '{item['id']}' in {file.name}"
                seen.add(item["id"])

def test_purposes_references():
    """Ensure purposes.yaml references valid legal bases, subjects, and categories."""
    purposes = {p["id"]: p for p in load_yaml("purposes.yaml")}
    legal_bases = {b["id"] for b in load_yaml("legal_bases.yaml")}
    categories = {c["id"] for c in load_yaml("data_categories.yaml")}
    subjects = {s["id"] for s in load_yaml("data_subjects.yaml")}

    for pid, p in purposes.items():
        for lb in p.get("compatible_bases", []):
            assert lb in legal_bases, f"Unknown legal basis '{lb}' in purpose {pid}"
        for cat in p.get("typical_categories", []):
            assert cat in categories, f"Unknown category '{cat}' in purpose {pid}"
        for subj in p.get("typical_subjects", []):
            assert subj in subjects, f"Unknown subject '{subj}' in purpose {pid}"

def test_processing_activities_references():
    """Ensure processing_activities.yaml references valid purposes, bases, subjects, and categories."""
    activities = load_yaml("processing_activities.yaml")
    purposes = {p["id"] for p in load_yaml("purposes.yaml")}
    legal_bases = {b["id"] for b in load_yaml("legal_bases.yaml")}
    categories = {c["id"] for c in load_yaml("data_categories.yaml")}
    subjects = {s["id"] for s in load_yaml("data_subjects.yaml")}

    for a in activities:
        for p in a.get("purposes", []):
            assert p in purposes, f"Unknown purpose '{p}' in activity {a['id']}"
        lb = a.get("default_legal_basis")
        if lb:
            assert lb in legal_bases, f"Unknown legal basis '{lb}' in activity {a['id']}"
        for cat in a.get("data_categories", []):
            assert cat in categories, f"Unknown category '{cat}' in activity {a['id']}"
        for subj in a.get("data_subjects", []):
            assert subj in subjects, f"Unknown subject '{subj}' in activity {a['id']}"
