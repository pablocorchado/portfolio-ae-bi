# portfolio-ae-bi

Estructura base para un pipeline tipo medallion (raw â†’ bronze â†’ silver â†’ gold) con ingesta de AEMET y carga a DuckDB.

## Estructura
- data/raw/aemet/: datos crudos descargados
- data/bronze/: datos con mÃ­nima limpieza
- data/silver/: datos estandarizados/enriquecidos
- data/gold/: marts/tablas finales para BI
- src/aemet/: scripts de ingesta (estaciones, diarios, etc.)
- src/db/: carga/transformaciones en DuckDB
- sql/: DDL + staging + marts

## Quickstart
1) Crea un venv e instala dependencias:
   - python -m venv .venv
   - .\.venv\Scripts\Activate.ps1
   - pip install -r requirements.txt
