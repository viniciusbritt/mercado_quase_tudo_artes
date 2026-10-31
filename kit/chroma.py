import sys,numpy as np,cv2
from PIL import Image
src,dst=sys.argv[1],sys.argv[2]
im=cv2.imread(src); hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
h,s,v=cv2.split(hsv)
g=((h>35)&(h<85)&(s>90)&(v>70)).astype(np.uint8)*255
g=cv2.morphologyEx(g,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
# mantém só o fundo conectado às bordas
n,lab=cv2.connectedComponents(g)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
areas=np.bincount(lab.ravel())
big={i for i in range(1,n) if areas[i]>150}
bg=np.isin(lab,list(border|big)).astype(np.uint8)*255
a=255-bg
a=cv2.erode(a,np.ones((3,3),np.uint8),1)
a=cv2.GaussianBlur(a,(5,5),0)
b,gc,r=cv2.split(im.astype(np.int16))
mx=np.maximum(r,b); gc=np.where(gc>mx,mx,gc)  # despill
out=cv2.merge([b,gc,r]).clip(0,255).astype(np.uint8)
rgba=np.dstack([cv2.cvtColor(out,cv2.COLOR_BGR2RGB),a])
ys,xs=np.nonzero(a>20); rgba=rgba[ys.min():ys.max()+1,xs.min():xs.max()+1]
Image.fromarray(rgba).save(dst); print(dst,rgba.shape)
