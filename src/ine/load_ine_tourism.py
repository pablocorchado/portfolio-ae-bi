from pathlib import Path
import duckdb

def try_load(con, csv_path: Path, encoding: str):
    con.execute("DROP TABLE IF EXISTS raw.ine_turismo;")
    con.execute(f"""
        CREATE TABLE raw.ine_turismo AS
        SELECT *
        FROM read_csv(
            '{csv_path.as_posix()}',
            auto_detect=true,
            encoding='{encoding}',
            header=true,
            delim=','
        );
    """)
    return True

def main():
    con = duckdb.connect("data/weather.duckdb")
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    con.execute("CREATE SCHEMA IF NOT EXISTS silver;")
    con.execute("CREATE SCHEMA IF NOT EXISTS gold;")

    csv_path = Path("data/raw/ine/turismo_provincia_mes.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"No encuentro {csv_path}. Guárdalo ahí con ese nombre.")

    # Probamos encodings típicos de INE/export Excel
    encodings_to_try = ["UTF-8", "UTF-16", "UTF-16LE", "ISO-8859-1", "Windows-1252"]

    loaded = False
    last_error = None

    for enc in encodings_to_try:
        try:
            print(f"Probando encoding: {enc}")
            try_load(con, csv_path, enc)
            loaded = True
            print(f"OK: cargado con encoding {enc}")
            break
        except Exception as e:
            last_error = e
            print(f"  Falló con {enc}: {str(e).splitlines()[0]}")

    if not loaded:
        raise RuntimeError(f"No pude cargar el CSV con encodings comunes. Último error: {last_error}")

    # Info de columnas detectadas
    cols = con.execute("PRAGMA table_info('raw.ine_turismo');").fetchdf()
    print("\nColumnas detectadas:")
    print(cols[["name", "type"]])

    # Muestra 5 filas para ver forma real
    print("\nMuestra (5 filas):")
    print(con.execute("SELECT * FROM raw.ine_turismo LIMIT 5;").fetchdf())

    print("\nSiguiente paso: dime cuál columna es Provincia, cuál es Mes/Fecha y cuál es la métrica (viajeros/pernoctaciones).")

if __name__ == "__main__":
    main()
