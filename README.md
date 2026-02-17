# Turismo & Meteo (España) — Analytics Engineering + Power BI

Proyecto de portfolio orientado a rol **Analytics Engineer (con BI)**: construyo un pipeline reproducible (Python + DuckDB) con capas **RAW → SILVER → GOLD**, data quality checks y un dataset final consumido por **Power BI** para analizar la relación entre clima y turismo por CCAA.

---

## 🧠 Qué problema resuelve
Unificar dos fuentes públicas con formatos “reales” (APIs, CSV con encoding raro, separadores regionales) para responder a preguntas tipo:

- ¿Cómo se relacionan **temperatura media** y **precipitación** con **pernoctaciones**?
- ¿Qué CCAA lideran en **demanda turística** y cómo cambia el patrón con el clima?

**Output final:** una tabla a nivel **CCAA + mes** lista para BI:  
`data/gold/turismo_meteo_ccaa_mes.csv`

---

## 🧰 Stack
- **Python** (requests, pandas)
- **DuckDB** (modelo analítico local, rápido, portable)
- **Power BI Desktop**
- **Data modeling:** dims/facts + marts
- **Quality checks:** conteos, nulos, duplicados, integridad referencial

---

## 📦 Fuentes de datos
- **AEMET OpenData**: valores climatológicos diarios por estación (España).  
  Se agregan a provincia y luego a CCAA por mes (temperatura media y precipitación acumulada).
- **INE**: viajeros y pernoctaciones por CCAA y mes.  
  Incluye limpieza de CSV real (encoding cp1252 / separador `;` / decimales).

> Nota: este repo no incluye `.env` ni datos RAW pesados. El pipeline permite regenerarlos.

---

## 🧱 Arquitectura de datos (RAW → SILVER → GOLD)
**RAW**
- `raw.aemet_stations`
- `raw.aemet_daily`

**SILVER**
- `silver.meteo_daily` (tipado, fechas parseadas, limpieza nulos)

**GOLD**
- Dimensiones:
  - `gold.dim_fecha`
  - `gold.dim_estacion`
- Hecho:
  - `gold.fact_meteo_daily` (si aplica en tu build)
- Marts:
  - `gold.meteo_provincia_mes`
  - `gold.meteo_ccaa_mes`
  - `gold.turismo_ccaa_mes` (INE)
  - `gold.turismo_meteo_ccaa_mes` (JOIN final)

**Dataset final para BI**
- `data/gold/turismo_meteo_ccaa_mes.csv`

---

## ✅ Data Quality / Checks incluidos
Ejemplos de checks ejecutados:
- Conteos RAW vs SILVER vs GOLD
- Fechas nulas tras parseo
- Duplicados por clave (indicativo, fecha)
- Cobertura de estaciones por mes
- Nulos en métricas clave (tmed/prec)
- Integridad referencial en joins de GOLD

Scripts: `src/db/run_checks.py`, `src/db/gold_checks.py` (y otros según tu repo).

---

## ▶️ Cómo ejecutar (reproducible)
### 1) Entorno
```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
pip install -r requirements.txt
