"""Recorta o Britinho de um vídeo em fundo verde (Flow) e coloca sobre uma FOTO REAL (fachada/interior).
Uso: python chroma_video.py cena.mp4 foto.jpg saida.mp4 [escala=0.8] [foco_x=0.5] [foco_y=0.3] [blur=3]
- escala: altura do personagem em relação ao quadro 1080x1920 (o vídeo do Flow inteiro é escalado)
- foco_x/foco_y: ponto da foto que fica no centro do recorte (0-1)
- a foto ganha zoom lento (Ken Burns) e um leve desfoque, como profundidade de campo
"""
import sys, subprocess, numpy as np, cv2
src, foto, out = sys.argv[1:4]
esc = float(sys.argv[4]) if len(sys.argv) > 4 else 0.8
fx = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
fy = float(sys.argv[6]) if len(sys.argv) > 6 else 0.3
blur = float(sys.argv[7]) if len(sys.argv) > 7 else 3
W, H = 1080, 1920
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS) or 24; n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
bg0 = cv2.imread(foto)
s = max(W * 1.12 / bg0.shape[1], H * 1.12 / bg0.shape[0])
bg0 = cv2.resize(bg0, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
if blur > 0: bg0 = cv2.GaussianBlur(bg0, (0, 0), blur)
bh, bw = bg0.shape[:2]
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                      "-i", src, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", out], stdin=subprocess.PIPE)
i = 0
while True:
    ok, fr = cap.read()
    if not ok: break
    t = i / max(n - 1, 1)
    z = 1.0 + 0.08 * t                       # zoom lento
    cw, ch = int(W * 1.12 / z * (bw / (W * 1.12))), 0
    cw = int(bw / z); ch = int(bh / z)
    cx = int(np.clip(fx * bw - cw / 2, 0, bw - cw)); cy = int(np.clip(fy * bh - ch / 2 + (H/1.12 - ch) * 0, 0, bh - ch))
    bg = cv2.resize(bg0[cy:cy + ch, cx:cx + cw], (W, H), interpolation=cv2.INTER_LINEAR)
    hsv = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV)
    h, sat, v = cv2.split(hsv)
    g = ((h > 35) & (h < 90) & (sat > 60) & (v > 40)).astype(np.uint8) * 255
    g = cv2.morphologyEx(g, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    a = 255 - g
    a = cv2.erode(a, np.ones((3, 3), np.uint8))
    a = cv2.GaussianBlur(a, (5, 5), 0).astype(np.float32) / 255
    b_, g_, r_ = cv2.split(fr.astype(np.int16)); g_ = np.minimum(g_, np.maximum(r_, b_) + 8)  # despill
    fr2 = cv2.merge([b_, g_, r_]).clip(0, 255).astype(np.uint8)
    ph = int(H * esc); pw = int(fr.shape[1] * ph / fr.shape[0])
    fr2 = cv2.resize(fr2, (pw, ph), interpolation=cv2.INTER_CUBIC); a = cv2.resize(a, (pw, ph))
    x0 = (W - pw) // 2; y0 = H - ph
    roi = bg[y0:y0 + ph, max(x0, 0):max(x0, 0) + min(pw, W)]
    fx0 = max(-x0, 0); fr2 = fr2[:, fx0:fx0 + roi.shape[1]]; a = a[:, fx0:fx0 + roi.shape[1]]
    # sombra suave no chão
    a3 = a[..., None]
    bg[y0:y0 + ph, max(x0, 0):max(x0, 0) + roi.shape[1]] = (fr2 * a3 + roi * (1 - a3)).astype(np.uint8)
    p.stdin.write(bg.tobytes()); i += 1
p.stdin.close(); p.wait(); print("ok", out, i, "quadros")
