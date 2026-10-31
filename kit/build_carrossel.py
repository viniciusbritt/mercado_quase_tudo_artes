"""Carrossel "Quase Tudo que você não sabia" (feed 1080x1440 + story da capa 1080x1920).
Uso: python build_carrossel.py carrossel.json pasta_saida
Regras de texto: até ~22 palavras por slide, frases curtas, 1 ideia por slide, fatos com fonte.

carrossel.json:
{
  "slug": "carrinho",
  "capa":  {"titulo": "O carrinho quase foi <mk>um fracasso</mk>", "apoio": "Ninguém queria usar.", "foto": "caminho.jpg"},
  "slides": [ {"eyebrow": "1937 · Oklahoma, EUA", "titulo": "(opcional)", "texto": "Texto com <b>destaque</b>.", "foto": "(opcional)", "nota": "(opcional)"} ],
  "cta":   {"gancho": "Hoje ninguém precisa…", "titulo": "Frase ligando o tema ao Quase Tudo.", "foto": "(opcional)"}
}
<mk>…</mk> = marca-texto amarelo; <b>…</b> = destaque roxo.
"""
import os, sys, json, re
from playwright.sync_api import sync_playwright

D = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(D, "assets")
LOGO = os.path.join(A, "logo.png")

CSS = """
@font-face{font-family:"Disp";src:url("file:///usr/share/fonts/opentype/inter/InterDisplay-Black.otf");font-weight:900}
@font-face{font-family:"Disp";src:url("file:///usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf");font-weight:800}
@font-face{font-family:"Pop";src:url("file:///usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf");font-weight:400}
@font-face{font-family:"Pop";src:url("file:///usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf");font-weight:500}
@font-face{font-family:"Pop";src:url("file:///usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf");font-weight:700}
@font-face{font-family:"Note";src:url("file:///usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf");font-style:italic}
:root{--papel:#F5F0FA;--roxo:#4B1E78;--roxo2:#7B3FB0;--verm:#E1251B;--amar:#FFD400;--tinta:#22152F}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;overflow:hidden}
body{background:var(--papel);color:var(--tinta);font-family:"Pop",sans-serif;position:relative}
.grain{position:absolute;inset:0;opacity:.35;background-image:radial-gradient(rgba(75,30,120,.10) 1px,transparent 1.2px);background-size:7px 7px}
.cv{position:absolute;left:0;width:1080px;height:1440px}
.top{position:absolute;left:64px;right:64px;top:56px;display:flex;justify-content:space-between;align-items:center}
.serie{display:flex;align-items:center;gap:14px;background:var(--roxo);color:#fff;border-radius:999px;padding:10px 30px 10px 10px;font-weight:700;font-size:30px;letter-spacing:.01em}
.serie .q{width:52px;height:52px;border-radius:50%;background:var(--amar);color:var(--roxo);display:grid;place-items:center;font-family:"Disp";font-weight:900;font-size:36px}
.serie em{font-style:normal;color:var(--amar)}
.cnt{font-family:"Disp";font-weight:800;font-size:32px;color:var(--roxo2);font-variant-numeric:tabular-nums}
.foto{position:absolute;background:#fff;padding:16px 16px 18px;box-shadow:0 18px 40px rgba(34,21,47,.18)}
.foto img{display:block;width:100%;height:100%;object-fit:cover}
.fita{position:absolute;width:150px;height:44px;background:rgba(255,212,0,.75);top:-20px;left:50%;transform:translateX(-50%) rotate(-4deg)}
.eyebrow{font-weight:700;font-size:36px;letter-spacing:.1em;text-transform:uppercase;color:var(--verm)}
h1{font-family:"Disp";font-weight:900;color:var(--roxo);line-height:.98;letter-spacing:-.02em;text-wrap:balance}
mk{background:linear-gradient(transparent 58%,rgba(255,212,0,.9) 58%,rgba(255,212,0,.9) 92%,transparent 92%);padding:0 6px}
.body{font-size:50px;line-height:1.3;color:var(--tinta);text-wrap:pretty}
.body b{color:var(--roxo);font-weight:700}
.nota{font-family:"Note";font-style:italic;font-size:30px;color:#6C5F79;margin-top:18px}
.swipe{position:absolute;right:64px;bottom:64px;background:var(--verm);color:#fff;font-weight:700;font-size:32px;border-radius:999px;padding:18px 34px}
.txt{position:absolute;left:72px;right:72px;display:flex;flex-direction:column;gap:16px}
.cta{position:absolute;left:0;right:0;bottom:0;background:var(--roxo);color:#fff;padding:40px 72px 44px}
.cta h2{font-family:"Disp";font-weight:900;font-size:50px;line-height:1.05;margin-bottom:14px;padding-right:260px}
.cta .row{display:flex;gap:16px;align-items:flex-start;font-size:30px;line-height:1.34;margin-top:12px}
.cta .row span.i{flex:none;width:46px;height:46px;border-radius:50%;background:var(--amar);display:grid;place-items:center;margin-top:2px}
.cta .slogan{margin-top:24px;font-family:"Disp";font-weight:900;font-size:42px;color:var(--amar)}
.logo{position:absolute;background:#fff;border-radius:18px;padding:10px 16px}
.logo img{display:block;width:230px}
.brand{position:absolute;right:72px;bottom:46px;width:210px;opacity:.95}
.storytop{position:absolute;left:0;right:0;top:120px;text-align:center;font-family:"Disp";font-weight:900;font-size:54px;color:var(--roxo)}
.storybot{position:absolute;left:0;right:0;bottom:170px;text-align:center}
.storybot span{display:inline-block;background:var(--verm);color:#fff;font-weight:700;font-size:36px;border-radius:999px;padding:18px 40px}
"""

