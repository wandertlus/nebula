# NEBULA — Weekly Roadmap + Signal Templates

## Identidades activas: Engineering · Be Fluent · Fitness

---

## ROADMAP SEMANAL

| Identidad   | Objetivo semanal | Mínimo días | Duración típica | Categoría |
|-------------|-----------------|-------------|-----------------|-----------|
| Engineering | 5–8 señales     | 5 días      | 45–120 min      | Work      |
| Be Fluent   | 5–7 señales     | 5 días      | 20–60 min       | Education |
| Fitness     | 3–4 señales     | 3 días      | 60–90 min       | Health    |

**Coherencia objetivo:** si mantienes este ritmo 2 semanas seguidas, el score sube de 0.37 a ~0.65+

---

## PLANTILLAS POR IDENTIDAD

Copia el comando exacto cuando termines una sesión.
Ajusta solo: el texto entre comillas y el número de minutos.

---

### ⚙️ ENGINEERING — Construir

```bash
# Feature / módulo nuevo
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Built [DESCRIPCIÓN del módulo o feature]", "category": "Work", "duration": 90}'
```

```bash
# Fix / debug
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Fixed [DESCRIPCIÓN del bug o problema]", "category": "Work", "duration": 45}'
```

```bash
# Refactor / arquitectura
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Refactored [DESCRIPCIÓN del componente] for better structure", "category": "Work", "duration": 60}'
```

```bash
# Proyecto Nebula específicamente
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Worked on Nebula [DESCRIPCIÓN del cambio]", "category": "Work", "duration": 60}'
```

---

### ⚙️ ENGINEERING — Estudiar

```bash
# Documentación técnica
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Read documentation on [TEMA]", "category": "Education", "duration": 30}'
```

```bash
# Paper / artículo técnico (con resultado medible)
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Read technical paper on [TEMA]", "category": "Education", "duration": 30, "effort_signals": {"result_type": "numeric", "result_value": 1, "result_unit": "papers", "result_text": "[QUÉ APRENDISTE]"}}'
```

```bash
# Tutorial / curso / video técnico
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Watched tutorial on [TEMA]", "category": "Education", "duration": 45}'
```

---

### 🗣️ BE FLUENT — Escuchar

```bash
# Podcast en inglés
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Listened to English podcast: [NOMBRE o TEMA]", "category": "Education", "duration": 30}'
```

```bash
# Video / contenido en inglés
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Watched English content on [TEMA]", "category": "Education", "duration": 45}'
```

---

### 🗣️ BE FLUENT — Escribir

```bash
# Documentación técnica en inglés
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Wrote technical documentation in English for [PROYECTO o TEMA]", "category": "Education", "duration": 30}'
```

```bash
# Notas / journaling en inglés
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Wrote English notes and reflections on [TEMA]", "category": "Education", "duration": 20}'
```

```bash
# Mensaje / email profesional en inglés
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Wrote professional email in English to [DESTINATARIO o CONTEXTO]", "category": "Education", "duration": 20}'
```

---

### 🗣️ BE FLUENT — Hablar

```bash
# Conversación / práctica oral
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Practiced English conversation on [TEMA o CON QUIÉN]", "category": "Education", "duration": 30}'
```

```bash
# Shadowing / pronunciación
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "English shadowing and pronunciation practice", "category": "Education", "duration": 20}'
```

---

### 💪 FITNESS — Fuerza

```bash
# Sesión completa de gym
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Strength training session: [GRUPOS MUSCULARES o TIPO]", "category": "Health", "duration": 75}'
```

```bash
# Sesión con resultado medible (peso levantado, sets completados)
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Strength training: [EJERCICIO PRINCIPAL]", "category": "Health", "duration": 75, "effort_signals": {"result_type": "numeric", "result_value": [PESO_KG], "result_unit": "kg", "result_text": "[DESCRIPCIÓN del PR o logro]"}}'
```

```bash
# Sesión corta / movilidad
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Mobility and warm-up session", "category": "Health", "duration": 30}'
```

---

## GUÍA DE USO RÁPIDO

### Regla de oro

Registra la señal **justo cuando terminas** la sesión.
No acumules para el final del día — pierdes precisión en la duración y el texto.

### Qué escribir en action_text

- Sé específico: `"Built authentication module with JWT"` > `"Worked on code"`
- Menciona el tema real: `"Read docs on FastAPI dependency injection"` > `"Read documentation"`
- Para fitness nombra el enfoque: `"Strength training: chest and triceps"` > `"Gym session"`
- La especificidad mejora la alineación semántica de MiniLM directamente

### Duración

- No estimes de más. Si estuviste 45 min pero 15 fueron distracciones → pon 30.
- El sistema penaliza automáticamente las distracciones si las registras.

### Cuándo usar effort_signals

Solo cuando tienes un resultado concreto y medible:

- Terminaste un paper → `result_value: 1, result_unit: "papers"`
- Levantaste un PR nuevo → `result_value: X, result_unit: "kg"`
- Completaste un módulo → `result_value: 1, result_unit: "modules"`

---

## SEÑALES DE DISTRACCIÓN (registrar también)

El sistema es más preciso si registras las distracciones. No se juzgan, se describen.

```bash
# Distracción
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Scrolled social media and news", "category": "Distraction", "duration": 30}'
```

```bash
# Descanso legítimo
curl -X POST http://localhost:8000/api/signal \
  -H "Content-Type: application/json" \
  -d '{"action_text": "Rest and recovery", "category": "Rest", "duration": 45}'
```

---

## QUÉ ESPERAR ESTA SEMANA

| Día       | Engineering       | Be Fluent        | Fitness         |
|-----------|-------------------|------------------|-----------------|
| Lunes     | Build (90 min)    | Escuchar (30 min)| Fuerza (75 min) |
| Martes    | Estudiar (45 min) | Escribir (20 min)| —               |
| Miércoles | Build (90 min)    | Hablar (30 min)  | Fuerza (75 min) |
| Jueves    | Build (60 min)    | Escuchar (30 min)| —               |
| Viernes   | Estudiar (45 min) | Escribir (20 min)| Fuerza (75 min) |
| Sábado    | Build (60 min)    | Mix (30 min)     | —               |
| Domingo   | —                 | —                | —               |

**Total estimado:** ~13 señales/semana · ~11 horas de actividad constructiva

---

## ROADMAP FUTURO — Cómo escalar el input

### Fase 2 — Barra de aplicación (próxima)

Un input rápido desde la barra del sistema operativo (macOS menu bar).
Escribe texto + selecciona categoría → señal enviada en 5 segundos.

### Fase 3 — Telegram bot

Envías un mensaje a un bot: `"Gym 75 min"` o `"Built auth module 90 min Work"`.
El bot parsea y llama a POST /api/signal automáticamente.
Ideal para registrar desde el celular al salir del gym.

### Fase 4 — Parsing inteligente

Input completamente libre: `"Estuve 1 hora en el gym haciendo pecho"`.
Un modelo extrae category, duration y action_text automáticamente.
