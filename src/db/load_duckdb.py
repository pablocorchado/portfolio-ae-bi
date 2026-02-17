from pathlib import Path
import duckdb

def pick_latest_combined_csv() -> Path:
    files = sorted(Path("data/raw/aemet").glob("daily_combined_*.csv"))
    if not files:
        raise FileNotFoundError("No encuentro data/raw/aemet/daily_combined_*.csv")
    # orden lexicográfico funciona porque el nombre lleva YYYY-MM-DD
    return files[-1]

def main():
    db_path = Path("data/weather.duckdb")
    con = duckdb.connect(str(db_path))

    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    con.execute("CREATE SCHEMA IF NOT EXISTS silver;")

    stations_csv = Path("data/raw/aemet/stations.csv")
    combined_csv = pick_latest_combined_csv()

    if not stations_csv.exists():
        raise FileNotFoundError(f"No existe {stations_csv}")

    print(f"Usando combined CSV: {combined_csv}")

    # RAW
    con.execute("DROP TABLE IF EXISTS raw.aemet_stations;")
    con.execute(f"""
        CREATE TABLE raw.aemet_stations AS
        SELECT * FROM read_csv_auto('{stations_csv.as_posix()}');
    """)

    con.execute("DROP TABLE IF EXISTS raw.aemet_daily;")
    con.execute(f"""
        CREATE TABLE raw.aemet_daily AS
        SELECT * FROM read_csv_auto('{combined_csv.as_posix()}');
    """)

    print("OK: RAW cargado (raw.aemet_stations, raw.aemet_daily)")

    # SILVER
    con.execute("DROP TABLE IF EXISTS silver.meteo_daily;")
    con.execute("""
        CREATE TABLE silver.meteo_daily AS
        SELECT
            TRY_CAST(fecha AS DATE) AS fecha,
            indicativo,
            nombre,
            provincia,

            TRY_CAST(REPLACE(tmed, ',', '.') AS DOUBLE) AS tmed,
            TRY_CAST(REPLACE(tmin, ',', '.') AS DOUBLE) AS tmin,
            TRY_CAST(REPLACE(tmax, ',', '.') AS DOUBLE) AS tmax,
            TRY_CAST(REPLACE(prec, ',', '.') AS DOUBLE) AS prec,

            TRY_CAST(REPLACE(velmedia, ',', '.') AS DOUBLE) AS velmedia,
            TRY_CAST(REPLACE(racha, ',', '.') AS DOUBLE) AS racha
        FROM raw.aemet_daily;
    """)

    print("OK: SILVER creado (silver.meteo_daily)")

if __name__ == "__main__":
    main()
