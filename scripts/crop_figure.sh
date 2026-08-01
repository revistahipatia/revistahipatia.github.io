#!/usr/bin/env bash
# Extrai uma figura (ex.: uma imagem de tikzpicture, que o pandoc não sabe
# renderizar) diretamente do PDF já compilado do artigo, em vez de tentar
# recompilar o tikz sozinho. Ver docs/nova-edicao.md para o processo
# completo de como descobrir as coordenadas (x,y,largura,altura).
#
# Uso:
#   ./crop_figure.sh artigo.pdf PAGINA X Y LARGURA ALTURA saida.png [DPI]
#
# Exemplo (figura na página 8, aproximadamente no canto inferior esquerdo,
# renderizada a 300dpi):
#   ./crop_figure.sh problema.pdf 8 300 2430 800 950 tikz_circulo.png 300
set -euo pipefail

pdf="$1"; page="$2"; x="$3"; y="$4"; w="$5"; h="$6"; out="$7"; dpi="${8:-300}"

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

pdftoppm -png -r "$dpi" -f "$page" -l "$page" "$pdf" "$tmpdir/page"
rendered=$(ls "$tmpdir"/page*.png | head -1)

magick "$rendered" -crop "${w}x${h}+${x}+${y}" +repage \
  -fuzz 3% -trim +repage \
  -bordercolor white -border 25 \
  "$out"

echo "gerado: $out"
identify "$out"
