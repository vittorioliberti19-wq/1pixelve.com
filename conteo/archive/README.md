# Archivo permanente — Conteo Vehicular 1PIXEL

Respaldo **inmutable y versionado** del conteo de cada galería. Vive en Git → existe mientras exista el repo (y cualquier clon). Pensado para consultar la data del 2026, 2027, … dentro de 10 años sin depender de Cloudflare ni Camlytics.

## Capas de respaldo

1. **Camlytics Cloud** — fuente original (eventos crudos). Tiene límite de storage: borra eventos viejos. NO confiar para histórico.
2. **Cloudflare KV** (`frozen:<galería>:<día>`) — snapshot diario permanente que arma el Worker cada madrugada (cron). Rápido, sirve el dashboard. Vive mientras viva la cuenta Cloudflare.
3. **Este archivo Git** (`*.json`) — copia dueña, offline-clonable, versionada. **La capa de 10 años.**

El Worker congela cada día cerrado en KV; este archivo copia KV a Git. Aunque Camlytics borre los eventos y aunque se pierda la cuenta Cloudflare, la data sobrevive aquí.

## Formato

Un archivo por galería (`3h.json`, `cecilio.json`, …):

```jsonc
{
  "gallery": "cecilio",
  "label": "Calle 67 Cecilio Acosta",
  "exported_at": "2026-06-05T...",
  "day_count": 14,
  "first_day": "2026-05-21",
  "last_day": "2026-06-03",
  "days": {
    "2026-06-03": {
      "raw": 30411,        // total RegionJoin = conteo real de vehículos/peatones
      "unique": 30407,     // dedup con ventana 5s (≈ raw; el viejo dedup por object_id subcontaba)
      "byType": { "Car": 13000, "Truck": 9000, "Human": 2000, ... },
      "unknown": {},
      "hourly": [/* 24 valores, hora local Caracas */],
      "lifetime": 622995,
      "estimated": false   // true = día estimado de vecinos (cámara caída/degradada)
    }
  }
}
```

`raw` es el conteo bueno. `estimated:true` marca días rellenados (no medidos realmente).

## Refrescar

```bash
./refresh-archive.sh          # actualiza los JSON
./refresh-archive.sh --push   # + commit + push
```

Correr semanal (o cuando quieras). Idempotente: re-exporta todo el histórico de KV.

## Restaurar a KV (si se borrara)

Cada día del JSON se puede reescribir a KV con `wrangler kv bulk put` usando la clave `frozen:<galería>:<día>` y el objeto del día como valor. La data nunca depende de un solo lugar.
