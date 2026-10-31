"""Arte de OFERTA do Quase Tudo (estilo aprovado v3), em feed 1080x1440 e story 1080x1920.
Uso: python build_oferta.py oferta.json saida_sem_extensao
Gera saida_feed.png e saida_story.png.

oferta.json:
  nome, preco (número), unidade, inicio (AAAA-MM-DD), fim (opcional), cond (opcional),
  foto (caminho do produto recortado), britinho (caminho da pose; NUNCA em bebida alcoólica),
  destaque (bool, oferta realmente forte -> "imperdível"), titulo1/titulo2 (opcional),
  layout: "a" (card à esquerda, Britinho na borda direita) ou "b" (card à direita, Britinho na borda ESQUERDA). ALTERNE a cada oferta.
  No layout "b" use uma pose gerada para a borda esquerda (nunca espelhe a imagem: a logo da camisa ficaria invertida).
  Sem "tema"/"evento", o fundo sai pelo tipo de produto (CATEGORIAS): granja, acougue, hortifruti,
  padaria, laticinios, bebidas, limpeza, doces.
  ANÚNCIO SEM PREÇO (torresmo, Domingão do Gás, novidade): preco null + "selo" (texto da etiqueta amarela,
        ex. "Sexta do Torresmo") + "caixa" (texto do quadro escuro, ex. "SÓ NO<br><em>DOMINGO!</em>");
        "foto_cheia": true faz a foto real ocupar o quadro branco inteiro.
  tema (opcional: hortifruti, acougue, padaria, natal, blackfriday, pascoa, festajunina, ou
        qualquer texto -> cai no padrão roxo), alcool (bool -> aviso CONAR e sem Britinho)
"""
import os, sys, json, html
from playwright.sync_api import sync_playwright

D = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(D, "assets")

FONTS = """
@font-face{font-family:"Disp";src:url("file:///usr/share/fonts/opentype/inter/InterDisplay-Black.otf");font-weight:900}
@font-face{font-family:"Disp";src:url("file:///usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf");font-weight:800}
@font-face{font-family:"Pop";src:url("file:///usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf");font-weight:500}
@font-face{font-family:"Pop";src:url("file:///usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf");font-weight:700}
"""

