"""Arte de OFERTAS MÚLTIPLAS (2 a 3 produtos do mesmo setor) no estilo do Quase Tudo.
Uso: python build_combo.py combo.json saida_base  -> saida_base_feed.png e saida_base_story.png
combo.json: {"tema":"acougue","titulo1":"Ofertas","titulo2":"do Açougue","caixa":"...","caixa_apoio":"...","evento":"Açougue",
             "britinho":"pose corpo inteiro.png","itens":[{"nome":"","detalhe":"","preco":11.5,"unidade":"kg","foto":"recorte.png"}]}
"""
import os, sys, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_oferta as bo
from playwright.sync_api import sync_playwright

def doc(o, H):
    T = bo.TEMAS[o.get("tema", "padrao")]
    itens = ""
    for it in o["itens"]:
        rs, cent = bo.preco(it["preco"])
        itens += f'''<div class="it"><div class="ph"><img src="file://{it['foto']}"></div>
<div class="tx"><div class="nm">{html.escape(it['nome'])}</div><div class="dt">{html.escape(it.get('detalhe',''))}</div></div>
<div class="pt"><span class="r">R$</span><span class="i">{rs}</span><span class="d"><span class="c">,{cent}</span><span class="u">{html.escape(it.get('unidade','kg'))}</span></span></div></div>'''
    box = f'<div class="big">{o.get("caixa","ESTOQUE<br><em>LIMITADO!</em>")}</div>' + (f'<div class="small">{html.escape(o["caixa_apoio"])}</div>' if o.get("caixa_apoio") else "") + (f'<div class="ev">{html.escape(o["evento"])}</div>' if o.get("evento") else "")
    logo = os.path.join(bo.A, "logo.png")
    extra = """
.itens{position:absolute;left:52px;width:700px;top:380px;display:flex;flex-direction:column;gap:26px;z-index:2}
.it{position:relative;height:250px;background:#fff;border-radius:40px;box-shadow:0 22px 44px rgba(30,0,0,.35);display:flex;align-items:center;padding:0 24px 0 16px}
.ph{width:230px;height:220px;display:grid;place-items:center;flex:none}
.ph img{max-width:100%;max-height:100%;filter:drop-shadow(0 12px 12px rgba(60,10,10,.25))}
.tx{flex:1;padding:0 10px 0 14px}
.nm{font-family:"Disp";font-weight:900;font-size:44px;line-height:1;color:#3E0604;letter-spacing:-.01em}
.dt{margin-top:10px;font-weight:500;font-size:21px;line-height:1.25;color:#7a5250}
.pt{position:absolute;right:-26px;bottom:-22px;background:var(--amar);border-radius:26px;padding:4px 18px 10px 14px;display:flex;align-items:flex-start;gap:4px;color:var(--roxo);box-shadow:0 9px 0 var(--verm),0 18px 26px rgba(0,0,0,.3);transform:rotate(-3deg)}
.pt .r{font-family:"Disp";font-weight:900;font-size:28px;margin-top:30px;color:var(--verm)}
.pt .i{font-family:"Disp";font-weight:900;font-size:104px;line-height:.95;letter-spacing:-.04em}
.pt .d{display:flex;flex-direction:column;margin-top:12px}
.pt .c{font-family:"Disp";font-weight:900;font-size:50px;line-height:.9}
.pt .u{font-weight:700;font-size:22px;color:var(--verm);margin-left:4px}
.brit2{position:absolute;right:-20px;bottom:132px;height:1010px;z-index:3;filter:drop-shadow(-10px 20px 30px rgba(30,0,0,.4))}
"""
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{bo.css(T, H)}{extra}{o.get('css','')}</style></head><body>
<div class="grain"></div><div class="deco"></div><div class="cv">
<div class="title"><div class="l1">{html.escape(o.get('titulo1','Ofertas'))}</div><div class="l2">{html.escape(o.get('titulo2','do Quase Tudo'))}</div></div>
<div class="box">{box}</div>
<div class="itens">{itens}</div>
{('<img class="brit2" src="file://'+o['britinho']+'">') if o.get('britinho') else ''}
<div class="foot"><img src="file://{logo}"><div class="end">Av. João Farah, 649 · Ibitinga<span>Alto dos Pinheiros</span></div><div class="zap"><span style="font-weight:500;font-size:16px;display:block;opacity:.85">WhatsApp</span>(16) 3341-7427</div></div>
<div class="legal">Imagens meramente ilustrativas. Ofertas válidas enquanto durarem os estoques.</div>
</div></body></html>"""

def build(o, base):
    outs = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for nome, H in (("feed", 1440), ("story", 1920)):
            f = f"{base}_{nome}.html"; open(f, "w").write(doc(o, H))
            pg = b.new_page(viewport={"width": 1080, "height": H}); pg.goto("file://" + os.path.abspath(f)); pg.wait_for_timeout(500)
            out = f"{base}_{nome}.png"; pg.screenshot(path=out); outs.append(out); pg.close()
        b.close()
    return outs

if __name__ == "__main__":
    print(build(json.load(open(sys.argv[1])), sys.argv[2]))
