import duckdb

def main():
    con = duckdb.connect("data/weather.duckdb")

    print("\n[1] Filas RAW:")
    print(con.execute("SELECT COUNT(*) AS rows FROM raw.aemet_daily;").fetchdf())

    print("\n[2] Filas SILVER:")
    print(con.execute("SELECT COUNT(*) AS rows FROM silver.meteo_daily;").fetchdf())

    print("\n[3] Fechas nulas tras parseo (debería ser 0):")
    print(con.execute("""
        SELECT COUNT(*) AS bad_dates
        FROM silver.meteo_daily
        WHERE fecha IS NULL;
    """).fetchdf())

    print("\n[4] Duplicados por (indicativo, fecha):")
    print(con.execute("""
        SELECT indicativo, fecha, COUNT(*) AS n
        FROM silver.meteo_daily
        GROUP BY 1,2
        HAVING COUNT(*) > 1
        ORDER BY n DESC
        LIMIT 10;
    """).fetchdf())

    print("\n[5] Rango fechas y cobertura:")
    print(con.execute("""
        SELECT MIN(fecha) AS min_fecha, MAX(fecha) AS max_fecha,
               COUNT(DISTINCT indicativo) AS estaciones
        FROM silver.meteo_daily;
    """).fetchdf())

    print("\n[6] Nulos en métricas principales (tmed/prec):")
    print(con.execute("""
        SELECT
          SUM(CASE WHEN tmed IS NULL THEN 1 ELSE 0 END) AS null_tmed,
          SUM(CASE WHEN prec IS NULL THEN 1 ELSE 0 END) AS null_prec
        FROM silver.meteo_daily;
    """).fetchdf())

if __name__ == "__main__":
    main()
