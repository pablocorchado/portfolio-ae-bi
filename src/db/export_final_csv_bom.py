import duckdb
from pathlib import Path

def main():
    con = duckdb.connect("data/weather.duckdb")

    out_dir = Path("data/gold")
    out_dir.mkdir(parents=True, exist_ok=True)

    df = con.execute("SELECT * FROM gold.turismo_meteo_ccaa_mes ORDER BY ccaa;").fetchdf()
    out_path = out_dir / "turismo_meteo_ccaa_mes_utf8_bom.csv"
    df.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"OK: export (UTF-8 BOM) -> {out_path} ({len(df)} filas)")

if __name__ == "__main__":
    main()
