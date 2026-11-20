"""python3 tools/celular/aplicar_test.py — injeta() is idempotent and saves the real screen first in <head>."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from aplicar import INI, TELA, injeta

base = '<!doctype html><html><head><meta charset="utf-8"><script>function screen(){}</script></head><body><script src="lib/dist/reveal.js"></script></body></html>'
um = injeta(base)
assert injeta(um) == um, "rodar de novo muda o arquivo"
assert um.index(TELA) < um.index("function screen"), "a tela real tem que ser guardada antes do deck"
assert um.count(INI) == 1 and um.count(TELA) == 1
print("aplicar ok")
