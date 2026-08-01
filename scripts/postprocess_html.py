#!/usr/bin/env python3
"""
Corrige artefatos que o pandoc deixa no HTML gerado a partir do LaTeX da
revista. Rodar depois do `pandoc ... -o artigo.html`, antes de adicionar o
front matter (ver docs/nova-edicao.md).

Uso:
    python3 postprocess_html.py artigo1.html artigo2.html ...

Artefatos corrigidos:
1. \\begin{thebibliography}{99} vira, no HTML, um parágrafo solto só com
   "99" (ou "1", o argumento de largura do rótulo) logo no início da
   div.thebibliography. É lixo, sempre removido.
2. \\begin{wrapfigure}{L}{1.7cm} (usado nas mini-bios no fim de cada
   artigo) vira <p><span>L</span><span>1.7cm</span> <img .../></p> — os
   argumentos de posição/largura viram texto visível por engano. Aqui
   ficam só a imagem.
"""
import re
import sys


def fix(html):
    html = re.sub(
        r'(<div class="thebibliography">)\s*<p><span>\d+</span></p>\s*',
        r"\1\n",
        html,
    )
    html = re.sub(
        r"<p><span>[A-Za-z]</span><span>[^<]*</span>\s*(<img[^>]*/?>)</p>",
        r"<p>\1</p>",
        html,
    )
    return html


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as f:
            html = f.read()
        new_html = fix(html)
        if new_html != html:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_html)
            print(f"corrigido: {path}")
        else:
            print(f"sem mudanças: {path}")
