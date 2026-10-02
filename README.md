# idiot-nightmare

> **A Windows prank payload — jumpscares, window rain, screen rotation, input block, audio scream.**
> Built for controlled pranks on your own machine or a consenting friend's VM.

![status](https://img.shields.io/badge/status-prank%20only-red)
![platform](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)
![python](https://img.shields.io/badge/python-3.10%2B-yellow)

---

## ⚠️ Read this first

This is **not malware**. It does not exfiltrate data, does not install a backdoor, does not phone home, does not encrypt files. It is a **troll payload** that:

- spams `MessageBoxW` windows with creepy text,
- shakes every visible window on the desktop,
- plays random `Beep` frequencies ("scream"),
- kills `explorer.exe` (desktop + taskbar disappear),
- flips the screen orientation,
- flashes the whole screen white/black,
- spawns fullscreen black "jumpscare" windows with drawn red eyes,
- blocks keyboard and mouse input for ~20 seconds via `BlockInput(True)`.

**Do not run this on someone else's machine without explicit consent.** That is a crime in most jurisdictions (unauthorized modification of a computer system). The author is not responsible for what you do with it.

**Run it on a VM.** The screen flash overwrites the entire desktop — unsaved work in other apps can be lost.

---

## Demo

_TODO: add a 10-second screen recording of the payload running in a VM._

(If you fork this, please add a GIF. Pull requests welcome.)

---

## Requirements

- Windows 10 or 11
- Python 3.10+
- No third-party packages (only stdlib + `ctypes` + `winsound`)

---

## Install

```bash
git clone https://github.com/<your-user>/idiot-nightmare.git
cd idiot-nightmare
