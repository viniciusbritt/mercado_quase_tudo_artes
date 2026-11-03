import sys, subprocess, os
from playwright.sync_api import sync_playwright
D=os.path.dirname(os.path.abspath(__file__)); K="/home/claude/mercado_quase_tudo_artes/kit/assets"
h=open(D+'/anim.html').read().replace('LOGO','file://'+K+'/logo.png').replace('M1','file://'+D+'/m1_cut.png').replace('B2','file://'+D+'/b2_cut.png').replace('V0','file://'+D+'/vinho_cut.png')
open(D+'/_a.html','w').write(h)
mode=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920})
    pg.goto('file://'+D+'/_a.html'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(500)
    if mode=='amostra':
        ts=[float(x) for x in sys.argv[2].split(',')]
        for i,t in enumerate(ts):
            pg.evaluate(f'render({t},false)'); pg.screenshot(path=f'{D}/am_{i}.jpg',type='jpeg',quality=80)
        pg.evaluate('render(0,true)'); pg.screenshot(path=f'{D}/capa.jpg',type='jpeg',quality=92)
    else:
        dur=float(sys.argv[2]); fps=30; n=int(dur*fps)
        ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-framerate',str(fps),'-c:v','mjpeg','-i','-','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p',D+'/video_mudo.mp4'],stdin=subprocess.PIPE)
        for i in range(n):
            pg.evaluate(f'render({i/fps},false)'); ff.stdin.write(pg.screenshot(type='jpeg',quality=90))
        ff.stdin.close(); ff.wait()
    b.close()
