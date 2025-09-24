# scripts/edgar.py
from __future__ import annotations
import sys
import threading
import time
from contextlib import contextmanager

SCAN_FRAMES = [
    "[)...................]", "[))..................]", "[))).................]",
    "[))))................]", "[)))))...............]", "[))))))..............]",
    "[))))))).............]", "[))))))))............]", "[)))))))))...........]",
    "[))))))))))..........]", "[))))))))))).........]", "[))))))))))))........]",
    "[))))))))))))).......]", "[))))))))))))))......]", "[))))))))))))))).....]",
    "[))))))))))))))))....]", "[)))))))))))))))))...]", "[))))))))))))))))))..]",
    "[))))))))))))))))))).]", "[))))))))))))))))))))]"
]

SPLASH = r"""
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 XXXXXXXXXXXXXXXXXX         XXXXXXXX
XXXXXXXXXXXXXXXX              XXXXXXX
XXXXXXXXXXXXX                   XXXXX
 XXX     _________ _________     XXX
  XX    I  _xxxxx I xxxxx_  I    XX
 ( X----I         I         I----X )
( +I    I      00 I 00      I    I+ )
 ( I    I    __0  I  0__    I    I )
  (I    I______ /   \_______I    I)
   I           ( ___ )           I
   I    _  :::::::::::::::  _    i
    \    \___ ::::::::: ___/    /
     \_      \_________/      _/
       \        \___,        /
         \                 /
          |\             /|
          |  \_________/  |
       ======================
       |-Edgar the Dossier-|
       |-------Hunter-------|
       |Programmed entirely-|
       |in mom's basement---|
       |by Edgar------(C)1982|
       ======================
""".strip("\n")

def _beep(pattern: list[tuple[float,int]]] | None = None) -> None:
    """
    Cross-platform-ish 'beep'. We’ll use terminal bell (\a) because winsound
    isn't on macOS by default. It’s goofy but fun.
    """
    if not pattern:
        sys.stdout.write("\a")
        sys.stdout.flush()
        return
    for _freq, dur_ms in pattern:
        sys.stdout.write("\a")
        sys.stdout.flush()
        time.sleep(dur_ms / 1000.0)

def splash() -> None:
    # Splash SFX-ish: mimic the PowerShell beeps by timing
    sys.stdout.write("\x1b[2J\x1b[H")  # clear
    print(SPLASH)
    _beep([
        (1567.98,90), (1567.98,90), (1760,90),
        (1567.98,90), (1760,90), (1975.53,90)
    ])
    input("Press ENTER to continue.")
    sys.stdout.write("\x1b[2J\x1b[H")

class EdgarSpinner:
    """
    A lightweight TUI animator you can start/stop around long work.
    """
    def __init__(self, interval: float = 0.5):
        self.interval = interval
        self._stop = threading.Event()
        self._thr: threading.Thread | None = None
        self._frame_i = 0

    def start(self) -> None:
        if self._thr and self._thr.is_alive():
            return
        self._stop.clear()
        self._thr = threading.Thread(target=self._run, daemon=True)
        self._thr.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thr:
            self._thr.join(timeout=1.0)
        # Move to a clean line after stopping
        sys.stdout.write("\n")
        sys.stdout.flush()

    def _run(self) -> None:
        while not self._stop.is_set():
            frame = SCAN_FRAMES[self._frame_i % len(SCAN_FRAMES)]
            self._frame_i += 1
            sys.stdout.write("\x1b[2J\x1b[H")  # clear + home
            print("==========================")
            print("|----Dossier Scanner-----|")
            print("|-----version .0001------|")
            print("|------------------------|")
            print("|Last scan was NEVER ago.|")
            print("|------------------------|")
            print("|-------scanning...------|")
            print(f"|--{frame}|")
            print("==========================")
            sys.stdout.flush()
            time.sleep(self.interval)

    def complete(self) -> None:
        sys.stdout.write("\x1b[2J\x1b[H")
        print("================")
        print("|Scan Complete!|")
        print("|--------------|")
        print("|---423,827----|")
        print("|Viruses Found-|")
        print("|--------------|")
        print("|A New Record!!|")
        print("================")
        _beep([(783.99,700)])

@contextmanager
def edgar_context(show_splash: bool = False, interval: float = 0.5):
    """
    Context manager to wrap any long task:
      with edgar_context(show_splash=args.edgar_splash):
          ...do work...
    """
    spinner = EdgarSpinner(interval=interval)
    try:
        if show_splash:
            splash()
        spinner.start()
        yield spinner
    finally:
        spinner.stop()
        spinner.complete()

def flagrant_system_error_loop() -> None:
    """
    Optional prank loop (off by default!). Use responsibly :)
    """
    _beep([(329.628,150), (415.30,50), (445,700)])
    while True:
        sys.stdout.write("\x1b[2J\x1b[H")
        print("          FLAGRANT SYSTEM ERROR          \n")
        print("             Computer over.              ")
        print("            Virus = Very Yes.            ")
        sys.stdout.flush()
        time.sleep(10)
