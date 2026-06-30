from pathlib import Path
import yaml

def load_battles_schema(filename: str) -> dict:
    path = Path(__file__).parent.parent / "schemas" / filename
    with path.open(mode="r", encoding="utf-8") as f:
        return yaml.safe_load(f)