# Macro Manager v27 — F1–F12
### LU4 (Lineage Universe 4) · IKAR Core Pipe

Automatizador de habilidades para LU4 que envía comandos directamente al pipe de IKAR — sin simulación de teclado, sin pulsaciones de OS, sin ser detectado por anti-cheat a nivel de kernel.

---

## Requisitos

| Requisito | Detalle |
|-----------|---------|
| **Python 3.8+** | Solo stdlib — sin pip install |
| **IKAR con core.exe activo** | Debe estar inyectado en el juego |
| **LU4 en ejecución** | El pipe solo existe cuando IKAR está conectado |
| **Windows 10/11** | Usa `kernel32.dll` para named pipes |

---

## Inicio Rápido

```
1. Abrir LU4
2. Lanzar IKAR → esperar que core.exe se conecte al juego
3. Ejecutar:  python MacroFKeys.py
4. Presionar ⚡ Conectar en la barra superior
5. Configurar Skill ID + Delay en cada fila F1–F12
6. Presionar ▶ START
```

---

## Interfaz

```
┌─ Pipe IKAR: \\.\pipe\scripthost-debug  │ botId: 1 │ ⚡ Conectar │ ✓ Conectado botId=4 ─┐
│ [debug: F1] skill=1042  ✓                                                                │
├──────────┬───────┬──────────┬─────────┬──────────┬───────┬───────┬────────┬─────────────┤
│ START/STOP│ Tecla │ Skill ID │ Repetir │ Infinito │ Veces │ Delay │ Unidad │   Estado    │
├──────────┼───────┼──────────┼─────────┼──────────┼───────┼───────┼────────┼─────────────┤
│ ■ STOP   │  F1   │   1042   │   ☑    │    ☑    │   —   │  800  │   ms   │  ● ACTIVO  │
│ ▶ START  │  F2   │   1055   │   ☑    │    ☐    │   5   │   2   │   s    │     —       │
│ ▶ START  │  F3   │    0     │   ☐    │    ☐    │   1   │ 1000  │   ms   │     —       │
└──────────┴───────┴──────────┴─────────┴──────────┴───────┴───────┴────────┴─────────────┘
                                          ⛔ Detener Todo
```

---

## Columnas de Configuración

| Campo | Descripción |
|-------|-------------|
| **START/STOP** | Activa o detiene el macro para esa tecla |
| **Skill ID** | ID numérico de la habilidad en LU4 |
| **Repetir** | ☑ = repite con delay · ☐ = dispara una sola vez |
| **Infinito** | ☑ = repite indefinidamente (ignora Veces) |
| **Veces** | Cantidad de repeticiones si Infinito está desactivado |
| **Delay** | Tiempo entre cada uso de skill |
| **Unidad** | `ms` = milisegundos · `s` = segundos · `min` = minutos |

---

## Configurar el Delay

El delay se interpreta según la unidad del dropdown:

- `800 ms` → usa skill cada 0.8 segundos  
- `2 s` → usa skill cada 2 segundos  
- `0.5 min` → usa skill cada 30 segundos  

> **Mínimo efectivo:** 50 ms. Valores menores se truncan automáticamente.

---

## Barra de Conexión

| Campo | Descripción |
|-------|-------------|
| **Pipe IKAR** | Por defecto `\\.\pipe\scripthost-debug`. Solo cambiar si IKAR usa `--pipe-host` |
| **botId** | Se actualiza automáticamente al recibir el primer `world_state` del juego |
| **⚡ Conectar** | Abre la conexión. Cambia a ⛔ Desconectar cuando está activo |

### Estados de Conexión

| Estado | Significado |
|--------|-------------|
| `— No conectado` | Estado inicial |
| `↔ Esperando world_state…` | Pipe abierto, esperando evento del juego |
| `✓ Conectado  botId=X` | Listo para enviar habilidades |
| `✗ No se pudo conectar (err=2)` | Pipe no existe — IKAR/juego no están activos |
| `✗ Desconectado` | IKAR o juego se cerraron — reconectá |

---

## Cómo Funciona

```
Python (MacroFKeys.py)
        │
        │  Named Pipe  \\.\pipe\scripthost-debug
        ▼
IKAR core.exe  (DLL inyectada en LU4)
        │
        │  Llamada interna al proceso del juego
        ▼
LU4 (Lineage Universe 4)  →  Servidor
```

El macro **no simula teclado ni mouse**. Envía un JSON por named pipe al core de IKAR, que a su vez llama directamente la función interna del juego para usar la habilidad. El anti-cheat no lo detecta porque no hay eventos de OS.

### Formato del mensaje enviado

```json
{
  "v": 1,
  "type": "request",
  "botId": "4",
  "requestId": "py-1",
  "payload": {
    "@type": "use_fight_skill",
    "skillId": 1042,
    "ctrl": false,
    "shift": false
  }
}
```

---

## Solución de Problemas

**No se puede conectar (err=2)**  
→ LU4 no está abierto o IKAR core.exe no está inyectado en el proceso del juego.

**Skill se envía (✓) pero no pasa nada en el juego**  
→ El Skill ID es incorrecto. Revisá el ID numérico real de la habilidad en los logs de IKAR.

**El macro dispara muy rápido / muy lento**  
→ Verificá la unidad: `1000 ms` = 1 segundo, `1000 s` = 16 minutos.

**La ventana queda detrás de LU4**  
→ La ventana está en modo `always-on-top`. Minimizá y restaurá si queda tapada.

---

## Archivos

```
lu4-macro/
└── MacroFKeys.py    # Script principal — todo en un archivo, sin dependencias externas
```

---

*Macro Manager v27 · AYI GROUP*
