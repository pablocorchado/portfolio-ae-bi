import duckdb

def main():
    con = duckdb.connect("data/weather.duckdb")
    con.execute("CREATE SCHEMA IF NOT EXISTS gold;")

    # 1) dim_fecha
    con.execute("DROP TABLE IF EXISTS gold.dim_fecha;")
    con.execute("""
        CREATE TABLE gold.dim_fecha AS
        WITH fechas AS (
            SELECT DISTINCT fecha
            FROM silver.meteo_daily
            WHERE fecha IS NOT NULL
        )
        SELECT
            fecha AS date_key,
            EXTRACT(year  FROM fecha) AS year,
            EXTRACT(month FROM fecha) AS month,
            EXTRACT(day   FROM fecha) AS day,
            EXTRACT(dow   FROM fecha) AS dow,
            STRFTIME(fecha, '%Y-%m') AS year_month,
            CASE
              WHEN EXTRACT(month FROM fecha) IN (12,1,2) THEN 'invierno'
              WHEN EXTRACT(month FROM fecha) IN (3,4,5)  THEN 'primavera'
              WHEN EXTRACT(month FROM fecha) IN (6,7,8)  THEN 'verano'
              ELSE 'otono'
            END AS season
        FROM fechas;
    """)

    # 2) dim_estacion (desde inventario raw)
    con.execute("DROP TABLE IF EXISTS gold.dim_estacion;")
    con.execute("""
        CREATE TABLE gold.dim_estacion AS
        SELECT
            indicativo AS station_id,
            nombre     AS station_name,
            provincia,
            -- latitud/longitud vienen como texto tipo "412356N" / "0021234W" en algunos casos
            latitud,
            longitud,
            altitud
        FROM raw.aemet_stations;
    """)

    # 3) fact_meteo_diaria (silver + claves)
    con.execute("DROP TABLE IF EXISTS gold.fact_meteo_diaria;")
    con.execute("""
        CREATE TABLE gold.fact_meteo_diaria AS
        SELECT
            s.fecha AS date_key,
            s.indicativo AS station_id,
            s.provincia,
            s.tmed, s.tmin, s.tmax, s.prec,
            s.velmedia, s.racha,

            -- flags útiles para calidad/BI
            CASE WHEN s.tmed IS NULL THEN 1 ELSE 0 END AS is_tmed_null,
            CASE WHEN s.prec IS NULL THEN 1 ELSE 0 END AS is_prec_null
        FROM silver.meteo_daily s
        WHERE s.fecha IS NOT NULL
          AND s.indicativo IS NOT NULL;
    """)

    # Controles rápidos
    print("OK: GOLD creado")
    print(con.execute("""
        SELECT
          (SELECT COUNT(*) FROM gold.dim_fecha) AS dim_fecha_rows,
          (SELECT COUNT(*) FROM gold.dim_estacion) AS dim_estacion_rows,
          (SELECT COUNT(*) FROM gold.fact_meteo_diaria) AS fact_rows;
    """).fetchdf())

if __name__ == "__main__":
    main()
