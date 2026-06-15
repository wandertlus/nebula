# NEBULA — Reset Completo + Setup Post-Reset

---

## PASO 1 — Detener el backend

```bash
# Matar el proceso en puerto 8000
lsof -ti :8000 | xargs kill -9
```

---

## PASO 2 — Borrar todos los archivos de estado

```bash
cd /Users/dokodo/Desktop/nebula
```

```bash
# Borrar historial de eventos
> events.jsonl
```

```bash
# Resetear identity state
cat > identity_state.json << 'EOF'
{
  "identity_vector": [],
  "dimension": 384,
  "efficiency_by_category": {},
  "updated_at": ""
}
EOF
```

```bash
# Resetear thermodynamic state
cat > thermodynamic_state.json << 'EOF'
{
  "_last_decay": ""
}
EOF
```

```bash
# Resetear ventures
cat > ventures_state.json << 'EOF'
{
  "schema_version": 1,
  "updated_at": "",
  "ventures": {}
}
EOF
```

```bash
# Resetear dynamic fields (limpio, sin campos custom)
cat > dynamic_fields.json << 'EOF'
{}
EOF
```

---

## PASO 3 — Verificar que quedó limpio

```bash
wc -l events.jsonl
# Debe decir: 0 events.jsonl

cat thermodynamic_state.json
# Debe mostrar solo _last_decay vacío

cat ventures_state.json
# Debe mostrar ventures: {}
```

---

## PASO 4 — Arrancar el backend limpio

```bash
cd /Users/dokodo/Desktop/nebula
python api.py
```

El backend arranca con estado en cero.
Los campos base (engineering, fitness, be_fluent) están definidos en config.py — no se borran con el reset.

---

## PASO 5 — Añadir campos de identidad custom

Los campos base **no necesitan agregarse** — ya existen:

- `engineering`
- `fitness`
- `be_fluent`

Para agregar campos **adicionales** usa este comando desde la terminal:

```bash
# Agregar un campo nuevo
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "/add-field find_job Freelance work, portfolio building, job applications and client acquisition", "category": "Work", "duration": 0}'
```

**Formato del comando:**

```
/add-field <nombre_campo> <descripción semántica del campo>
```

La descripción es importante — MiniLM la usa para calcular alineación semántica.
Mientras más descriptiva, mejor clasifica las señales.

**Ejemplos:**

```bash
# Campo para emprendimiento
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "/add-field entrepreneurship Business operations, supplier management, customer acquisition, revenue generation and business growth", "category": "Work", "duration": 0}'

# Campo para finanzas personales
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "/add-field finance Personal finance management, investment tracking, budgeting and financial planning", "category": "Work", "duration": 0}'
```

Para **eliminar** un campo custom:

```bash
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "/delete-field nombre_campo", "category": "Work", "duration": 0}'
```

---

## PASO 6 — Crear un nuevo venture

Un venture es un sistema económico paralelo (negocio, proyecto, startup).
Se crea automáticamente la primera vez que envías una señal con `venture_id`.

```bash
# Primera señal crea el venture automáticamente
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{
    "action_text": "Met with coffee supplier to discuss pricing",
    "category": "Work",
    "duration": 60,
    "venture_id": "cafe",
    "money_delta": -50
  }'
```

El venture `cafe` queda creado con:

- `mass: 0`
- `momentum: 0`
- `resource_flow: time_in: 60, money_out: 50`

**Parámetros de venture disponibles:**

| Campo          | Qué significa                           | Ejemplo        |
|----------------|-----------------------------------------|----------------|
| `venture_id`   | Nombre único del venture (sin espacios) | `"cafe"`       |
| `money_delta`  | Positivo = ingreso, Negativo = gasto    | `-200` o `500` |
| `energy_delta` | Energía invertida en el venture         | `0.8`          |

**Ejemplos de señales con venture:**

```bash
# Gasto en el café
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Paid monthly rent for cafe location", "category": "Work", "duration": 10, "venture_id": "cafe", "money_delta": -1200}'

# Ingreso en el café
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Cafe daily revenue collected", "category": "Work", "duration": 30, "venture_id": "cafe", "money_delta": 350}'

# Tiempo operativo sin flujo de dinero
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Managed cafe operations and staff", "category": "Work", "duration": 120, "venture_id": "cafe"}'
```

---

## RESUMEN POST-RESET

Después de ejecutar este orden, el sistema queda:

| Archivo                  | Estado                                          |
|--------------------------|-------------------------------------------------|
| events.jsonl             | Vacío — 0 líneas                                |
| identity_state.json      | Vector limpio dim 384                           |
| thermodynamic_state.json | Sin clusters, sin masa                          |
| ventures_state.json      | Sin ventures                                    |
| dynamic_fields.json      | Sin campos custom                               |
| config.py                | Intacto — engineering/fitness/be_fluent activos |

**Primera señal real después del reset:**

```bash
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Started Nebula from zero — first real signal", "category": "Work", "duration": 5}'
```
