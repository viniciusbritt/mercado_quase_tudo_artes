import os
from playwright.sync_api import sync_playwright
import os, sys
K = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
D = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "./saida")  # pasta de trabalho (recortes e saída)
os.makedirs(D, exist_ok=True)
K = os.path.abspath(K)
FONTS = """
@font-face{font-family:"Disp";src:url("file:///usr/share/fonts/opentype/inter/InterDisplay-Black.otf");font-weight:900}
@font-face{font-family:"Pop";src:url("file:///usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf");font-weight:500}
@font-face{font-family:"Pop";src:url("file:///usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf");font-weight:700}
"""

def doc(H):
    story = H == 1920
    off = 230 if story else 0          # deslocamento vertical do bloco no story
    gas_h = 900 if story else 760
    return f"""<!doctype html><meta charset=utf-8><style>{FONTS}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1080px;height:{H}px;overflow:hidden}}
body{{font-family:"Pop",sans-serif;color:#fff;position:relative;
 background:radial-gradient(60% 40% at 30% {48 if story else 55}%,rgba(255,140,40,.55),transparent 70%),
 radial-gradient(70% 45% at 15% 8%,rgba(123,63,176,.95),transparent 70%),
 linear-gradient(180deg,#53228A 0%,#4B1E78 45%,#3A1563 100%)}}
.grain{{position:absolute;inset:0;opacity:.16;background-image:radial-gradient(rgba(255,255,255,.55) 1px,transparent 1.3px);background-size:8px 8px}}
.t{{position:absolute;left:64px;top:{70+off}px}}
.t .l1{{font-family:"Disp";font-weight:900;font-size:136px;line-height:.9;letter-spacing:-.035em}}
.t .l2{{display:inline-block;margin-top:12px;font-family:"Disp";font-weight:900;font-size:88px;line-height:1;color:#4B1E78;background:#FFD400;padding:4px 26px 14px;border-radius:26px;transform:rotate(-2.5deg);box-shadow:0 10px 0 #E1251B}}
.box{{position:absolute;right:64px;top:{78+off}px;width:300px;background:#2C0D4D;border-radius:32px;padding:24px 20px;text-align:center;box-shadow:0 16px 40px rgba(0,0,0,.25)}}
.box .big{{font-family:"Disp";font-weight:900;font-size:46px;line-height:1}}
.box .big em{{font-style:normal;color:#FFD400}}
.box .small{{margin-top:10px;font-weight:500;font-size:22px;line-height:1.25;color:#E9DDF7}}
.glow{{position:absolute;left:{40}px;top:{(430 if not story else 700)}px;width:640px;height:640px;border-radius:50%;background:radial-gradient(closest-side,rgba(255,200,90,.55),rgba(255,120,30,.25) 55%,transparent 75%)}}
.gas{{position:absolute;left:{70 if not story else 60}px;top:{(380 if not story else 640)}px;height:{gas_h}px;filter:drop-shadow(0 40px 40px rgba(20,5,40,.55));transform:rotate(-4deg)}}
.tag{{position:absolute;z-index:4;right:{60 if not story else 70}px;top:{(850 if not story else 1240)}px;transform:rotate(-4deg);text-align:center}}
.tag .p{{background:#FFD400;color:#4B1E78;border-radius:40px;padding:6px 34px 16px;display:flex;align-items:flex-start;gap:6px;box-shadow:0 14px 0 #E1251B,0 30px 40px rgba(0,0,0,.35)}}
.tag .rs{{font-family:"Disp";font-weight:900;font-size:54px;margin-top:52px;color:#E1251B}}
.tag .int{{font-family:"Disp";font-weight:900;font-size:220px;line-height:.92;letter-spacing:-.05em}}
.tag .cent{{font-family:"Disp";font-weight:900;font-size:96px;line-height:.9;margin-top:24px}}
.tag .cond{{margin:30px auto 0;display:inline-block;background:#fff;color:#4B1E78;border-radius:999px;padding:12px 26px;font-weight:700;font-size:28px;line-height:1.15;box-shadow:0 12px 26px rgba(0,0,0,.3)}}
.tag .cond b{{color:#E1251B}}
.brit{{position:absolute;z-index:3;right:{40 if not story else 30}px;top:{(310 if not story else 520)}px;height:{500 if not story else 700}px;filter:drop-shadow(-10px 20px 30px rgba(20,5,40,.4))}}
.foot{{z-index:5;position:absolute;left:64px;right:64px;bottom:{44 if not story else 250}px;height:92px;background:#fff;border-radius:999px;display:flex;align-items:center;gap:22px;padding:0 30px 0 26px;color:#4B1E78}}
.foot img{{height:50px}}
.foot .end{{font-weight:700;font-size:22px;line-height:1.25;white-space:nowrap}}
.foot .end span{{display:block;font-weight:500;color:#5b4a6e;font-size:19px}}
.foot .zap{{margin-left:auto;background:#4B1E78;color:#fff;border-radius:999px;padding:12px 22px;font-weight:700;font-size:21px;white-space:nowrap;line-height:1.1;text-align:center}}
.legal{{position:absolute;left:64px;right:64px;bottom:{10 if not story else 215}px;text-align:center;font-size:15px;color:rgba(255,255,255,.75)}}
</style>
<div class="grain"></div>
<div class="t"><div class="l1">Domingão</div><div class="l2">do Gás 🔥</div></div>
<div class="box"><div class="big">DOMINGO<br><em>01/11</em></div><div class="small">Aberto das 7h30 às 12h30</div></div>
<div class="glow"></div>
<img class="gas" src="file://{K}/produtos/botijao_gas_p13_grande.png">
<img class="brit" src="file://{K}/britinho_celular_whatsapp.png">
<div class="tag"><div class="p"><span class="rs">R$</span><span class="int">110</span><span class="cent">,00</span></div>
<div class="cond"><b>À vista</b> e para <b>retirada</b> na loja</div></div>
<div class="foot"><img src="file://{K}/logo.png"><div class="end">Av. João Farah, 649 · Ibitinga<span>Alto dos Pinheiros</span></div><div class="zap"><span style="font-weight:500;font-size:16px;display:block;opacity:.85">WhatsApp</span>(16) 3341-7427</div></div>
<div class="legal">Gás P13. Imagens meramente ilustrativas. Válido enquanto durarem os estoques.</div>
"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for nome, H in (("feed", 1440), ("story", 1920)):
        f = f"{D}/gas_{nome}.html"; open(f, "w").write(doc(H))
        pg = b.new_page(viewport={"width": 1080, "height": H})
        pg.goto("file://" + f); pg.wait_for_timeout(400)
        pg.screenshot(path=f"{D}/gas_{nome}.png"); pg.close()
    b.close()
from PIL import Image
a = Image.open(D + "/gas_feed.png").resize((540, 720)); s = Image.open(D + "/gas_story.png").resize((405, 720))
c = Image.new("RGB", (955, 720), "white"); c.paste(a, (0, 0)); c.paste(s, (550, 0)); c.save(D + "/sheet.jpg")
print("ok")
