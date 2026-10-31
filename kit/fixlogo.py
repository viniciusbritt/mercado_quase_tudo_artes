"""Troca a logo inventada pela IA na camisa do Britinho pela logo real.
Uso: python fixlogo.py entrada.mp4 saida.mp4 [debug_dir] [--apagar]
--apagar: só remove a logo (camisa lisa), sem colar a logo real.
Detecta, quadro a quadro, as letras azuis/vermelhas dentro da área roxa da camisa,
apaga (inpaint) e cola a logo real (logo_patch.png) com a mesma posição/ângulo."""
import sys, os, cv2, numpy as np, subprocess

D = os.path.dirname(os.path.abspath(__file__))
PATCH = cv2.imread(os.path.join(D, "assets", "logo_patch.png"), cv2.IMREAD_UNCHANGED)  # BGRA
PH, PW = PATCH.shape[:2]


def masks(fr):
    hsv = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    purple = ((h >= 125) & (h <= 160) & (s >= 60) & (v >= 50)).astype(np.uint8)
    blue = ((h >= 96) & (h <= 126) & (s >= 25) & (v >= 60)).astype(np.uint8)
    red = (((h <= 18) | (h >= 168)) & (s >= 70) & (v >= 110)).astype(np.uint8)
    white = ((s <= 60) & (v >= 190)).astype(np.uint8)
    return purple, blue, red, white


