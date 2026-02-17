import duckdb

def main():
    con = duckdb.connect("data/weather.duckdb")

    print("\n[1] Fact sin dim_fecha (debería ser 0):")
    print(con.execute("""
        SELECT COUNT(*) AS missing_date_dim
        FROM gold.fact_meteo_diaria f
        LEFT JOIN gold.dim_fecha d ON f.date_key = d.date_key
        WHERE d.date_key IS NULL;
    """).fetchdf())

    print("\n[2] Fact sin dim_estacion (debería ser 0 o muy bajo):")
    print(con.execute("""
        SELECT COUNT(*) AS missing_station_dim
        FROM gold.fact_meteo_diaria f
        LEFT JOIN gold.dim_estacion s ON f.station_id = s.station_id
        WHERE s.station_id IS NULL;
    """).fetchdf())

    print("\n[3] Top provincias por filas (sanity check):")
    print(con.execute("""
        SELECT provincia, COUNT(*) AS rows
        FROM gold.fact_meteo_diaria
        GROUP BY 1
        ORDER BY rows DESC
        LIMIT 10;
    """).fetchdf())

    print("\n[4] Nulos en tmed/prec por provincia (top 10):")
    print(con.execute("""
        SELECT provincia,
               AVG(is_tmed_null) AS pct_tmed_null,
               AVG(is_prec_null) AS pct_prec_null
        FROM gold.fact_meteo_diaria
        GROUP BY 1
        ORDER BY pct_prec_null DESC
        LIMIT 10;
    """).fetchdf())

if __name__ == "__main__":
    main()
