import duckdb

def main():
    con = duckdb.connect("data/weather.duckdb")

    con.execute("DROP TABLE IF EXISTS gold.meteo_provincia_mes;")
    con.execute("""
        CREATE TABLE gold.meteo_provincia_mes AS
        WITH base AS (
            SELECT
                f.provincia,
                d.year,
                d.month,
                d.year_month,
                f.date_key,
                f.station_id,
                f.tmed,
                f.prec,
                f.is_tmed_null,
                f.is_prec_null
            FROM gold.fact_meteo_diaria f
            JOIN gold.dim_fecha d
              ON f.date_key = d.date_key
        )
        SELECT
            provincia,
            year,
            month,
            year_month,

            COUNT(DISTINCT date_key) AS days_in_month_with_data,
            COUNT(DISTINCT station_id) AS active_stations,

            AVG(tmed) AS tmed_avg_month,
            SUM(prec) AS prec_sum_month,

            AVG(is_tmed_null) AS pct_tmed_null,
            AVG(is_prec_null) AS pct_prec_null
        FROM base
        GROUP BY 1,2,3,4;
    """)

    print("OK: gold.meteo_provincia_mes creado")
    print(con.execute("""
        SELECT COUNT(*) AS rows,
               MIN(year_month) AS min_ym,
               MAX(year_month) AS max_ym
        FROM gold.meteo_provincia_mes;
    """).fetchdf())

    print("\nTop 10 provincias por prec_sum_month (sanity):")
    print(con.execute("""
        SELECT provincia, year_month, prec_sum_month
        FROM gold.meteo_provincia_mes
        ORDER BY prec_sum_month DESC
        LIMIT 10;
    """).fetchdf())

if __name__ == "__main__":
    main()
