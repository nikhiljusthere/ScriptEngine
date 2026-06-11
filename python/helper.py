from pathlib import Path
import json
root = Path(__file__).resolve().parents[1] 
paths_file = root / "constants.json"

def get_scrapped_data_dir():
    
    if not paths_file.exists():
        raise FileNotFoundError(f"constants.json not found at {paths_file}")

    config = json.loads(paths_file.read_text(encoding="utf-8"))

    crawl_dir = Path(config["crawl_ingestion_data_dir"])
    print(root / crawl_dir)

    return  root / crawl_dir