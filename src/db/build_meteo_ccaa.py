import duckdb

def main():
    con = duckdb.connect("data/weather.duckdb")
    con.execute("CREATE SCHEMA IF NOT EXISTS gold;")

    # 1) Mapping provincia -> CCAA
    con.execute("DROP TABLE IF EXISTS gold.map_provincia_ccaa;")
    con.execute("""
        CREATE TABLE gold.map_provincia_ccaa AS
        SELECT * FROM (VALUES
          ('A CORUÑA','Galicia'),('LUGO','Galicia'),('OURENSE','Galicia'),('PONTEVEDRA','Galicia'),
          ('ASTURIAS','Asturias'),
          ('CANTABRIA','Cantabria'),

          -- País Vasco (variantes)
          ('BIZKAIA','País Vasco'),('GIPUZKOA','País Vasco'),
          ('ARABA/ALAVA','País Vasco'),('ALAVA','País Vasco'),('ARABA','País Vasco'),

          ('NAVARRA','Navarra'),
          ('LA RIOJA','La Rioja'),

          ('HUESCA','Aragón'),('ZARAGOZA','Aragón'),('TERUEL','Aragón'),

          ('LLEIDA','Cataluña'),('GIRONA','Cataluña'),('BARCELONA','Cataluña'),('TARRAGONA','Cataluña'),

          ('MADRID','Comunidad de Madrid'),

          ('AVILA','Castilla y León'),('BURGOS','Castilla y León'),('LEON','Castilla y León'),
          ('PALENCIA','Castilla y León'),('SALAMANCA','Castilla y León'),('SEGOVIA','Castilla y León'),
          ('SORIA','Castilla y León'),('VALLADOLID','Castilla y León'),('ZAMORA','Castilla y León'),

          ('ALBACETE','Castilla-La Mancha'),('CIUDAD REAL','Castilla-La Mancha'),('CUENCA','Castilla-La Mancha'),
          ('GUADALAJARA','Castilla-La Mancha'),('TOLEDO','Castilla-La Mancha'),

          ('CACERES','Extremadura'),('BADAJOZ','Extremadura'),

          ('ALICANTE','Comunitat Valenciana'),('CASTELLON','Comunitat Valenciana'),('VALENCIA','Comunitat Valenciana'),

          ('MURCIA','Región de Murcia'),

          ('ALMERIA','Andalucía'),('CADIZ','Andalucía'),('CORDOBA','Andalucía'),('GRANADA','Andalucía'),
          ('HUELVA','Andalucía'),('JAEN','Andalucía'),('MALAGA','Andalucía'),('SEVILLA','Andalucía'),

          -- Baleares (variantes)
          ('BALEARES','Illes Balears'),
          ('ILLES BALEARS','Illes Balears'),

          -- Canarias (variantes)
          ('LAS PALMAS','Canarias'),
          ('SANTA CRUZ DE TENERIFE','Canarias'),
          ('STA. CRUZ DE TENERIFE','Canarias'),

          ('CEUTA','Ceuta'),
          ('MELILLA','Melilla')
        ) AS t(provincia, ccaa);
    """)

    # 2) Agregación provincia_mes -> ccaa_mes
    con.execute("DROP TABLE IF EXISTS gold.meteo_ccaa_mes;")
    con.execute("""
        CREATE TABLE gold.meteo_ccaa_mes AS
        WITH joined AS (
          SELECT
            mp.ccaa,
            p.year,
            p.month,
            p.year_month,
            p.days_in_month_with_data,
            p.active_stations,
            p.tmed_avg_month,
            p.prec_sum_month
          FROM gold.meteo_provincia_mes p
          LEFT JOIN gold.map_provincia_ccaa mp
            ON p.provincia = mp.provincia
        )
        SELECT
          ccaa,
          year,
          month,
          year_month,
          SUM(days_in_month_with_data) AS days_rows_sum,
          SUM(active_stations) AS active_stations_sum,
          AVG(tmed_avg_month) AS tmed_avg_month,
          SUM(prec_sum_month) AS prec_sum_month
        FROM joined
        WHERE ccaa IS NOT NULL
        GROUP BY 1,2,3,4;
    """)

    print("OK: gold.meteo_ccaa_mes creado")
    print(con.execute("""
        SELECT COUNT(*) AS rows, MIN(year_month) AS min_ym, MAX(year_month) AS max_ym
        FROM gold.meteo_ccaa_mes;
    """).fetchdf())

    # Checks
    print("\nFilas provincia_mes:", con.execute("SELECT COUNT(*) FROM gold.meteo_provincia_mes;").fetchone()[0])
    print("Filas ccaa_mes:", con.execute("SELECT COUNT(*) FROM gold.meteo_ccaa_mes;").fetchone()[0])

    print("\nProvincias sin mapping (si sale alguna, la arreglamos):")
    print(con.execute("""
        SELECT DISTINCT p.provincia
        FROM gold.meteo_provincia_mes p
        LEFT JOIN gold.map_provincia_ccaa mp
          ON p.provincia = mp.provincia
        WHERE mp.ccaa IS NULL
        ORDER BY p.provincia;
    """).fetchdf())

if __name__ == "__main__":
    main()
