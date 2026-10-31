#!/bin/sh
# Coloca as fontes nos caminhos que os scripts do kit usam. Rode se faltar alguma fonte.
D="$(cd "$(dirname "$0")" && pwd)"
mkdir -p /usr/share/fonts/opentype/inter /usr/share/fonts/truetype/google-fonts
for f in InterDisplay-Black.otf InterDisplay-ExtraBold.otf; do [ -f /usr/share/fonts/opentype/inter/$f ] || cp "$D/$f" /usr/share/fonts/opentype/inter/; done
for f in Poppins-Regular.ttf Poppins-Medium.ttf Poppins-Bold.ttf Lora-Italic-Variable.ttf; do [ -f /usr/share/fonts/truetype/google-fonts/$f ] || cp "$D/$f" /usr/share/fonts/truetype/google-fonts/; done
fc-cache -f >/dev/null 2>&1; echo "fontes ok"
