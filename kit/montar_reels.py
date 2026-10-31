"""Edição automática dos Reels do Britinho (cenas do Google Flow -> Reels pronto).

1) Analisar:  python montar_reels.py analisar plano.json
   plano.json = {"cenas": ["cena1.mp4", ...], "endcard": "endcard.mp4"(opcional),
                 "musica": "musica.mp3"(opcional), "saida": "reels.mp4"}
   -> escreve plano.json de volta com "cortes" sugeridos por cena e gera <cena>_folha.jpg
      (folha de contato com o tempo de cada quadro) para revisar os cortes olhando.
      Cada cena ganha: {"arquivo", "ini", "fim", "remover": [[a,b], ...]}
2) Revisar o plano (ajustar ini/fim/remover à mão se a folha mostrar algo sem sentido).
3) Montar:    python montar_reels.py montar plano.json
   -> corta, junta, normaliza 1080x1920 30fps, música de fundo baixinha que abaixa sozinha
      quando o Britinho fala (ducking), fade no fim, loudness -14 LUFS.

Regras do corte automático (o que um editor humano faria):
 - fim da cena: corta o rabo depois da última fala/ação (Flow costuma deixar 0,3-1,5 s sem sentido)
 - início: corta tempo parado sem som antes da ação (deixa 0,15 s de respiro)
 - meio: trecho parado e sem fala > 0,7 s vira 0,25 s
"""
import sys, json, os, subprocess, numpy as np

FPS_A = 25  # janelas de análise por segundo

def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)

def dur(f):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                         capture_output=True, text=True).stdout.strip()
    return float(out)

def audio_env(f):
    """energia de voz (300-3400 Hz) por janela de 40 ms"""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-vn", "-ac", "1", "-ar", "16000",
                          "-af", "highpass=f=300,lowpass=f=3400", "-f", "s16le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    w = 16000 // FPS_A
    n = len(a) // w
    if n == 0:
        return np.zeros(1)
    e = np.sqrt((a[: n * w].reshape(n, w) ** 2).mean(1) + 1e-12)
    return 20 * np.log10(e + 1e-9)

def motion(f):
    """movimento por janela: diferença média entre quadros (vídeo reduzido 64x114 cinza)"""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-vf", f"fps={FPS_A},scale=64:114,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    v = np.frombuffer(raw, np.uint8).reshape(-1, 114, 64).astype(np.float32)
    d = np.abs(np.diff(v, axis=0)).mean((1, 2))
    return np.concatenate([[d[0] if len(d) else 0], d])

def smooth(x, k=5):
    return np.convolve(x, np.ones(k) / k, mode="same") if len(x) > k else x

def analisar_cena(f):
    D = dur(f)
    ae, mo = audio_env(f), motion(f)
    n = min(len(ae), len(mo))
    ae, mo = smooth(ae[:n], 3), smooth(mo[:n], 5)
    voz_lim = max(np.percentile(ae, 60) - 4, -38)          # janela "com som relevante"
    mov_lim = max(np.percentile(mo, 35), 0.6)              # janela "com ação"
    ativo = (ae > voz_lim) | (mo > mov_lim * 1.6)
    t = np.arange(n) / FPS_A
    idx = np.nonzero(ativo)[0]
    if len(idx) == 0:
        return {"arquivo": f, "ini": 0, "fim": round(D, 2), "remover": []}
    # ignora o "pulo" que o Flow costuma deixar nos últimos ~0,35 s
    util = int(max(0, D - 0.35) * FPS_A)
    voz_forte = max(voz_lim, -30)
    voz = np.nonzero(ae[:util] > voz_forte)[0]
    if len(voz):
        k = voz[-1] + 1
        # estende enquanto a ação continua logo depois da fala (até 0,8 s)
        while k < util and mo[k] > mov_lim * 1.6 and (k - voz[-1]) < 0.8 * FPS_A:
            k += 1
        fim = t[min(k, n - 1)] + 0.3
    else:
        act = idx[idx < util]
        fim = (t[act[-1]] + 0.2) if len(act) else D
    fim = float(min(fim, D - 0.12))
    ini = max(0.0, t[idx[0]] - 0.15)
    if ini < 0.3:
        ini = 0.0
    remover, i = [], 0
    parado = ~ativo
    while i < n:
        if parado[i] and ini < t[i] < fim:
            j = i
            while j < n and parado[j]:
                j += 1
            if (j - i) / FPS_A > 0.7 and t[j - 1] < fim - 0.3:
                a, b = t[i] + 0.12, t[j - 1] - 0.12
                if b - a > 0.3:
                    remover.append([round(a, 2), round(b, 2)])
            i = j
        else:
            i += 1
    return {"arquivo": f, "ini": round(float(ini), 2), "fim": round(float(fim), 2), "remover": remover,
            "duracao_original": round(D, 2)}

