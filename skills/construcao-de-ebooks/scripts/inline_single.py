# Gera uma versão de arquivo único do deck (CSS, JS e fontes embutidos) para enviar a outras pessoas.
# Uso: python3 -I inline_single.py [<deck/index.html> [<saida.html>]]
import base64, os, re, sys

src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'index.html')
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(src), 'slides-de-aula.html')
base = os.path.dirname(os.path.abspath(src))
html = open(src, encoding='utf-8').read()

def read(rel, mode='r'):
    with open(os.path.join(base, rel), mode, **({} if 'b' in mode else {'encoding': 'utf-8'})) as f:
        return f.read()

def font(m):
    rel = m.group(2)
    ext = rel.rsplit('.', 1)[-1]; mime = {'woff2': 'font/woff2', 'woff': 'font/woff', 'ttf': 'font/ttf', 'otf': 'font/otf'}[ext]
    return f"url({m.group(1)}data:{mime};base64,{base64.b64encode(read(rel, 'rb')).decode()}{m.group(1)}"

def css(href):
    # url() relativo dentro do CSS vale a partir da pasta do CSS (fonts/fonts.css → url(X.woff2) = fonts/X.woff2)
    d = os.path.dirname(href)
    return re.sub(r"url\((['\"]?)(?!data:|https?:|/|#)([^)'\"]+)\1\)",
                  lambda m: f"url({m.group(1)}{os.path.normpath(os.path.join(d, m.group(2)))}{m.group(1)})", read(href))

html = re.sub(r'<link rel="stylesheet" href="([^"]+)">', lambda m: f'<style>\n{css(m.group(1))}\n</style>', html)
html = re.sub(r'<script src="([^"]+)"></script>', lambda m: '<script>\n' + read(m.group(1)).replace('</script', '<\\/script') + '\n</script>', html)
html = re.sub(r"url\((['\"]?)([^)'\"]+\.(?:woff2|woff|ttf|otf))\1\)", lambda m: font(m) + ')', html)

left = re.findall(r'(?:src|href)="(?!data:|#|https?:|mailto:)([^"]+\.(?:js|css|woff2|woff|ttf|otf|png|svg|jpg))"', html)
left += re.findall(r"url\(['\"]?(?!data:)([^)'\"]+\.(?:woff2|woff|ttf|otf))", html)
assert not left, f'referências externas restantes: {left}'
open(out, 'w', encoding='utf-8').write(html)
print(out, f'{os.path.getsize(out) / 1e6:.1f} MB')
