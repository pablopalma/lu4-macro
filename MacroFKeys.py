#!/usr/bin/env python3
"""
Macro Manager — F1 a F12  v5
  · Modo Fondo (PostMessage) — sin mover el foco
  · Modo Flash (SetForegroundWindow + SendInput) — foco ~30ms para juegos Raw Input
  · Múltiples instancias: corré el .py N veces, cada una captura su ventana
"""
import sys, os, time, ctypes, ctypes.wintypes as wt, threading, tkinter as tk
from tkinter import font as tkfont

user32   = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# ── Número de instancia (por puerto de socket local) ─────────────────
import socket as _sock
INST_NUM = 1
for _p in range(47200, 47220):
    try:
        _srv = _sock.socket(); _srv.bind(("127.0.0.1", _p)); _srv.listen(1)
        INST_NUM = _p - 47199
        break
    except OSError:
        INST_NUM += 1

# ── Estructuras SendInput ────────────────────────────────────────────
KEYEVENTF_KEYUP    = 0x0002
KEYEVENTF_SCANCODE = 0x0008
INPUT_KEYBOARD     = 1

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wt.WORD), ("wScan", wt.WORD),
                ("dwFlags", wt.DWORD), ("time", wt.DWORD),
                ("dwExtraInfo", ctypes.c_size_t)]

class _U(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", wt.DWORD), ("_input", _U)]

_SZ = ctypes.sizeof(INPUT)

VK = {f"F{i}": 0x70 + (i-1) for i in range(1, 13)}
SC = {"F1":0x3B,"F2":0x3C,"F3":0x3D,"F4":0x3E,"F5":0x3F,"F6":0x40,
      "F7":0x41,"F8":0x42,"F9":0x43,"F10":0x44,"F11":0x57,"F12":0x58}
WM_KEYDOWN = 0x0100
WM_KEYUP   = 0x0101

target_hwnd = 0
flash_mode  = False   # True = focus-flash + SendInput

def send_key_post(key):
    """PostMessage directo — sin mover el foco."""
    vk = VK[key]; sc = SC[key]
    user32.PostMessageW(target_hwnd, WM_KEYDOWN, vk, 1|(sc<<16))
    time.sleep(0.05)
    user32.PostMessageW(target_hwnd, WM_KEYUP,   vk, 1|(sc<<16)|(1<<30)|(1<<31))

def send_key_flash(key):
    """
    Focus-flash: lleva el juego al frente ~30ms, manda la tecla como input real
    (Raw Input / DirectInput), y devuelve el foco.  Funciona con juegos UE5.
    """
    vk = VK[key]; sc = SC[key]
    prev = user32.GetForegroundWindow()

    # Llevar juego al frente
    user32.ShowWindow(target_hwnd, 5)  # SW_SHOW
    user32.SetForegroundWindow(target_hwnd)
    time.sleep(0.025)

    # Enviar via SendInput (input real, no INJECTED desde el punto de vista del juego)
    buf = (INPUT * 2)()
    buf[0].type = INPUT_KEYBOARD
    buf[0]._input.ki.wVk   = vk
    buf[0]._input.ki.wScan = sc
    buf[0]._input.ki.dwFlags = KEYEVENTF_SCANCODE
    buf[1].type = INPUT_KEYBOARD
    buf[1]._input.ki.wVk   = vk
    buf[1]._input.ki.wScan = sc
    buf[1]._input.ki.dwFlags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP
    user32.SendInput(2, buf, _SZ)
    time.sleep(0.025)

    # Devolver foco
    if prev and prev != target_hwnd:
        user32.SetForegroundWindow(prev)

def send_key(key):
    if not target_hwnd:
        return
    if flash_mode:
        send_key_flash(key)
    else:
        send_key_post(key)

def capture_window():
    global target_hwnd
    btn_cap.config(state="disabled", text="Esperá 3s…")
    def _do():
        global target_hwnd
        for i in range(3, 0, -1):
            root.after(0, lambda n=i: lbl_win.config(
                text=f"  Alt+Tab al juego ahora… ({n}s)", fg="#FF8800"))
            time.sleep(1)
        hwnd = user32.GetForegroundWindow()
        buf  = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, buf, 256)
        title = buf.value or "(sin título)"
        target_hwnd = hwnd
        root.after(0, lambda: (
            lbl_win.config(text=f"  ✓  {title[:38]}", fg="#00BB00"),
            btn_cap.config(state="normal", text="🎯  Capturar ventana")
        ))
    threading.Thread(target=_do, daemon=True).start()

def toggle_flash():
    global flash_mode
    flash_mode = not flash_mode
    if flash_mode:
        btn_mode.config(text="⚡ Modo Flash  (foco ~30ms)", bg="#886600")
    else:
        btn_mode.config(text="🔕 Modo Fondo  (sin foco)", bg="#226622")

# ── Estado ───────────────────────────────────────────────────────────
FKEYS     = [f"F{i}" for i in range(1, 13)]
active    = {k: False for k in FKEYS}
stop_evts = {k: threading.Event() for k in FKEYS}
cfg       = {}

