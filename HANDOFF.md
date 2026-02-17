# HANDOFF

## Estado
- Pipeline Python + DuckDB terminado (AEMET + INE) y JOIN final a nivel CCAA+mes.
- Dataset final exportado a CSV: data/gold/turismo_meteo_ccaa_mes.csv (local).
- Power BI Desktop: Página 1 creada con KPIs + barras + scatter + slicer (ccaa), con Detalles=ccaa y tooltips (precipitación, ratio).

## DAX
- Total Viajeros = SUM(...)
- Total Pernoctaciones = SUM(...)
- Ratio Pernoct/Viajero = DIVIDE(SUM(pernoctaciones), SUM(viajeros))

## Problemas resueltos
- Importación CSV: locale (punto decimal) → Power Query “Usar configuración regional”.
- Tipos numéricos: viajeros/pernoctaciones a entero; temp/prec a decimal.
- Renombrar campos rompía visuals: se arregló re-asignando campos y quitando filtros rotos.

## Próximo
- Limpiar layout (Top 10 + slicer dropdown + títulos pro).
- Página 2 detalle por CCAA + navegación.
- Ampliar a 6–12 meses y rehacer marts/final.
