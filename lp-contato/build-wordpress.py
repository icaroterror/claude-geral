"""Gera wordpress-colar.html: versão autocontida da LP para colar num bloco
"HTML personalizado" / widget HTML do Elementor (imagens embutidas em WebP)."""
import base64, io, re
from PIL import Image

SIZES = {'fernanda.jpg': 720, 'equipe.jpg': 900, 'recepcao.jpg': 1000, 'estacoes.jpg': 1000,
         'sala-reunioes.jpg': 600, 'sala-presidencia.jpg': 600, 'corredores.jpg': 700,
         'estacao-trabalho.jpg': 600, 'logo.png': 420}

def data_uri(name):
    im = Image.open('img/' + name)
    w = SIZES[name]
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    if name.endswith('.png'):
        im.save(buf, 'WEBP', lossless=True)
    else:
        im.convert('RGB').save(buf, 'WEBP', quality=72, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()

src = open('index.html', encoding='utf8').read()
style = re.search(r'<style>.*?</style>', src, re.S).group(0)
ld = re.search(r'<script type="application/ld\+json">.*?</script>', src, re.S).group(0)
body = re.search(r'<body>(.*)</body>', src, re.S).group(1)
body = re.sub(r'<noscript>.*?</noscript>\s*', '', body, flags=re.S)  # GTM já está no site

cache = {}
def repl(m):
    n = m.group(1)
    cache.setdefault(n, data_uri(n))
    return 'src="' + cache[n] + '"'
body = re.sub(r'src="img/([\w.-]+)"', repl, body)

fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,800;1,700'
         '&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">')
out = ('<!-- LP Contato CC&M: colar num bloco HTML personalizado, em página com template sem cabeçalho/rodapé -->\n'
       + fonts + '\n' + style + '\n' + ld + '\n' + body.strip() + '\n')
open('wordpress-colar.html', 'w', encoding='utf8').write(out)
print(f'wordpress-colar.html: {len(out)/1024:.0f} KB')