# Fundos temáticos para ofertas ligadas a eventos (o resto do layout não muda)
TEMAS = {
    "padrao": dict(bg="radial-gradient(70% 45% at 15% 8%, rgba(123,63,176,.95), transparent 70%),radial-gradient(60% 40% at 90% 95%, rgba(225,37,27,.35), transparent 70%),linear-gradient(180deg,#53228A 0%, #4B1E78 45%, #3A1563 100%)",
                   box="#2C0D4D", titulo="#fff", pill="#FFD400", pilltxt="#4B1E78", sombra="#E1251B", deco=""),
    "hortifruti": dict(bg="radial-gradient(70% 45% at 15% 8%, rgba(120,200,80,.9), transparent 70%),radial-gradient(60% 40% at 90% 95%, rgba(255,212,0,.35), transparent 70%),linear-gradient(180deg,#2E8B3A 0%, #1F6E2E 50%, #155423 100%)",
                       box="#0F3D19", titulo="#fff", pill="#FFD400", pilltxt="#1F6E2E", sombra="#E1251B", deco="folhas"),
    "acougue": dict(bg="radial-gradient(70% 45% at 15% 8%, rgba(255,90,70,.85), transparent 70%),linear-gradient(180deg,#B3140D 0%, #8E0F0A 55%, #5E0906 100%)",
                    box="#3E0604", titulo="#fff", pill="#FFD400", pilltxt="#8E0F0A", sombra="#2C0D4D", deco=""),
    "padaria": dict(bg="radial-gradient(70% 45% at 15% 8%, rgba(255,200,120,.9), transparent 70%),linear-gradient(180deg,#C67A2B 0%, #A35E1C 55%, #7A4312 100%)",
                    box="#4A2708", titulo="#fff", pill="#FFF4D6", pilltxt="#7A4312", sombra="#4B1E78", deco=""),
    "natal": dict(bg="radial-gradient(70% 45% at 15% 8%, rgba(255,80,70,.8), transparent 70%),linear-gradient(180deg,#C8102E 0%, #9E0C24 55%, #0E5C34 100%)",
                  box="#0E3F25", titulo="#fff", pill="#FFD400", pilltxt="#9E0C24", sombra="#0E5C34", deco="neve"),
    "blackfriday": dict(bg="radial-gradient(60% 40% at 15% 8%, rgba(255,212,0,.25), transparent 70%),linear-gradient(180deg,#151018 0%, #0B080D 100%)",
                        box="#2C0D4D", titulo="#FFD400", pill="#E1251B", pilltxt="#fff", sombra="#FFD400", deco=""),
    "pascoa": dict(bg="radial-gradient(70% 45% at 15% 8%, rgba(190,150,230,.9), transparent 70%),linear-gradient(180deg,#7B4A2A 0%, #5C341C 60%, #3F2312 100%)",
                   box="#2C1709", titulo="#fff", pill="#F3D9FF", pilltxt="#5C341C", sombra="#4B1E78", deco=""),
    "granja": dict(bg="radial-gradient(70% 45% at 15% 8%, rgba(255,214,90,.95), transparent 70%),linear-gradient(180deg,#F2A516 0%, #D9800B 55%, #A85A06 100%)",
                   box="#5A2E02", titulo="#fff", pill="#fff", pilltxt="#A85A06", sombra="#E1251B", deco=""),
    "bebidas": dict(bg="radial-gradient(70% 45% at 15% 8%, rgba(90,190,255,.85), transparent 70%),linear-gradient(180deg,#1666C5 0%, #0F4A99 55%, #0A3270 100%)",
                    box="#061E45", titulo="#fff", pill="#FFD400", pilltxt="#0F4A99", sombra="#E1251B", deco="bolhas"),
    "limpeza": dict(bg="radial-gradient(70% 45% at 15% 8%, rgba(120,240,230,.85), transparent 70%),linear-gradient(180deg,#14A3A0 0%, #0E7F86 55%, #0A5A63 100%)",
                    box="#063A40", titulo="#fff", pill="#FFD400", pilltxt="#0E7F86", sombra="#4B1E78", deco="bolhas"),
    "laticinios": dict(bg="radial-gradient(70% 45% at 15% 8%, rgba(200,230,255,.95), transparent 70%),linear-gradient(180deg,#5BA4E6 0%, #3A82C9 55%, #275F9A 100%)",
                       box="#12345A", titulo="#fff", pill="#FFD400", pilltxt="#275F9A", sombra="#E1251B", deco=""),
    "doces": dict(bg="radial-gradient(70% 45% at 15% 8%, rgba(255,170,210,.9), transparent 70%),linear-gradient(180deg,#E0457B 0%, #B92D62 55%, #861B46 100%)",
                  box="#4A0B24", titulo="#fff", pill="#FFD400", pilltxt="#B92D62", sombra="#4B1E78", deco=""),
    "festajunina": dict(bg="radial-gradient(70% 45% at 15% 8%, rgba(255,160,40,.85), transparent 70%),linear-gradient(180deg,#D9531E 0%, #B23A14 55%, #7F250B 100%)",
                        box="#4B1E78", titulo="#fff", pill="#FFD400", pilltxt="#B23A14", sombra="#4B1E78", deco="bandeirinhas"),
}

def tema_de(o):
    t = (o.get("tema") or o.get("evento") or "").lower()
    for k in TEMAS:
        if k != "padrao" and k.replace("festajunina", "junina") in t.replace(" ", "").replace("-", "").replace("ú", "u").replace("ç", "c").replace("á", "a"):
            return k
    if "hortifr" in t or "feira" in t or "verdura" in t or "fruta" in t: return "hortifruti"
    if "carne" in t or "churras" in t or "acoug" in t or "açoug" in t: return "acougue"
    if "pão" in t or "pao" in t or "padar" in t: return "padaria"
    if "black" in t: return "blackfriday"
    if "natal" in t or "ceia" in t: return "natal"
    if "páscoa" in t or "pascoa" in t: return "pascoa"
    if "junina" in t or "julina" in t: return "festajunina"
    return "padrao"

