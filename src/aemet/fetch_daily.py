import os
import json
from pathlib import Path
from urllib.parse import quote
from datetime import datetime, timedelta

import requests
import pandas as pd
from dotenv import load_dotenv

BASE = "https://opendata.aemet.es/opendata/api"


def aemet_get_json_url(api_key: str, api_path: str) -> str:
    r = requests.get(f"{BASE}{api_path}", params={"api_key": api_key}, timeout=60)
    r.raise_for_status()
    meta = r.json()
    if "datos" not in meta:
        raise RuntimeError(f"Respuesta inesperada: {meta}")
    return meta["datos"]


def safe_filename(s: str) -> str:
    return s.replace(":", "-").replace("/", "-")


def parse_date(d: str) -> datetime:
    # acepta "YYYY-MM-DD"
    return datetime.strptime(d, "%Y-%m-%d")


def to_aemet_utc(dt: datetime, end_of_day: bool = False) -> str:
    if end_of_day:
        return dt.strftime("%Y-%m-%dT23:59:59UTC")
    return dt.strftime("%Y-%m-%dT00:00:00UTC")


def daterange_chunks(start: datetime, end: datetime, max_days: int = 15):
    """
    Genera trozos [a, b] donde cada chunk tiene como mucho max_days (incluyendo ambos extremos).
    """
    cur = start
    while cur <= end:
        chunk_end = min(cur + timedelta(days=max_days - 1), end)
        yield cur, chunk_end
        cur = chunk_end + timedelta(days=1)


def fetch_chunk(api_key: str, chunk_start: datetime, chunk_end: datetime) -> list[dict]:
    fecha_ini = to_aemet_utc(chunk_start, end_of_day=False)
    fecha_fin = to_aemet_utc(chunk_end, end_of_day=True)

    fecha_ini_enc = quote(fecha_ini, safe="")
    fecha_fin_enc = quote(fecha_fin, safe="")

    api_path = (
        f"/valores/climatologicos/diarios/datos/"
        f"fechaini/{fecha_ini_enc}/fechafin/{fecha_fin_enc}/todasestaciones"
    )

    print(f"-> Chunk {chunk_start.date()} a {chunk_end.date()}")
    data_url = aemet_get_json_url(api_key, api_path)

    r = requests.get(data_url, timeout=300)
    r.raise_for_status()
    return r.json()


def main(
    start_date: str = "2024-01-01",
    end_date: str = "2024-01-31",
):
    load_dotenv()
    api_key = os.getenv("AEMET_API_KEY")
    if not api_key:
        raise SystemExit("Falta AEMET_API_KEY en .env")

    out_dir = Path("data/raw/aemet")
    out_dir.mkdir(parents=True, exist_ok=True)

    start = parse_date(start_date)
    end = parse_date(end_date)

    all_dfs = []

    for a, b in daterange_chunks(start, end, max_days=15):
        try:
            data = fetch_chunk(api_key, a, b)
        except Exception as e:
            # si un chunk falla, lo reportamos y seguimos (luego lo reintentamos si hace falta)
            print(f"!! Falló chunk {a.date()} a {b.date()}: {e}")
            continue

        ini_fn = safe_filename(to_aemet_utc(a, False))
        fin_fn = safe_filename(to_aemet_utc(b, True))

        # guardar raw json del chunk (opcional)
        raw_path = out_dir / f"daily_{ini_fn}_to_{fin_fn}.json"
        raw_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        df = pd.DataFrame(data)
        csv_path = out_dir / f"daily_{a.date()}_to_{b.date()}.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8")

        print(f"   OK: {len(df)} filas -> {csv_path}")
        all_dfs.append(df)

    if not all_dfs:
        raise RuntimeError("No se descargó ningún chunk. Revisa la API key o el rango de fechas.")

    final = pd.concat(all_dfs, ignore_index=True)

    combined_path = out_dir / f"daily_combined_{start_date}_to_{end_date}.csv"
    final.to_csv(combined_path, index=False, encoding="utf-8")

    print(f"\nOK FINAL: {len(final)} filas combinadas -> {combined_path}")


if __name__ == "__main__":
    main("2025-10-01", "2025-10-31")
