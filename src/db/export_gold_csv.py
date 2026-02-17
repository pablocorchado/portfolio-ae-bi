import duckdb
from pathlib import Path

def main():
    con = duckdb.connect("data/weather.duckdb")
    out_dir = Path("data/gold")
    out_dir.mkdir(parents=True, exist_ok=True)

    tables = [
        ("gold.dim_fecha", "dim_fecha.csv"),
        ("gold.dim_estacion", "dim_estacion.csv"),
        ("gold.meteo_provincia_mes", "meteo_provincia_mes.csv"),
    ]

    for table, filename in tables:
        df = con.execute(f"SELECT * FROM {table}").fetchdf()
        path = out_dir / filename
        df.to_csv(path, index=False, encoding="utf-8")
        print(f"OK: {table} -> {path} ({len(df)} filas)")

if __name__ == "__main__":
    main()
