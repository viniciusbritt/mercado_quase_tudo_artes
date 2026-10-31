# Artes do Quase Tudo Supermercado

Artes e kit do Instagram @mercadoquasetudo (mascote Britinho). O Buffer puxa as imagens daqui pelo link direto:

```
https://raw.githubusercontent.com/viniciusbritt/mercado_quase_tudo_artes/main/artes/AAAA-MM-DD/<arquivo>.jpg
```

## Pastas

- `artes/AAAA-MM-DD/` — artes finais de cada dia de post (feed 1080x1440, story 1080x1920, slides de carrossel, Reels em mp4).
- `kit/` — scripts que montam as artes (`build_oferta.py`, `build_combo.py`, `build_carrossel.py`, `build_interacao.py`, `montar_reels.py`) e os recursos que eles usam.
- `kit/assets/` — logo, endcard, fachada real e as poses do Britinho recortadas (PNG com fundo transparente).
- `kit/assets/produtos/` — fotos de produto recortadas.
- `kit/musicas/` — músicas livres de direitos (Mixkit) e `LICENCAS.txt`.
- `kit/modelos/` — layouts prontos que não são do build_oferta (Domingão do Gás com preço, Britinho na moto). Uso: `python3 kit/modelos/build_gas.py pasta_saida`.
- `kit/fonts/` — Inter Display, Poppins e Lora (licença OFL). Se faltar fonte: `sh kit/fonts/instalar_fontes.sh`.
- `kit/chroma.py` — recorta imagem do Flow em fundo verde: `python3 kit/chroma.py entrada.jpg saida.png`.

## Regras

- Postagens só no canal **mercadoquasetudo** do Buffer. Nunca no canal da Liga BRT.
- Nomes de arquivo únicos: `AAAA-MM-DD_assunto_feed.jpg`, `..._story.jpg`, `..._slide01.jpg`, `..._reels.mp4`.
- Nunca apague ou renomeie uma arte que já está agendada: o Buffer busca o arquivo pelo link na hora de publicar.
