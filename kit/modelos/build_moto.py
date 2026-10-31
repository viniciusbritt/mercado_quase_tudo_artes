from playwright.sync_api import sync_playwright
import os, sys
K = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
D = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "./saida")  # pasta de trabalho (recortes e saída)
os.makedirs(D, exist_ok=True)
K = os.path.abspath(K)
FONTS='''@font-face{font-family:"Disp";src:url("file:///usr/share/fonts/opentype/inter/InterDisplay-Black.otf");font-weight:900}
@font-face{font-family:"Pop";src:url("file:///usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf");font-weight:500}
@font-face{font-family:"Pop";src:url("file:///usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf");font-weight:700}'''
def doc(H):
    st=H==1920; off=200 if st else 0
    road=1180 if not st else 1440      # topo da rua
    mw=960 if st else 900; mh=int(mw*802/837)
    mtop=road+70-mh                     # rodas apoiadas na rua
    return f'''<!doctype html><meta charset=utf-8><style>{FONTS}
*{{box-sizing:border-box;margin:0;padding:0}}html,body{{width:1080px;height:{H}px;overflow:hidden}}
body{{font-family:"Pop";color:#fff;position:relative;background:
 radial-gradient(55% 35% at 75% 12%,rgba(255,212,0,.35),transparent 70%),
 radial-gradient(70% 45% at 10% 5%,rgba(123,63,176,.95),transparent 70%),
 linear-gradient(180deg,#53228A 0%,#4B1E78 50%,#3A1563 100%)}}
.grain{{position:absolute;inset:0;opacity:.14;background-image:radial-gradient(rgba(255,255,255,.55) 1px,transparent 1.3px);background-size:8px 8px}}
.city{{position:absolute;left:0;right:0;top:{road-330}px;height:330px;display:flex;align-items:flex-end;gap:14px;padding:0 20px;opacity:.35}}
.city i{{display:block;background:#2C0D4D;border-radius:10px 10px 0 0}}
.road{{position:absolute;left:0;right:0;top:{road}px;bottom:0;background:linear-gradient(180deg,#2C0D4D,#22093D)}}
.lane{{position:absolute;left:0;right:0;top:{road+110}px;height:14px;background:repeating-linear-gradient(90deg,#FFD400 0 90px,transparent 90px 160px);opacity:.9}}
.speed{{position:absolute;left:0;top:{mtop+180}px;width:260px}}
.speed b{{display:block;height:10px;border-radius:10px;background:rgba(255,255,255,.55);margin:34px 0}}
.shadow{{position:absolute;left:{(1080-mw)//2+40}px;top:{road+40}px;width:{mw-80}px;height:60px;border-radius:50%;background:radial-gradient(closest-side,rgba(0,0,0,.55),transparent)}}
.moto{{position:absolute;left:{(1080-mw)//2+20}px;top:{mtop}px;width:{mw}px}}
.t{{position:absolute;left:64px;top:{70+off}px;right:64px}}
.l0{{display:inline-block;background:#fff;color:#4B1E78;font-weight:700;font-size:28px;border-radius:999px;padding:8px 24px;margin-bottom:18px}}
.l1{{font-family:"Disp";font-weight:900;font-size:{120 if st else 112}px;line-height:.92;letter-spacing:-.035em}}
.l2{{display:inline-block;margin-top:14px;font-family:"Disp";font-weight:900;font-size:{92 if st else 86}px;line-height:1;color:#4B1E78;background:#FFD400;padding:4px 28px 14px;border-radius:26px;transform:rotate(-2deg);box-shadow:0 10px 0 #E1251B}}
.foot{{z-index:5;position:absolute;left:64px;right:64px;bottom:{44 if not st else 230}px;height:92px;background:#fff;border-radius:999px;display:flex;align-items:center;gap:22px;padding:0 30px 0 26px;color:#4B1E78}}
.foot img{{height:50px}}.foot .end{{font-weight:700;font-size:22px;line-height:1.25;white-space:nowrap}}
.foot .end span{{display:block;font-weight:500;color:#5b4a6e;font-size:19px}}
.foot .zap{{margin-left:auto;background:#4B1E78;color:#fff;border-radius:999px;padding:12px 22px;font-weight:700;font-size:21px;white-space:nowrap;line-height:1.1;text-align:center}}
</style><div class="grain"></div>
<div class="city">{''.join(f'<i style="width:{w}px;height:{h}px"></i>' for w,h in [(90,180),(130,260),(70,140),(150,300),(100,200),(80,240),(140,170),(110,280)])}</div>
<div class="road"></div><div class="lane"></div><div class="shadow"></div>
<div class="speed"><b style="width:220px"></b><b style="width:150px"></b><b style="width:190px"></b></div>
<img class="moto" src="file://{K}/britinho_moto_gas.png">
<div class="t"><div class="l0">Botijão P13 🔥</div><div class="l1">Acabou o gás?</div><div class="l2">Tem no Quase Tudo!</div></div>
<div class="foot"><img src="file://{K}/logo.png"><div class="end">Av. João Farah, 649 · Ibitinga<span>Alto dos Pinheiros</span></div><div class="zap"><span style="font-weight:500;font-size:16px;display:block;opacity:.85">WhatsApp</span>(16) 3341-7427</div></div>'''
with sync_playwright() as p:
    b=p.chromium.launch()
    for n,H in (("feed",1440),("story",1920)):
        f=f"{D}/moto_{n}.html"; open(f,"w").write(doc(H))
        pg=b.new_page(viewport={"width":1080,"height":H}); pg.goto("file://"+f); pg.wait_for_timeout(400)
        pg.screenshot(path=f"{D}/moto_{n}.jpg",type="jpeg",quality=92); pg.close()
    b.close()
from PIL import Image
a=Image.open(D+"/moto_feed.jpg").resize((540,720)); s=Image.open(D+"/moto_story.jpg").resize((405,720))
c=Image.new("RGB",(955,720),"white"); c.paste(a,(0,0)); c.paste(s,(550,0)); c.save(D+"/sheet.jpg")
