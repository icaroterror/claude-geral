"""Gera wordpress-colar.html: versão autocontida da LP para colar no widget HTML
do Elementor (ou bloco "HTML personalizado").

- imagens embutidas em WebP;
- classes e ids prefixados com "ccm-" e todo o CSS escopado em #ccm-lp, para o
  tema/Elementor Kit não sobrescrever fontes, cores e links;
- a LP "vaza" o container do Elementor e ocupa 100% da largura da tela;
- sem GTM (o site já carrega).
"""
import base64, io, os, re, sys
from PIL import Image

P = 'ccm-'
ROOT = '#ccm-lp'
SIZES = {'fernanda.jpg': 720, 'equipe.jpg': 900, 'recepcao.jpg': 1000, 'estacoes.jpg': 1000,
         'sala-reunioes.jpg': 600, 'sala-presidencia.jpg': 600, 'corredores.jpg': 700,
         'estacao-trabalho.jpg': 600, 'logo.png': 420}


def optimized(name):
    im = Image.open('img/' + name)
    w = SIZES[name]
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    if name.endswith('.png'):
        im.save(buf, 'WEBP', lossless=True)
    else:
        im.convert('RGB').save(buf, 'WEBP', quality=72, method=6)
    return buf.getvalue()


# Uso: python3 build-wordpress.py [URL_BASE_DAS_IMAGENS]
# Sem argumento: imagens embutidas (wordpress-colar.html).
# Com URL: imagens externas em <URL>/<nome>.webp (wordpress-colar-leve.html) e
# os .webp são gravados em img-web/ para hospedar.
CDN = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else None

def data_uri(name):
    data = optimized(name)
    if not CDN:
        return 'data:image/webp;base64,' + base64.b64encode(data).decode()
    web = os.path.splitext(name)[0] + '.webp'
    os.makedirs('img-web', exist_ok=True)
    open('img-web/' + web, 'wb').write(data)
    return CDN + '/' + web


src = open('index.html', encoding='utf8').read()
css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
ld = re.search(r'<script type="application/ld\+json">.*?</script>', src, re.S).group(0)
body = re.search(r'<body>(.*)</body>', src, re.S).group(1)
body = re.sub(r'<noscript>.*?</noscript>\s*', '', body, flags=re.S)  # GTM já está no site
body, js = re.match(r'(.*)(<script>.*?</script>)\s*$', body.strip(), re.S).groups()

# ---- nomes de classes e ids ----
classes = set()
for attr in re.findall(r'class="([^"]*)"', body):
    classes.update(attr.split())
classes.add('show')  # adicionada via JS
ids = set(re.findall(r'\bid="([^"]+)"', body))

def cls_attr(m):
    return 'class="' + ' '.join(P + c for c in m.group(1).split()) + '"'
body = re.sub(r'class="([^"]*)"', cls_attr, body)
body = re.sub(r'\bid="([^"]+)"', lambda m: 'id="' + P + m.group(1) + '"', body)
body = re.sub(r'(href|aria-labelledby)="#?([^"]+)"',
              lambda m: m.group(0).replace(m.group(2), P + m.group(2)) if m.group(2) in ids else m.group(0), body)

# ---- CSS: renomeia classes e escopa seletores em #ccm-lp ----
for c in sorted(classes, key=len, reverse=True):
    css = re.sub(r'\.' + re.escape(c) + r'(?![\w-])', '.' + P + c, css)

def scope_selectors(sel):
    out = []
    for s in sel.split(','):
        s = s.strip()
        if s in (':root', 'body'):
            out.append(ROOT)
        elif s == 'html':
            out.append('html')
        elif s == '*':
            out.append(ROOT + ' *')
        else:
            out.append(ROOT + ' ' + s)
    return ','.join(out)

def scope_block(block):
    res, i = [], 0
    while i < len(block):
        j = block.find('{', i)
        if j < 0:
            res.append(block[i:]); break
        head = block[i:j].strip()
        depth, k = 1, j + 1
        while depth:
            depth += {'{': 1, '}': -1}.get(block[k], 0); k += 1
        inner = block[j + 1:k - 1]
        if head.startswith('@media'):
            res.append(head + '{' + scope_block(inner) + '}')
        elif head.startswith('@'):
            res.append(head + '{' + inner + '}')
        else:
            res.append(scope_selectors(head) + '{' + inner + '}')
        i = k
    return '\n'.join(res)

css = scope_block(css)
css += ('\n/* Elementor: ocupa a largura toda e neutraliza estilos do tema */\n'
        'body{overflow-x:hidden}\n'
        + ROOT + '{position:relative;width:100vw;max-width:100vw;margin-left:calc(50% - 50vw);margin-right:calc(50% - 50vw);text-align:left}\n'
        + ROOT + ' a,' + ROOT + ' a:hover,' + ROOT + ' a:focus{text-decoration:none;box-shadow:none}\n'
        + ROOT + ' h1,' + ROOT + ' h2,' + ROOT + ' h3{letter-spacing:normal;text-transform:none}\n'
        + ROOT + ' .' + P + 'faq-list summary{background:none;border:0}\n'
        + ROOT + ' img{border:0;box-shadow:none}\n')

# ---- JS ----
for old, new in [("'.js-wa'", "'.%sjs-wa'" % P), ("'.js-tel'", "'.%sjs-tel'" % P),
                 ("'.hero .btn-wa'", "'.%shero .%sbtn-wa'" % (P, P)), ("'show'", "'%sshow'" % P)]:
    assert old in js, old
    js = js.replace(old, new)
js = re.sub(r"getElementById\('([^']+)'\)", lambda m: "getElementById('%s%s')" % (P, m.group(1)), js)

# ---- imagens ----
cache = {}
def img(m):
    n = m.group(1)
    cache.setdefault(n, data_uri(n))
    return 'src="' + cache[n] + '"'
body = re.sub(r'src="img/([\w.-]+)"', img, body)

fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,800;1,700'
         '&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">')
out = ('<!-- LP Contato CC&M: colar no widget HTML do Elementor (página com layout Elementor Canvas) -->\n'
       + fonts + '\n<style>\n' + css + '\n</style>\n' + ld + '\n<div id="ccm-lp">\n' + body.strip()
       + '\n</div>\n' + js + '\n')
dest = 'wordpress-colar-leve.html' if CDN else 'wordpress-colar.html'
open(dest, 'w', encoding='utf8').write(out)
print(f'{dest}: {len(out)/1024:.0f} KB')
