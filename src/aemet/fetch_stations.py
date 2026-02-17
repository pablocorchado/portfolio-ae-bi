import os
import json
from pathlib import Path

import requests
import pandas as pd
from dotenv import load_dotenv

BASE = "https://opendata.aemet.es/opendata/api"
STATIONS_ENDPOINT = "/valores/climatologicos/inventarioestaciones/todasestaciones/"

def aemet_get_json(api_key: str, path: str) -> list[dict]:
    """AEMET OpenData suele responder con una URL temporal en el campo 'datos'."""
    r = requests.get(f"{BASE}{path}", params={"api_key": api_key}, timeout=60)
    r.raise_for_status()
    meta = r.json()
    if "datos" not in meta:
        raise RuntimeError(f"Respuesta inesperada: {meta}")
    data_url = meta["datos"]
    d = requests.get(data_url, timeout=120)
    d.raise_for_status()
    return d.json()

def main():
    load_dotenv()
    api_key = os.getenv("AEMET_API_KEY")
    if not api_key:
        raise SystemExit("Falta AEMET_API_KEY en .env")

    out_dir = Path("data/raw/aemet")
    out_dir.mkdir(parents=True, exist_ok=True)

    stations = aemet_get_json(api_key, STATIONS_ENDPOINT)

    # Guardar raw JSON
    (out_dir / "stations.json").write_text(json.dumps(stations, ensure_ascii=False, indent=2), encoding="utf-8")

    # Guardar CSV “usable”
    df = pd.DataFrame(stations)
    df.to_csv(out_dir / "stations.csv", index=False, encoding="utf-8")

    print(f"OK: {len(df)} estaciones guardadas en {out_dir}")

if __name__ == "__main__":
    main()
