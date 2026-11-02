"""CAPA dos Reels do Quase Tudo (1080x1920). Todo Reels tem capa.
Uso: python3 build_capa.py capa.json saida.jpg
capa.json:
  serie     texto da pílula amarela (ex.: "Psiu, oferta!", "História do Quase Tudo · Cap. 1", "Britinho resolve", "Café da Manhã #3")
  titulo    título grande; <mk>…</mk> = palavra em amarelo. Até ~7 palavras.
  apoio     (opcional) linha curta abaixo do título
  preco     (opcional) ex. "59,90" → etiqueta amarela; unidade (opcional) ex. "kg"
  britinho  caminho da pose recortada (PNG) de CORPO INTEIRO (nunca a "espiando"); fica apoiado no chão
  foto      (opcional) foto de fundo (fachada, foto antiga, produto); fica escurecida atrás
  produto   (opcional) recorte do produto ao lado do Britinho
  sepia     (opcional, true) deixa a foto de fundo com cara de época (série História)
Tudo que importa fica no miolo 1080x1350 (y 285–1635), que é o que aparece na grade do perfil.
"""
import os, sys, json, re, html
from playwright.sync_api import sync_playwright
K = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
FONTS = """
@font-face{font-family:"Disp";src:url("file:///usr/share/fonts/opentype/inter/InterDisplay-Black.otf");font-weight:900}
@font-face{font-family:"Pop";src:url("file:///usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf");font-weight:500}
@font-face{font-family:"Pop";src:url("file:///usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf");font-weight:700}
"""
def esc(t):
    t = html.escape(t or "")
    return t.replace("&lt;mk&gt;", '<span class="mk">').replace("&lt;/mk&gt;", "</span>")

def doc(o):
    foto = o.get("foto")
    bg = (f'<div class="foto" style="background-image:url(\'file://{os.path.abspath(foto)}\');{"filter:sepia(.55) saturate(.8) contrast(1.05);" if o.get("sepia") else ""}"></div><div class="veu"></div>' if foto else "")
    preco = ""
    if o.get("preco"):
        i, _, c = str(o["preco"]).partition(",")
        preco = f'<div class="tag"><span class="rs">R$</span><span class="i">{html.escape(i)}</span><span class="d"><span class="c">,{html.escape(c or "00")}</span><span class="u">{html.escape(o.get("unidade",""))}</span></span></div>'
    prod = f'<img class="prod" src="file://{os.path.abspath(o["produto"])}">' if o.get("produto") else ""
    brit = f'<img class="brit" src="file://{os.path.abspath(o["britinho"])}">' if o.get("britinho") else ""
    apoio = f'<div class="apoio">{esc(o["apoio"])}</div>' if o.get("apoio") else ""
    return f"""<!doctype html><meta charset=utf-8><style>{FONTS}
*{{box-sizing:border-box;margin:0;padding:0}}html,body{{width:1080px;height:1920px;overflow:hidden}}
body{{font-family:"Pop";color:#fff;position:relative;background:
 radial-gradient(60% 35% at 50% 78%,rgba(255,170,60,.35),transparent 70%),
 radial-gradient(70% 40% at 15% 10%,rgba(123,63,176,.95),transparent 70%),
 linear-gradient(180deg,#53228A 0%,#4B1E78 50%,#3A1563 100%)}}
.foto{{position:absolute;inset:0;background-size:cover;background-position:center}}
.veu{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(43,12,80,.92) 0%,rgba(60,26,123,.55) 45%,rgba(43,12,80,.88) 100%)}}
.grain{{position:absolute;inset:0;opacity:.13;background-image:radial-gradient(rgba(255,255,255,.55) 1px,transparent 1.3px);background-size:8px 8px}}
.top{{position:absolute;left:70px;right:70px;top:300px;display:flex;justify-content:space-between;align-items:center}}
.serie{{background:#FFD400;color:#4B1E78;font-family:"Disp";font-weight:900;font-size:40px;border-radius:999px;padding:8px 28px 14px;transform:rotate(-2deg);box-shadow:0 8px 0 #E1251B;max-width:720px}}
.logo{{background:#fff;border-radius:999px;padding:10px 20px}}.logo img{{height:48px;display:block}}
.txt{{position:absolute;left:70px;right:70px;top:420px;display:flex;flex-direction:column;gap:20px}}
.tit{{font-family:"Disp";font-weight:900;font-size:112px;line-height:.93;letter-spacing:-.035em;text-wrap:balance;text-shadow:0 6px 24px rgba(20,0,40,.35)}}
.mk{{color:#FFD400}}
.apoio{{font-weight:700;font-size:38px;line-height:1.2;color:#EADCFF}}
.chao{{position:absolute;left:50%;transform:translateX(-50%);top:1590px;width:640px;height:70px;border-radius:50%;background:radial-gradient(closest-side,rgba(0,0,0,.5),transparent)}}
.brit{{position:absolute;left:50%;transform:translateX(-50%);bottom:{1920-1625}px;max-height:880px;max-width:900px;filter:drop-shadow(0 26px 30px rgba(10,0,30,.45))}}
.prod{{position:absolute;right:70px;bottom:{1920-1615}px;max-height:420px;max-width:380px;filter:drop-shadow(0 24px 24px rgba(10,0,30,.45))}}
.tag{{position:absolute;left:70px;top:1180px;background:#FFD400;color:#4B1E78;border-radius:36px;padding:4px 28px 14px;display:flex;align-items:flex-start;gap:6px;transform:rotate(-4deg);box-shadow:0 12px 0 #E1251B,0 26px 36px rgba(0,0,0,.35);z-index:3}}
.tag .rs{{font-family:"Disp";font-weight:900;font-size:44px;margin-top:40px;color:#E1251B}}
.tag .i{{font-family:"Disp";font-weight:900;font-size:170px;line-height:.92;letter-spacing:-.05em}}
.tag .d{{display:flex;flex-direction:column;margin-top:20px}}.tag .c{{font-family:"Disp";font-weight:900;font-size:76px;line-height:.9}}
.tag .u{{font-weight:700;font-size:28px;color:#E1251B;margin-left:4px}}
</style>{bg}<div class="grain"></div>
<div class="top"><div class="serie">{esc(o.get("serie",""))}</div><div class="logo"><img src="file://{K}/logo.png"></div></div>
<div class="txt"><div class="tit">{esc(o.get("titulo",""))}</div>{apoio}</div>
<div class="chao"></div>{brit}{prod}{preco}
"""

def build(o, saida):
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
        f = os.path.splitext(saida)[0] + ".html"; open(f, "w").write(doc(o))
        pg.goto("file://" + os.path.abspath(f)); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(400)
        pg.screenshot(path=saida, type="jpeg", quality=92); b.close()
    return saida

if __name__ == "__main__":
    print(build(json.load(open(sys.argv[1])), sys.argv[2]))