# tema pelo PRODUTO quando a oferta não tem evento (toda oferta ganha fundo do seu tema)
CATEGORIAS = [
    ("granja", ["ovo", "ovos", "frango", "galinha"]),
    ("acougue", ["carne", "picanha", "alcatra", "costela", "linguiça", "linguica", "bife", "acém", "acem", "coxão", "coxao", "patinho", "músculo", "musculo", "suína", "suina", "bisteca"]),
    ("hortifruti", ["banana", "tomate", "batata", "cebola", "alface", "laranja", "maçã", "maca", "fruta", "verdura", "legume", "mamão", "mamao", "melancia", "limão", "limao", "cenoura"]),
    ("padaria", ["pão", "pao", "bolo", "torrada", "biscoito", "bolacha", "rosca"]),
    ("laticinios", ["leite", "queijo", "iogurte", "manteiga", "requeijão", "requeijao", "presunto", "mussarela", "muçarela", "danone"]),
    ("bebidas", ["refrigerante", "coca", "suco", "água", "agua", "guaraná", "guarana", "cerveja", "energético", "energetico"]),
    ("limpeza", ["detergente", "sabão", "sabao", "amaciante", "desinfetante", "água sanitária", "esponja", "limpador", "papel higiênico", "papel higienico"]),
    ("doces", ["chocolate", "bombom", "doce", "sorvete", "picolé", "picole", "bala", "cacau"]),
]

def tema_final(o):
    t = tema_de(o)
    if t != "padrao" or o.get("tema") == "padrao":
        return t
    nome = (o.get("nome") or "").lower()
    for k, palavras in CATEGORIAS:
        if any(w in nome for w in palavras):
            return k
    return "padrao"