def folha(f, out, n=10):
    from PIL import Image, ImageDraw
    D = dur(f); ims = []
    for k in range(n):
        tt = D * (k + 0.5) / n
        p = f"{out}.{k}.jpg"
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{tt:.2f}", "-i", f, "-frames:v", "1", "-vf", "scale=180:-1", p])
        im = Image.open(p).convert("RGB"); ImageDraw.Draw(im).text((6, 6), f"{tt:.1f}s", fill=(255, 255, 0)); ims.append(im); os.remove(p)
    W = sum(i.width for i in ims); c = Image.new("RGB", (W, ims[0].height)); x = 0
    for i in ims: c.paste(i, (x, 0)); x += i.width
    c.save(out, quality=80)

def analisar(plano_path):
    P = json.load(open(plano_path))
    P["cortes"] = []
    for f in P["cenas"]:
        c = analisar_cena(f); P["cortes"].append(c)
        folha(f, os.path.splitext(f)[0] + "_folha.jpg")
        print(json.dumps(c, ensure_ascii=False))
    json.dump(P, open(plano_path, "w"), indent=1, ensure_ascii=False)

def trechos(c):
    segs, a = [], c["ini"]
    for r0, r1 in sorted(c.get("remover", [])):
        if r0 > a:
            segs.append((a, r0))
        a = max(a, r1)
    if c["fim"] > a:
        segs.append((a, c["fim"]))
    return segs

def montar(plano_path):
    P = json.load(open(plano_path))
    tmp = os.path.splitext(P["saida"])[0] + "_tmp"; os.makedirs(tmp, exist_ok=True)
    partes = []
    V = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps=30,setsar=1,format=yuv420p"
    for ci, c in enumerate(P["cortes"]):
        for si, (a, b) in enumerate(trechos(c)):
            o = f"{tmp}/p{ci:02d}_{si:02d}.mp4"
            fa = min(0.04, (b - a) / 4)
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", c["arquivo"], "-vf", V,
                 "-af", f"aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d={fa},afade=t=out:st={b-a-fa:.3f}:d={fa}",
                 "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", o])
            partes.append(o)
    if P.get("endcard"):
        o = f"{tmp}/zz_end.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-i", P["endcard"], "-vf", V, "-af", "aresample=48000,aformat=channel_layouts=stereo",
             "-c:v", "libx264", "-crf", "17", "-c:a", "aac", "-b:a", "192k", o])
        partes.append(o)
    lista = f"{tmp}/lista.txt"
    open(lista, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in partes))
    base = f"{tmp}/base.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", base])
    T = dur(base)
    if P.get("musica"):
        ini_m = float(P.get("musica_inicio", 0))
        vol = float(P.get("musica_volume", 0.22))
        fc = (f"[1:a]atrim=start={ini_m},asetpts=PTS-STARTPTS,aloop=loop=-1:size=2e9,atrim=duration={T:.3f},"
              f"volume={vol},afade=t=in:d=0.6,afade=t=out:st={max(T-1.6,0):.3f}:d=1.5,aformat=channel_layouts=stereo[m];"
              "[0:a]asplit=2[v1][v2];[m][v1]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[md];"
              "[v2][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    else:
        fc = "[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[a]"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", base]
    if P.get("musica"):
        cmd += ["-i", P["musica"]]
    cmd += ["-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-ar", "48000", "-movflags", "+faststart", P["saida"]]
    run(cmd)
    print(f"ok {P['saida']} {dur(P['saida']):.1f}s")

if __name__ == "__main__":
    {"analisar": analisar, "montar": montar}[sys.argv[1]](sys.argv[2])
