from pathlib import Path
import duckdb

def main():
    con = duckdb.connect("data/weather.duckdb")
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    con.execute("CREATE SCHEMA IF NOT EXISTS gold;")

    csv_path = Path("data/raw/ine/turismo_provincia_mes_clean.csv")
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    con.execute("DROP TABLE IF EXISTS raw.ine_turismo_clean;")
    con.execute(f"""
        CREATE TABLE raw.ine_turismo_clean AS
        SELECT * FROM read_csv_auto('{csv_path.as_posix()}');
    """)

    # Normalización: nos quedamos con CCAA, Periodo, Métrica y Total
    # OJO: Total viene con puntos como separador de miles (420.941) -> quitamos puntos y lo parseamos
    con.execute("DROP TABLE IF EXISTS gold.turismo_ccaa_mes;")
    con.execute("""
        CREATE TABLE gold.turismo_ccaa_mes AS
        SELECT
          -- CCAA: quitamos el prefijo numérico "01 Andalucía" -> "Andalucía"
          REGEXP_REPLACE("Comunidades y Ciudades Autónomas", '^\\d+\\s+', '') AS ccaa,

          -- Periodo: 2025M10 -> year_month 2025-10
          SUBSTR("Periodo", 1, 4) || '-' || LPAD(SUBSTR("Periodo", 6, 2), 2, '0') AS year_month,

          "Viajeros y pernoctaciones" AS metric,

          TRY_CAST(REPLACE("Total", '.', '') AS BIGINT) AS value
        FROM raw.ine_turismo_clean
        WHERE "Comunidades y Ciudades Autónomas" IS NOT NULL
          AND "Periodo" LIKE '%M%'
          AND "Residencia" = 'Total';
    """)

    print("OK: gold.turismo_ccaa_mes creado")
    print(con.execute("""
        SELECT COUNT(*) AS rows, MIN(year_month) AS min_ym, MAX(year_month) AS max_ym
        FROM gold.turismo_ccaa_mes;
    """).fetchdf())

    print("\nMuestra:")
    print(con.execute("""
        SELECT * FROM gold.turismo_ccaa_mes
        ORDER BY ccaa, year_month, metric
        LIMIT 10;
    """).fetchdf())

if __name__ == "__main__":
    main()