FIT = """<script>
for(const el of document.querySelectorAll('[data-fit]')){
  const max=+el.dataset.fit; let fs=parseFloat(getComputedStyle(el).fontSize);
  const kids=el.querySelectorAll('.body,h1');
  while(el.scrollHeight>max && fs>36){ fs-=2; kids.forEach(k=>k.style.fontSize=(k.tagName==='H1'?fs*1.6:fs)+'px'); }
}
</script>"""

ICONS = {
 "ok": '<svg width="26" height="26" viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="#4B1E78" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 "pin": '<svg width="26" height="26" viewBox="0 0 24 24"><path fill="#4B1E78" d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg>',
 "clock": '<svg width="26" height="26" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="none" stroke="#4B1E78" stroke-width="2.6"/><path d="M12 7v5l3.5 2" fill="none" stroke="#4B1E78" stroke-width="2.6" stroke-linecap="round"/></svg>',
 "zap": '<svg width="26" height="26" viewBox="0 0 24 24"><rect x="6" y="2" width="12" height="20" rx="3" fill="none" stroke="#4B1E78" stroke-width="2.6"/><circle cx="12" cy="18" r="1.4" fill="#4B1E78"/></svg>',
}

def foto(path, x, y, w, h, rot):
    return f'<div class="foto" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;transform:rotate({rot}deg)"><div class="fita"></div><img src="file://{path}"></div>'

def top(n, total):
    return f'<div class="top"><div class="serie"><span class="q">?</span><span>Quase Tudo <em>que você não sabia</em></span></div><div class="cnt">{n}/{total}</div></div>'