def toggle(key):
    if active[key]: _stop(key)
    else:           _start(key)

def _start(key):
    if not target_hwnd:
        lbl_win.config(text="  ⚠  Primero capturá la ventana del juego", fg="#FF4444")
        return
    c     = cfg[key]
    rep   = bool(c["rep"].get())
    inf   = bool(c["inf"].get())
    n     = max(1, _iv(c["times"], 1))
    delay = max(0.05, _iv(c["delay"], 500) / 1000.0)
    active[key] = True
    stop_evts[key].clear()
    _ui(key, True)
    def _run():
        count = 0; ev = stop_evts[key]
        while active[key]:
            send_key(key)
            count += 1
            if not rep: break
            if not inf and count >= n: break
            if ev.wait(timeout=delay): break
        _stop(key)
    threading.Thread(target=_run, daemon=True).start()

def _stop(key):
    active[key] = False
    stop_evts[key].set()
    root.after(0, lambda k=key: _ui(k, False))

def _ui(key, on):
    c = cfg[key]
    if on:
        c["btn"].config(text="■  STOP", bg="#BB2020", activebackground="#EE3333")
        c["lbl"].config(text="● ACTIVO", fg="#00BB00")
    else:
        c["btn"].config(text="▶  START", bg="#1a6bba", activebackground="#2288ee")
        c["lbl"].config(text="  —  ", fg="#888888")

def _iv(var, fb):
    try: return int(var.get())
    except: return fb

def stop_all():
    for k in FKEYS: _stop(k)

# ── GUI ──────────────────────────────────────────────────────────────
root = tk.Tk()
root.title(f"Macro Manager  v5  — Instancia #{INST_NUM}")
root.resizable(False, False)
root.attributes("-topmost", True)

FH = tkfont.Font(family="Segoe UI", size=8, weight="bold")
FN = tkfont.Font(family="Segoe UI", size=9)
FS = tkfont.Font(family="Segoe UI", size=8)
FB = tkfont.Font(family="Segoe UI", size=8, weight="bold")

# Barra superior
bar = tk.Frame(root, bd=1, relief="sunken", bg="#f0f0f0")
bar.pack(fill="x", padx=5, pady=(5,0))
btn_cap = tk.Button(bar, text="🎯  Capturar ventana", font=FB,
                    bg="#1a6bba", fg="white", activebackground="#2288ee",
                    relief="flat", command=capture_window)
btn_cap.pack(side="left", padx=4, pady=2)
lbl_win = tk.Label(bar, text="  (capturá la ventana del juego)",
                   fg="#888888", font=FS, bg="#f0f0f0", anchor="w")
lbl_win.pack(side="left", fill="x", expand=True)

# Botón modo
btn_mode = tk.Button(root, text="🔕 Modo Fondo  (sin foco)", font=FB,
                     bg="#226622", fg="white", activebackground="#338833",
                     relief="flat", command=toggle_flash)
btn_mode.pack(fill="x", padx=5, pady=(3,0))

# Encabezados
hdr = tk.Frame(root)
hdr.pack(fill="x", padx=5, pady=(4,0))
for txt, w in [("START/STOP",12),("Tecla",6),("Repetir",8),
               ("Infinito",8),("Veces",6),("Delay ms",9),("Estado",9)]:
    tk.Label(hdr, text=txt, font=FH, width=w, anchor="center").pack(side="left")

# Filas
for key in FKEYS:
    row = tk.Frame(root)
    row.pack(fill="x", padx=5, pady=1)
    btn = tk.Button(row, text="▶  START", font=FB, width=12,
                    bg="#1a6bba", fg="white", activebackground="#2288ee",
                    relief="flat", command=lambda k=key: toggle(k))
    btn.pack(side="left")
    tk.Label(row, text=key, font=FN, width=6, anchor="center").pack(side="left")
    vr = tk.IntVar(); vi = tk.IntVar()
    vt = tk.StringVar(value="1"); vd = tk.StringVar(value="500")
    tk.Checkbutton(row, variable=vr, width=8).pack(side="left")
    tk.Checkbutton(row, variable=vi, width=8).pack(side="left")
    tk.Entry(row, textvariable=vt, width=6, justify="center", font=FN).pack(side="left")
    tk.Entry(row, textvariable=vd, width=9, justify="center", font=FN).pack(side="left")
    lbl = tk.Label(row, text="  —  ", fg="#888888", font=FN, width=9)
    lbl.pack(side="left")
    cfg[key] = {"btn":btn,"rep":vr,"inf":vi,"times":vt,"delay":vd,"lbl":lbl}

foot = tk.Frame(root)
foot.pack(fill="x", padx=5, pady=(4,2))
tk.Label(foot, text="Para varias cuentas: abrí otra copia de este programa",
         fg="#808080", font=FS).pack()
tk.Button(foot, text="⛔  Detener Todo", font=FS, command=stop_all,
          width=20).pack(pady=(2,4))

def _close():
    stop_all(); root.destroy(); sys.exit(0)

root.protocol("WM_DELETE_WINDOW", _close)
root.mainloop()
