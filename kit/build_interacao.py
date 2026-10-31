"""Stories de INTERACAO (isso ou aquilo / quiz / arrasta ai). Edite ARTES e rode: python3 build_interacao.py
Poses: p_<nome>.png nesta pasta (recorte chroma do Flow). Espaco vazio embaixo e para a figurinha do Instagram."""
import os
from playwright.sync_api import sync_playwright
S = "/tmp/claude-0/-home-claude/283c481c-64ea-5d96-8655-3e47568e5090/scratchpad"
K = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
D = os.path.dirname(os.path.abspath(__file__))  # poses recortadas p_<nome>.png ficam nesta pasta; saida em D

FONTS = """
@font-face{font-family:"Disp";src:url("file:///usr/share/fonts/opentype/inter/InterDisplay-Black.otf");font-weight:900}
@font-face{font-family:"Pop";src:url("file:///usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf");font-weight:500}
@font-face{font-family:"Pop";src:url("file:///usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf");font-weight:700}
"""
BASE = FONTS + """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden}
body{background:#3C1A7B;font-family:"Pop",sans-serif;color:#fff;position:relative}
.top{position:absolute;top:226px;left:72px;right:72px;display:flex;align-items:center;justify-content:space-between}
.serie{display:inline-block;background:#FFD400;color:#3C1A7B;font-family:"Disp";font-weight:900;font-size:40px;border-radius:999px;padding:8px 26px 12px;transform:rotate(-2deg);box-shadow:0 8px 0 #E1251B}
.logo{background:#fff;border-radius:999px;padding:10px 20px}
.logo img{height:46px;display:block}
.prog{position:absolute;top:196px;left:72px;display:flex;gap:10px}
.prog i{display:block;width:60px;height:8px;border-radius:8px;background:rgba(255,255,255,.25)}
.prog i.on{background:#FFD400}
.q{position:absolute;left:72px;right:72px;top:330px;font-family:"Disp";font-weight:900;font-size:84px;line-height:.98;letter-spacing:-.025em;text-wrap:balance}
.q .y{color:#FFD400}
.halo{position:absolute;left:50%;transform:translateX(-50%);width:820px;height:820px;border-radius:50%;background:radial-gradient(closest-side,rgba(126,74,214,.55),rgba(60,26,123,0))}
.brit{position:absolute;left:50%;transform:translateX(-50%);filter:drop-shadow(0 26px 30px rgba(10,0,30,.45))}
.chao{position:absolute;left:50%;transform:translateX(-50%);width:420px;height:50px;border-radius:50%;background:radial-gradient(closest-side,rgba(0,0,0,.5),rgba(0,0,0,0))}
.tag{position:absolute;background:#fff;color:#3C1A7B;font-family:"Disp";font-weight:900;font-size:50px;line-height:1;border-radius:24px;padding:16px 26px 20px;box-shadow:0 12px 0 #FFD400,0 24px 34px rgba(10,0,30,.35);z-index:3}
.tag.l{transform:rotate(-5deg)} .tag.r{transform:rotate(5deg)}
.vs{position:absolute;left:50%;transform:translateX(-50%) rotate(-6deg);width:120px;height:120px;border-radius:50%;background:#E1251B;color:#fff;font-family:"Disp";font-weight:900;font-size:56px;display:grid;place-items:center;z-index:4;box-shadow:0 10px 24px rgba(0,0,0,.35)}
.hint{position:absolute;left:0;right:0;text-align:center;font-weight:700;font-size:34px;color:#E7DAFF;letter-spacing:.02em}
.hint b{color:#FFD400}
"""

def prog(n, tot=3):
    return '<div class="prog">' + "".join(f'<i class="{"on" if i <= n else ""}"></i>' for i in range(1, tot + 1)) + '</div>'

def top(serie):
    return f'<div class="top"><div class="serie">{serie}</div><div class="logo"><img src="file://{K}/logo.png"></div></div>'

def poll(n, q, a, b, pose, h=900, btop=610, tagtop=545, hint="Vota aqui embaixo 👇"):
    return f"""<style>{BASE}</style>{prog(n)}{top("ISSO OU AQUILO?")}
<div class="q">{q}</div>
<div class="halo" style="top:{btop+40}px"></div>
<div class="tag l" style="left:60px;top:{tagtop}px">{a}</div>
<div class="tag r" style="right:60px;top:{tagtop}px">{b}</div>
<div class="chao" style="top:{btop+h-30}px"></div>
<img class="brit" src="file://{D}/p_{pose}.png" style="top:{btop}px;height:{h}px">
<div class="hint" style="top:{btop+h+18}px"><b>{hint}</b></div>
"""

def quiz(n, q, pose, h=840, btop=600, hint="Responde no quiz 👇 e veja se acertou!"):
    return f"""<style>{BASE}</style>{prog(n)}{top("QUIZ DO BRITINHO 🧠")}
<div class="q" style="font-size:76px">{q}</div>
<div class="halo" style="top:{btop+20}px"></div>
<div class="chao" style="top:{btop+h-30}px"></div>
<img class="brit" src="file://{D}/p_{pose}.png" style="top:{btop}px;height:{h}px">
<div class="hint" style="top:{btop+h+18}px">{hint}</div>
"""

def slider(n, q, pose, h=860, btop=600, hint="Arrasta o emoji até onde você concorda 👇"):
    return f"""<style>{BASE}</style>{prog(n)}{top("ARRASTA AÍ ☕")}
<div class="q">{q}</div>
<div class="halo" style="top:{btop+20}px"></div>
<div class="chao" style="top:{btop+h-30}px"></div>
<img class="brit" src="file://{D}/p_{pose}.png" style="top:{btop}px;height:{h}px">
<div class="hint" style="top:{btop+h+18}px">{hint}</div>
"""

ARTES = {
    "2026-10-28_isso-ou-aquilo_1": poll(1, 'No almoço, qual desce <span class="y">melhor?</span>', "COCA-COLA", "GUARANÁ", "refri"),
    "2026-10-28_isso-ou-aquilo_2": poll(2, 'No café da manhã, você é <span class="y">time…</span>', "PÃO DE<br>QUEIJO", "PÃO NA<br>CHAPA", "paes", tagtop=530),
    "2026-10-28_isso-ou-aquilo_3": poll(3, 'Noite de lanche pede o <span class="y">quê?</span>', "PIZZA", "HAMBÚRGUER", "pizza"),
    "2026-10-30_quiz_1": quiz(1, 'A banana é uma <span class="y">baga</span>, igual à uva. Verdade ou mentira?', "banana"),
    "2026-10-30_quiz_2": quiz(2, 'Ovo de casca <span class="y">marrom</span> é mais nutritivo que o branco?', "ovos"),
    "2026-10-30_slider_3": slider(3, 'Café passado na hora numa <span class="y">sexta de manhã</span> é…', "cafe"),
}

if __name__ == "__main__":
    os.makedirs(D + "/out", exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for nome, h in ARTES.items():
            f = f"{D}/{nome}.html"; open(f, "w").write("<!doctype html><meta charset=utf-8>" + h)
            pg = b.new_page(viewport={"width": 1080, "height": 1920})
            pg.goto("file://" + f); pg.wait_for_timeout(400)
            pg.screenshot(path=f"{D}/{nome}.png"); pg.close()
        b.close()
    from PIL import Image
    ims = [Image.open(f"{D}/{n}.png").resize((360, 640)) for n in ARTES]
    c = Image.new("RGB", (6 * 370, 640), "white")
    for i, im in enumerate(ims): c.paste(im, (i * 370, 0))
    c.save(D + "/sheet.jpg")
    print("ok")
