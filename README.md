# Macro Manager v5 — F1–F12

Automatizador de teclas F1–F12 para Windows. Captura cualquier ventana de juego y envía las teclas directamente a ese proceso — sin depender de software externo.

Soporta múltiples instancias simultáneas (una por cuenta).

---

## Requisitos

| Requisito | Detalle |
|-----------|---------|
| **Python 3.8+** | Solo stdlib — sin pip install |
| **Windows 10/11** | Usa `user32.dll` para envío de teclas |
| **El juego abierto** | Necesita capturar la ventana del juego |

---

## Inicio Rápido

```
1. Ejecutar:  python MacroFKeys.py
2. Hacer clic en 🎯 Capturar ventana
3. Tenés 3 segundos para hacer Alt+Tab al juego
4. Configurar delay y opciones en cada fila F1–F12
5. Presionar ▶ START
```

---

## Interfaz

```
┌──────────────────────────────────────────────────────────────┐
│ 🎯 Capturar ventana  │  ✓  Lineage Universe 4               │
├──────────────────────────────────────────────────────────────┤
│         🔕 Modo Fondo  (sin foco)                            │
├──────────┬───────┬─────────┬──────────┬───────┬─────────┬───┤
│ START/STOP│ Tecla │ Repetir │ Infinito │ Veces │ Delay ms│Est│
├──────────┼───────┼─────────┼──────────┼───────┼─────────┼───┤
│ ■ STOP   │  F1   │   ☑    │    ☑    │   —   │   800   │ ● │
│ ▶ START  │  F2   │   ☑    │    ☐    │   5   │  2000   │ — │
│ ▶ START  │  F3   │   ☐    │    ☐    │   1   │   500   │ — │
└──────────┴───────┴─────────┴──────────┴───────┴─────────┴───┘
        Para varias cuentas: abrí otra copia de este programa
                    ⛔ Detener Todo
```

---

## Columnas de Configuración

| Campo | Descripción |
|-------|-------------|
| **START/STOP** | Activa o detiene el macro para esa tecla |
| **Repetir** | ☑ = repite con delay · ☐ = dispara una sola vez |
| **Infinito** | ☑ = repite indefinidamente (ignora Veces) |
| **Veces** | Cantidad de repeticiones si Infinito está desactivado |
| **Delay ms** | Tiempo entre cada pulsación, en milisegundos |

---

## Modos de Envío

El botón central alterna entre dos modos:

### 🔕 Modo Fondo (por defecto)
Envía la tecla con `PostMessage` directamente a la ventana del juego **sin mover el foco**. El juego sigue en segundo plano, podés seguir usando el teclado normalmente.

- Funciona en la mayoría de juegos con procesamiento de mensajes estándar
- No interrumpe lo que estás haciendo

### ⚡ Modo Flash
Lleva el juego al frente ~30ms, manda la tecla con `SendInput` (input real de hardware) y devuelve el foco a la ventana anterior.

- Necesario para juegos UE5/UE4 que usan **Raw Input** o **DirectInput**
- La ventana del juego parpadea brevemente (~30ms)
- Usar este modo si Modo Fondo no funciona

---

## Múltiples Cuentas

Cada instancia del programa captura y controla **una ventana independiente**. Para usar el macro con varias cuentas al mismo tiempo:

```
python MacroFKeys.py   ← Instancia #1 → captura Cuenta A
python MacroFKeys.py   ← Instancia #2 → captura Cuenta B
python MacroFKeys.py   ← Instancia #3 → captura Cuenta C
```

El título de cada ventana muestra el número de instancia: `Macro Manager v5 — Instancia #2`

---

## Cómo Funciona

```
MacroFKeys.py
     │
     │  PostMessage / SendInput  (Win32 API)
     ▼
Ventana del juego (por HWND capturado)
     │
     ▼
Proceso del juego recibe WM_KEYDOWN / WM_KEYUP
```

**No simula teclado a nivel de OS** (no usa keybd_event ni eventos globales). Envía mensajes directamente a la handle de la ventana destino.

---

## Solución de Problemas

**"Primero capturá la ventana del juego"**  
→ Presioná 🎯 Capturar ventana y hacé Alt+Tab al juego en los 3 segundos.

**La tecla no hace nada en el juego (Modo Fondo)**  
→ El juego usa Raw Input. Cambiá a ⚡ Modo Flash.

**El juego parpadea molestamente (Modo Flash)**  
→ Normal. El foco vuelve en ~30ms. Si el juego lo detecta como cheat, probá Modo Fondo.

**Una instancia se abre como #3 aunque solo hay una**  
→ Los puertos 47200–47201 están ocupados por otro proceso. No afecta el funcionamiento.

---

## Archivos

```
lu4-macro/
└── MacroFKeys.py    # Todo en un archivo — sin dependencias externas
```

---

*Macro Manager v5 · AYI GROUP*
