import sys, time, threading
from contextlib import contextmanager

_FRAMES = [
    '[)...................]','[))..................]','[))).................]','[))))................]',
    '[)))))...............]','[))))))..............]','[))))))).............]','[))))))))............]',
    '[)))))))))...........]','[))))))))))..........]','[))))))))))).........]','[))))))))))))........]',
    '[))))))))))))).......]','[))))))))))))))......]','[))))))))))))))).....]','[))))))))))))))))....]',
    '[)))))))))))))))))...]','[))))))))))))))))))..]','[))))))))))))))))))).]','[))))))))))))))))))))]'
]

_SPLASH = r""" 
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
       |---Edgar the Virus---
       |-------Hunter-------|
       |Programmed entirely-|
       |in mom's basement---|
       |by Edgar------(C)1982
       ======================
""".strip()

def _beep():
    try:
        import winsound; winsound.Beep(784,90)
    except Exception:
        pass

@contextmanager
def edgar_context(show_splash=False, interval=0.5):
    stop = threading.Event()
    def runner():
        i = 0
        while not stop.is_set():
            sys.stdout.write('==========================
'
                             '|---Virus Protection-----|
'
                             '|-----version .0001------|
'
                             '|------------------------|
'
                             '|Last scan was NEVER ago.|
'
                             '|------------------------|
'
                             f'|-------scanning...------|
|--{_FRAMES[i%len(_FRAMES)]}|
'
                             '==========================
')
            sys.stdout.flush()
            time.sleep(interval); i += 1
    try:
        if show_splash:
            print(_SPLASH); _beep(); time.sleep(1.2)
        t = threading.Thread(target=runner, daemon=True); t.start()
        yield
    finally:
        stop.set(); time.sleep(interval)
        sys.stdout.write('' + ' ' * 80 + '
'); sys.stdout.flush()

def flagrant_system_error_loop():
    try:
        while True:
            print('
          FLAGRANT SYSTEM ERROR          
'
                  '
             Computer over.              
'
                  '            Virus = Very Yes.            
')
            _beep(); time.sleep(3)
    except KeyboardInterrupt:
        pass
