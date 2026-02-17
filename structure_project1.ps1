# init_project.ps1
$ErrorActionPreference = "Stop"

$ProjectName = "portfolio-ae-bi"
$Root = Join-Path (Get-Location) $ProjectName

# Carpetas a crear
$Dirs = @(
  "data\raw\aemet",
  "data\bronze",
  "data\silver",
  "data\gold",
  "src\aemet",
  "src\db",
  "sql"
)

# Archivos a crear
$Files = @(
  "README.md",
  "requirements.txt",
  ".gitignore",
  "src\aemet\fetch_stations.py",
  "src\aemet\fetch_daily.py",
  "src\db\load_duckdb.py",
  "sql\00_schema.sql",
  "sql\10_staging.sql",
  "sql\20_marts.sql"
)

# Crea raíz
New-Item -ItemType Directory -Path $Root -Force | Out-Null

# Crea carpetas
foreach ($d in $Dirs) {
  New-Item -ItemType Directory -Path (Join-Path $Root $d) -Force | Out-Null
}

# Crea archivos vacíos si no existen
foreach ($f in $Files) {
  $p = Join-Path $Root $f
  if (-not (Test-Path $p)) {
    New-Item -ItemType File -Path $p -Force | Out-Null
  }
}

# Escribe README.md
@"
# portfolio-ae-bi

Estructura base para un pipeline tipo medallion (raw → bronze → silver → gold) con ingesta de AEMET y carga a DuckDB.

## Estructura
- data/raw/aemet/: datos crudos descargados
- data/bronze/: datos con mínima limpieza
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
"@ | Set-Content -Path (Join-Path $Root "README.md") -Encoding UTF8

# Escribe requirements.txt
@"
requests
pandas
duckdb
python-dotenv
"@ | Set-Content -Path (Join-Path $Root "requirements.txt") -Encoding UTF8

# Escribe .gitignore
@"
# Python
__pycache__/
*.py[cod]
*.pyd
*.pyo
*.egg-info/
dist/
build/

# Envs
.venv/
venv/
env/

# OS / IDE
.DS_Store
.idea/
.vscode/

# Data local
data/raw/
data/bronze/
data/silver/
data/gold/

# DuckDB / logs
*.duckdb
*.log

# Secrets
.env
"@ | Set-Content -Path (Join-Path $Root ".gitignore") -Encoding UTF8

Write-Host "✅ Estructura creada en: $Root"