def wrap(inner, H=1440, extra=""):
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}html,body{{height:{H}px}}.cv{{top:{(H-1440)//2}px}}</style></head><body>
<div class="grain"></div>{extra}<div class="cv">{inner}</div>{FIT}</body></html>"""

def capa(c, total):
    f = foto(c["foto"], 430, 600, 580, 580, 4) if c.get("foto") else ""
    return top(1, total) + f + f"""
<div class="txt" style="top:180px" data-fit="420"><h1 style="font-size:118px">{c['titulo']}</h1></div>
<div class="txt" style="top:1200px;right:110px"><p class="body" style="font-size:52px;font-weight:700;color:var(--verm)">{c.get('apoio','')}</p></div>
<div class="swipe">Arrasta pro lado →</div>"""

def interno(s, n, total):
    lado = n % 2 == 0
    if s.get("foto"):
        f = foto(s["foto"], 330 if lado else 90, 170, 660, 620, -3 if lado else 3)
        topo, alt = 850, 440
    else:
        f, topo, alt = "", None, 1000
    t = ""
    if s.get("eyebrow"): t += f'<div class="eyebrow">{s["eyebrow"]}</div>'
    if s.get("titulo"): t += f'<h1 style="font-size:{84 if s.get("foto") else 104}px">{s["titulo"]}</h1>'
    if s.get("texto"): t += f'<p class="body"{"" if s.get("foto") else " style=font-size:62px"}>{s["texto"]}</p>'
    if s.get("nota"): t += f'<p class="nota">{s["nota"]}</p>'
    pos = f"top:{topo}px" if topo else "top:200px;bottom:220px;justify-content:center"
    return top(n, total) + f + f'<div class="txt" style="{pos}" data-fit="{alt}">{t}</div><img class="brand" src="file://{LOGO}">'

def final(c, n, total):
    f = foto(c["foto"], 430, 150, 580, 620, -3) if c.get("foto") else ""
    r = lambda ic, txt: f'<div class="row"><span class="i">{ICONS[ic]}</span><div>{txt}</div></div>'
    return top(n, total) + f + f"""
<div class="txt" style="top:180px;right:{660 if c.get('foto') else 72}px" data-fit="560"><h1 style="font-size:66px">{c.get('gancho','')}</h1></div>
<div class="cta"><div class="logo" style="right:64px;top:36px"><img src="file://{LOGO}"></div><h2>{c['titulo']}</h2>
{r('ok','Mercado com mais de <b style="color:var(--amar)">26 anos de tradição</b>')}
{r('pin','Av. João Farah, 649 · Alto dos Pinheiros · Ibitinga')}
{r('clock','Segunda à Sexta: 7h30 - 12h30 | 15h - 19h<br>Sábados: 7h30 - 19h<br>Domingos e Feriados: 7h30 - 12h30')}
{r('zap','WhatsApp: (16) 3341-7427')}
<div class="slogan">Quase Tudo… só falta você!</div></div>"""

def build(cfg, outdir):
    os.makedirs(outdir, exist_ok=True)
    slides = cfg["slides"]; total = len(slides) + 2
    pages = [capa(cfg["capa"], total)] + [interno(s, i + 2, total) for i, s in enumerate(slides)] + [final(cfg["cta"], total, total)]
    slug = cfg.get("slug", "carrossel"); outs = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1440})
        for i, inner in enumerate(pages, 1):
            f = os.path.join(outdir, f"{slug}_{i}.html"); open(f, "w").write(wrap(inner))
            pg.goto("file://" + os.path.abspath(f)); pg.wait_for_timeout(450)
            o = os.path.join(outdir, f"{slug}_{i}.png"); pg.screenshot(path=o); outs.append(o)
        pg.close()
        # story: capa centralizada no formato 1080x1920
        ps = b.new_page(viewport={"width": 1080, "height": 1920})
        extra = '<div class="storytop">Post novo no feed!</div><div class="storybot"><span>Toque e arrasta pro lado →</span></div>'
        f = os.path.join(outdir, f"{slug}_story.html"); open(f, "w").write(wrap(pages[0].replace('<div class="swipe">Arrasta pro lado →</div>', ''), 1920, extra))
        ps.goto("file://" + os.path.abspath(f)); ps.wait_for_timeout(450)
        o = os.path.join(outdir, f"{slug}_story.png"); ps.screenshot(path=o); outs.append(o)
        b.close()
    return outs

if __name__ == "__main__":
    print(build(json.load(open(sys.argv[1])), sys.argv[2]))