def css(T, H):
    deco = ""
    if T["deco"] == "folhas":
        deco = ".deco{position:absolute;inset:0;opacity:.13;background-image:radial-gradient(ellipse 22px 10px at 50% 50%,#fff 98%,transparent 100%);background-size:90px 70px;transform:rotate(-25deg) scale(1.4)}"
    elif T["deco"] == "neve":
        deco = ".deco{position:absolute;inset:0;opacity:.22;background-image:radial-gradient(#fff 2px,transparent 2.5px),radial-gradient(#fff 1.3px,transparent 1.8px);background-size:70px 70px,37px 37px;background-position:0 0,18px 22px}"
    elif T["deco"] == "bolhas":
        deco = ".deco{position:absolute;inset:0;opacity:.16;background-image:radial-gradient(circle at 50% 50%,transparent 9px,#fff 10px,#fff 12px,transparent 13px),radial-gradient(#fff 3px,transparent 3.5px);background-size:110px 130px,60px 70px;background-position:0 0,30px 40px}"
    elif T["deco"] == "bandeirinhas":
        deco = ".deco{position:absolute;left:0;right:0;top:0;height:60px;background:repeating-linear-gradient(90deg,#FFD400 0 40px,#2E8B3A 40px 80px,#4B1E78 80px 120px,#fff 120px 160px);clip-path:polygon(0 0,100% 0,100% 40%,0 40%);opacity:.9}"
    return FONTS + f"""
:root{{--roxo:#4B1E78;--verm:#E1251B;--amar:#FFD400}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1080px;height:{H}px;overflow:hidden}}
body{{font-family:"Pop",sans-serif;color:#fff;position:relative;background:{T['bg']}}}
.grain{{position:absolute;inset:0;opacity:.18;background-image:radial-gradient(rgba(255,255,255,.55) 1px,transparent 1.3px);background-size:8px 8px}}
{deco}
.cv{{position:absolute;left:0;top:{(H-1440)//2}px;width:1080px;height:1440px}}
.title{{position:absolute;left:64px;top:70px}}
.title .l1{{font-family:"Disp";font-weight:900;font-size:148px;line-height:.9;letter-spacing:-.03em;color:{T['titulo']}}}
.title .l2{{display:inline-block;margin-top:14px;font-family:"Disp";font-weight:900;font-size:80px;line-height:1;letter-spacing:-.02em;color:{T['pilltxt']};
  background:{T['pill']};padding:4px 26px 12px;border-radius:26px;transform:rotate(-2.5deg);box-shadow:0 10px 0 {T['sombra']}}}
.box{{position:absolute;right:64px;top:70px;width:330px;background:{T['box']};border-radius:36px;padding:30px 26px 30px;text-align:center;box-shadow:0 16px 40px rgba(0,0,0,.25)}}
.box .big{{font-family:"Disp";font-weight:900;font-size:52px;line-height:.95;color:#fff}}
.box .big em{{font-style:normal;color:var(--amar)}}
.box .small{{margin-top:12px;font-weight:500;font-size:22px;line-height:1.25;color:#E9DDF7}}
.box .ev{{margin-top:14px;display:inline-block;background:var(--amar);color:#22152F;font-weight:700;font-size:20px;border-radius:999px;padding:6px 16px}}
.card{{position:absolute;left:64px;right:390px;top:385px;height:720px;background:#fff;border-radius:52px;box-shadow:0 30px 60px rgba(20,5,40,.35)}}
.card.full{{right:64px}}
.card .nome{{position:absolute;left:40px;right:40px;top:44px;text-align:center;font-weight:700;font-size:36px;line-height:1.15;letter-spacing:.02em;color:var(--roxo);text-transform:uppercase;text-wrap:balance}}
.card .prod{{position:absolute;left:50%;top:200px;transform:translateX(-50%) rotate(-5deg);width:570px;height:350px;display:grid;place-items:center}}
.card .prod img{{max-width:100%;max-height:100%;filter:drop-shadow(0 26px 24px rgba(40,10,70,.28))}}
.cond{{position:absolute;left:40px;bottom:36px;background:var(--verm);color:#fff;font-weight:700;font-size:26px;border-radius:999px;padding:12px 28px}}
.tag{{z-index:3;position:absolute;left:40px;top:1010px;background:var(--amar);border-radius:36px;padding:8px 34px 18px 30px;display:flex;align-items:flex-start;gap:8px;color:var(--roxo);
  box-shadow:0 14px 0 var(--verm),0 30px 40px rgba(0,0,0,.3);transform:rotate(-3deg)}}
.tag .rs{{font-family:"Disp";font-weight:900;font-size:50px;margin-top:58px;color:var(--verm)}}
.tag .int{{font-family:"Disp";font-weight:900;font-size:230px;line-height:.92;letter-spacing:-.05em}}
.tag .dec{{display:flex;flex-direction:column;align-items:flex-start;margin-top:30px}}
.tag .cent{{font-family:"Disp";font-weight:900;font-size:104px;line-height:.9;letter-spacing:-.03em}}
.tag .un{{font-family:"Pop";font-weight:700;font-size:30px;margin-top:10px;margin-left:8px;color:var(--verm)}}
.card img.cheia{{position:absolute;inset:18px;width:calc(100% - 36px);height:calc(100% - 36px);object-fit:cover;border-radius:38px}}
.tag.selo{{font-family:"Disp";font-weight:900;font-size:76px;line-height:1;padding:22px 40px 28px;max-width:620px}}
.brit{{position:absolute;right:0;bottom:60px;height:790px;z-index:1;filter:drop-shadow(-10px 20px 30px rgba(20,5,40,.35))}}
.foot{{z-index:2;position:absolute;left:64px;right:64px;bottom:44px;height:92px;background:#fff;border-radius:999px;display:flex;align-items:center;gap:22px;padding:0 34px 0 26px;color:var(--roxo)}}
.foot img{{height:50px}}
.foot .end{{font-weight:700;font-size:22px;line-height:1.25;white-space:nowrap}}
.foot .end span{{display:block;font-weight:500;color:#5b4a6e;font-size:19px}}
.foot .zap{{margin-left:auto;background:var(--roxo);color:#fff;border-radius:999px;padding:12px 22px;font-weight:700;font-size:21px;white-space:nowrap;line-height:1.1;text-align:center}}
/* layout B (espelhado): card à direita, Britinho espiando da borda ESQUERDA, título à direita */
.lb .title{{left:auto;right:64px;text-align:right}}
.lb .box{{right:auto;left:64px}}
.lb .card{{left:390px;right:64px}}
.lb .card.full{{left:64px}}
.lb .brit{{right:auto;left:0;filter:drop-shadow(10px 20px 30px rgba(20,5,40,.35))}}
.lb .tag{{left:auto;right:40px;transform:rotate(3deg)}}
.lb .title .l2{{transform:rotate(2.5deg)}}
.legal{{position:absolute;left:64px;right:64px;bottom:10px;text-align:center;font-size:15px;color:rgba(255,255,255,.75)}}
.legal.alc{{font-weight:700;font-size:17px;color:#fff;letter-spacing:.02em}}
"""

