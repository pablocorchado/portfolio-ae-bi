import duckdb

def main():
    con = duckdb.connect("data/weather.duckdb")
    con.execute("CREATE SCHEMA IF NOT EXISTS gold;")

    con.execute("DROP TABLE IF EXISTS gold.turismo_meteo_ccaa_mes;")
    con.execute("""
        CREATE TABLE gold.turismo_meteo_ccaa_mes AS
        WITH turismo_pivot AS (
          SELECT
            -- Normaliza nombres INE -> estándar de nuestro meteo
            CASE
              WHEN ccaa = 'Asturias, Principado de' THEN 'Asturias'
              WHEN ccaa = 'Balears, Illes' THEN 'Illes Balears'
              WHEN ccaa = 'Castilla - La Mancha' THEN 'Castilla-La Mancha'
              WHEN ccaa = 'Madrid, Comunidad de' THEN 'Comunidad de Madrid'
              WHEN ccaa = 'Murcia, Región de' THEN 'Región de Murcia'
              WHEN ccaa = 'Navarra, Comunidad Foral de' THEN 'Navarra'
              WHEN ccaa = 'Comunidad Foral de Navarra' THEN 'Navarra'
              WHEN ccaa = 'Rioja, La' THEN 'La Rioja'
              ELSE ccaa
            END AS ccaa_norm,
            year_month,
            MAX(CASE WHEN metric = 'Viajero' THEN value END) AS viajeros,
            MAX(CASE WHEN metric = 'Pernoctaciones' THEN value END) AS pernoctaciones
          FROM gold.turismo_ccaa_mes
          GROUP BY 1,2
        ),
        meteo_norm AS (
          SELECT
            ccaa AS ccaa_norm,
            year_month,
            tmed_avg_month,
            prec_sum_month,
            active_stations_sum
          FROM gold.meteo_ccaa_mes
        )
        SELECT
          t.ccaa_norm AS ccaa,
          t.year_month,
          t.viajeros,
          t.pernoctaciones,
          CASE WHEN t.viajeros > 0 THEN CAST(t.pernoctaciones AS DOUBLE) / t.viajeros ELSE NULL END AS pernoct_por_viajero,
          m.tmed_avg_month,
          m.prec_sum_month,
          m.active_stations_sum
        FROM turismo_pivot t
        LEFT JOIN meteo_norm m
          ON t.ccaa_norm = m.ccaa_norm
         AND t.year_month = m.year_month;
    """)

    print("OK: gold.turismo_meteo_ccaa_mes creado")
    print(con.execute("""
        SELECT
          COUNT(*) AS rows,
          SUM(CASE WHEN tmed_avg_month IS NULL THEN 1 ELSE 0 END) AS rows_without_meteo
        FROM gold.turismo_meteo_ccaa_mes;
    """).fetchdf())

    print("\nMuestra:")
    print(con.execute("""
        SELECT *
        FROM gold.turismo_meteo_ccaa_mes
        ORDER BY ccaa
        LIMIT 10;
    """).fetchdf())

if __name__ == "__main__":
    main()