def detect(fr, prev):
    purple, blue, red, white = masks(fr)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))
    shirt = cv2.morphologyEx(purple, cv2.MORPH_CLOSE, k)
    shirt = cv2.erode(shirt, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)))
    cand = ((blue | red) & shirt).astype(np.uint8)
    if prev is not None:
        (cx, cy), (w, hh), _ = prev
        r = max(w, hh) * 1.3 + 30
        win = np.zeros_like(cand)
        cv2.rectangle(win, (int(cx - r), int(cy - r)), (int(cx + r), int(cy + r)), 1, -1)
        cand &= win
    if cand.sum() < 25:
        return None, None
    m = cv2.dilate(cand, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    best = None
    for i in range(1, n):
        x, y, w, hh, a = st[i]
        if a < 120 or w < 18:
            continue
        ar = w / max(hh, 1)
        # precisa ter azul E vermelho (duas linhas da logo)
        comp = lab == i
        nb, nr = (blue.astype(bool) & comp).sum(), (red.astype(bool) & comp).sum()
        if nb < 8 or nr < 5:
            continue
        score = a - (abs(cen[i][0] - prev[0][0]) + abs(cen[i][1] - prev[0][1])) * 3 if prev is not None else a
        if best is None or score > best[0]:
            best = (score, i)
    if best is None:
        return None, None
    comp = (lab == best[1]).astype(np.uint8)
    pts = cv2.findNonZero(comp & ((blue | red)).astype(np.uint8))
    rect = cv2.minAreaRect(pts)
    # região a apagar: componente dilatado + contorno branco perto
    er = cv2.dilate(comp, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    er = er | (cv2.dilate(er, np.ones((7, 7), np.uint8)) & white)
    er = cv2.dilate(er, np.ones((5, 5), np.uint8))
    return rect, er


def norm(rect):
    (cx, cy), (w, h), a = rect
    if w < h:
        w, h, a = h, w, a + 90
    while a > 45:
        a -= 180
    while a < -45:
        a += 180
    return (cx, cy), (w, h), a


def paste(fr, rect):
    (cx, cy), (w, h), a = rect
    a = max(-25, min(25, a))
    tw = w * 1.3
    s = tw / PW
    M = cv2.getRotationMatrix2D((PW / 2, PH / 2), -a, s)
    M[0, 2] += cx - PW / 2
    M[1, 2] += cy - PH / 2
    H, W = fr.shape[:2]
    p = cv2.warpAffine(PATCH, M, (W, H), flags=cv2.INTER_AREA, borderValue=(0, 0, 0, 0))
    p = cv2.GaussianBlur(p, (0, 0), 0.6)
    al = p[..., 3:4].astype(np.float32) / 255 * 0.97
    # luz local: usa a luminância do fundo (já sem a logo antiga)
    g = cv2.GaussianBlur(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 6)
    ys, xs = np.nonzero(al[..., 0] > 0.3)
    if len(ys):
        ref = np.median(g[ys, xs])
        shade = np.clip(g / max(ref, 1), 0.75, 1.15)[..., None]
    else:
        shade = 1
    col = np.clip(p[..., :3].astype(np.float32) * (0.92 * shade), 0, 255)
    out = fr.astype(np.float32) * (1 - al) + col * al
    return out.astype(np.uint8)


def run(src, dst, dbg=None, so_apagar=False):
    cap = cv2.VideoCapture(src)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    rects, erases = [], []
    prev, miss = None, 0
    for f in frames:
        r, e = detect(f, prev)
        if r is not None:
            r = norm(r)
            if prev is not None:  # suaviza
                (pcx, pcy), (pw, ph), pa = prev
                (cx, cy), (w, h), a = r
                k = 0.55
                r = ((pcx + (cx - pcx) * k, pcy + (cy - pcy) * k), (pw + (w - pw) * 0.35, ph + (h - ph) * 0.35), pa + (a - pa) * 0.4)
            prev, miss = r, 0
        else:
            miss += 1
            if miss > 3:
                prev = None
        rects.append(r)
        erases.append(e)
    # preenche falhas curtas de detecção (evita piscar a logo antiga)
    idx = [i for i, r in enumerate(rects) if r is not None]
    for a_, b_ in zip(idx, idx[1:]):
        if 1 < b_ - a_ <= 8:
            ra, rb = rects[a_], rects[b_]
            for j in range(a_ + 1, b_):
                t = (j - a_) / (b_ - a_)
                r = ((ra[0][0] + (rb[0][0] - ra[0][0]) * t, ra[0][1] + (rb[0][1] - ra[0][1]) * t),
                     (ra[1][0] + (rb[1][0] - ra[1][0]) * t, ra[1][1] + (rb[1][1] - ra[1][1]) * t),
                     ra[2] + (rb[2] - ra[2]) * t)
                (cx, cy), (w, h), an = r
                box = cv2.boxPoints(((cx, cy), (w * 1.25 + 8, h * 1.6 + 8), an)).astype(np.int32)
                e = np.zeros(frames[j].shape[:2], np.uint8)
                cv2.fillPoly(e, [box], 1)
                rects[j], erases[j] = r, e
    out = []
    for i, f in enumerate(frames):
        r, e = rects[i], erases[i]
        if r is None or r[1][0] < 14:
            out.append(f)
            continue
        g = cv2.inpaint(f, e, 6, cv2.INPAINT_TELEA)
        out.append(g if so_apagar else paste(g, r))
    H, W = frames[0].shape[:2]
    tmp = dst + ".noaudio.mp4"
    vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
    for f in out:
        vw.write(f)
    vw.release()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-i", src, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264",
                    "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "copy", dst], check=True)
    os.remove(tmp)
    det = sum(r is not None for r in rects)
    miss = [i for i, r in enumerate(rects) if r is None]
    rg = []
    for k in miss:
        if rg and k == rg[-1][1] + 1:
            rg[-1][1] = k
        else:
            rg.append([k, k])
    print(f"{src}: {len(frames)} quadros, logo trocada em {det}; sem troca: {rg}")
    if dbg:
        os.makedirs(dbg, exist_ok=True)
        for i in range(0, len(frames), max(1, len(frames) // 12)):
            cv2.imwrite(f"{dbg}/{i:03d}.jpg", np.hstack([frames[i], out[i]]))


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if x != "--apagar"]
    run(a[0], a[1], a[2] if len(a) > 2 else None, "--apagar" in sys.argv)