def preco(v):
    return f"{float(v):.2f}".replace(".", ",").split(",")

def doc(o, H):
    T = TEMAS[tema_final(o)]
    sem_preco = o.get("preco") in (None, "", 0)
    rs, cent = ("", "") if sem_preco else preco(o["preco"])
    meses = ["janeiro","fevereiro","março","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"]
    if o.get("caixa"):
        box = f'<div class="big">{o["caixa"]}</div>' + (f'<div class="small">{html.escape(o["caixa_apoio"])}</div>' if o.get("caixa_apoio") else "")
    elif o.get("fim"):
        i, f = o["inicio"].split("-"), o["fim"].split("-")
        box = f'<div class="big">{int(i[2])} A {int(f[2])}<br><em>DE {meses[int(f[1])-1].upper()}</em></div><div class="small">ou enquanto durarem os estoques</div>'
    else:
        box = '<div class="big">ESTOQUE<br><em>LIMITADO!</em></div><div class="small">Válido enquanto durarem os estoques</div>'
    if o.get("evento"):
        box += f'<div class="ev">{html.escape(o["evento"])}</div>'
    c = o.get("cond", "") or ""
    cond = "" if (c.lower().startswith("estoque limitado") and not o.get("fim")) or not c else f'<div class="cond">{html.escape(c)}</div>'
    alcool = bool(o.get("alcool"))
    brit = "" if alcool or not o.get("britinho") else f'<img class="brit" src="file://{o["britinho"]}">'
    card_cls = "card full" if not brit else "card"
    logo = o.get("logo") or os.path.join(A, "logo.png")
    t2 = o.get("titulo2") or ("imperdível" if o.get("destaque") else "do Quase Tudo")
    legal = ('<div class="legal alc">BEBA COM MODERAÇÃO · VENDA E CONSUMO PROIBIDOS PARA MENORES DE 18 ANOS</div>' if alcool
             else '<div class="legal">Imagens meramente ilustrativas.</div>')
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{css(T, H)}{o.get("css","")}</style></head><body>
<div class="grain"></div><div class="deco"></div><div class="cv{' lb' if o.get('layout') == 'b' else ''}">
<div class="title"><div class="l1">{html.escape(o.get('titulo1','Oferta'))}</div><div class="l2">{html.escape(t2)}</div></div>
<div class="box">{box}</div>
<div class="{card_cls}">{'<img class="cheia" src="file://'+o['foto']+'">' if o.get('foto_cheia') else '<div class="nome">'+html.escape(o['nome'])+'</div><div class="prod"><img src="file://'+o['foto']+'"></div>'}{cond}</div>
{brit}
{('<div class="tag selo">'+html.escape(o.get('selo',''))+'</div>') if sem_preco else ('<div class="tag"><span class="rs">R$</span><span class="int">'+rs+'</span><span class="dec"><span class="cent">,'+cent+'</span><span class="un">'+html.escape(o.get('unidade','unid'))+'</span></span></div>')}
<div class="foot"><img src="file://{logo}"><div class="end">Av. João Farah, 649 · Ibitinga<span>Alto dos Pinheiros</span></div><div class="zap"><span style="font-weight:500;font-size:16px;display:block;opacity:.85">WhatsApp</span>(16) 3341-7427</div></div>
{legal}
</div></body></html>"""

def build(o, base):
    outs = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for nome, H in (("feed", 1440), ("story", 1920)):
            f = f"{base}_{nome}.html"; open(f, "w").write(doc(o, H))
            pg = b.new_page(viewport={"width": 1080, "height": H})
            pg.goto("file://" + os.path.abspath(f)); pg.wait_for_timeout(500)
            out = f"{base}_{nome}.png"; pg.screenshot(path=out); outs.append(out); pg.close()
        b.close()
    return outs

if __name__ == "__main__":
    print(build(json.load(open(sys.argv[1])), sys.argv[2]))
