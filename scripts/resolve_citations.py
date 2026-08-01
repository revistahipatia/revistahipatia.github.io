#!/usr/bin/env python3
"""
Resolve citações LaTeX (\\cite{...} / \\bibitem{...}) para números simples
antes de rodar o pandoc, já que o pandoc não executa o LaTeX e não sabe
numerar bibliografias sozinho.

Cobre os dois casos encontrados no repositório fonte da revista:

1) Bibliografia manual (\\begin{thebibliography} com \\bibitem{chave} escritos
   à mão no próprio artigo, ex.: historia.tex, panorama.tex). Nesse caso a
   numeração vem do .aux gerado ao compilar o artigo sozinho.

     python3 resolve_citations.py manual artigo.tex artigo.aux

2) Bibliografia via bibtex (\\bibliographystyle + \\bibliography{nome}, com
   nome.bib e nome.bbl já compilados, ex.: tecnica.tex). Nesse caso a
   numeração vem do .aux, mas o conteúdo formatado vem do .bbl (o pandoc
   ignora \\bibliography{} silenciosamente).

     python3 resolve_citations.py bibtex artigo.tex artigo.aux artigo.bbl

Em ambos os casos o script edita o .tex OUTPUT_TEX (uma cópia já copiada
para o repositório do site, nunca o .tex original do repositório fonte) e
insere um "\\section{Bibliografia}" antes do bloco, já que o
\\begin{thebibliography} gera esse título sozinho ao compilar em LaTeX de
verdade, mas o pandoc não sabe disso.

ATENÇÃO / ARMADILHAS JÁ CONHECIDAS (ver docs/nova-edicao.md para mais
contexto):
- \\newblock (dos estilos padrão do bibtex) faz o pandoc "engolir" o grupo
  {...} seguinte inteiro, como se \\newblock fosse uma macro desconhecida
  que consome um argumento. Este script já remove todo \\newblock do .bbl
  antes de qualquer outra coisa.
- \\textordfeminine (o "ª" de "5ª edição") é silenciosamente descartado
  pelo pandoc. Este script troca por \\textsuperscript{a}.
- Prefira tentar primeiro `pandoc artigo.tex --bibliography=artigo.bib
  --citeproc` quando existir um .bib de verdade (não apenas .bbl) — pode
  resolver a bibliografia sozinho, sem precisar deste script. Só use este
  script se o --citeproc não der conta (bibliografia manual sem .bib, ou
  formatação que fuja do padrão esperado pelo citeproc).
"""
import re
import sys


def load_bibcite(aux_path):
    """Lê \\bibcite{chave}{numero} do .aux. Cobre tanto o formato padrão
    ({numero}) quanto o do pacote amsrefs ({{numero}{...}})."""
    mapping = {}
    with open(aux_path, encoding="utf-8", errors="replace") as f:
        content = f.read()
    for m in re.finditer(r"\\bibcite\{([^}]+)\}\{\{?(\d+)", content):
        mapping[m.group(1)] = m.group(2)
    return mapping


def replace_cites(text, mapping):
    def cite_repl(m):
        keys = [k.strip() for k in m.group(1).split(",")]
        nums = [mapping.get(k, "??") for k in keys]
        return "[" + ",".join(nums) + "]"

    return re.sub(r"\\cite\{([^}]+)\}", cite_repl, text)


def replace_bibitems(text, mapping):
    def bibitem_repl(m):
        return f"[{mapping.get(m.group(1), '??')}]"

    return re.sub(r"\\bibitem\{([^}]+)\}", bibitem_repl, text)


def fix_bbl_quirks(bbl_text):
    bbl_text = bbl_text.replace("\\newblock ", "").replace("\\newblock", "")
    bbl_text = bbl_text.replace("\\textordfeminine", "\\textsuperscript{a}")
    return bbl_text


def warn_missing_keys(text, mapping, label):
    keys_used = set()
    for grp in re.findall(r"\\cite\{([^}]+)\}", text):
        keys_used.update(k.strip() for k in grp.split(","))
    missing = keys_used - set(mapping.keys())
    if missing:
        print(f"AVISO ({label}): chaves de \\cite sem entrada no .aux: {missing}", file=sys.stderr)


def run_manual(tex_path, aux_path):
    mapping = load_bibcite(aux_path)
    with open(tex_path, encoding="utf-8") as f:
        text = f.read()
    warn_missing_keys(text, mapping, tex_path)
    text = replace_cites(text, mapping)
    text = replace_bibitems(text, mapping)
    text, n = re.subn(
        r"\\begin\{thebibliography\}",
        r"\\section{Bibliografia}\n\n\\begin{thebibliography}",
        text,
        count=1,
    )
    if n == 0:
        print("AVISO: não encontrei \\begin{thebibliography} para inserir o heading.", file=sys.stderr)
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"OK: {tex_path} atualizado com {len(mapping)} chaves resolvidas.")


def run_bibtex(tex_path, aux_path, bbl_path):
    mapping = load_bibcite(aux_path)
    with open(bbl_path, encoding="utf-8") as f:
        bbl = f.read()
    bbl = fix_bbl_quirks(bbl)
    bbl_body = replace_bibitems(bbl, mapping)

    with open(tex_path, encoding="utf-8") as f:
        text = f.read()
    warn_missing_keys(text, mapping, tex_path)
    text = replace_cites(text, mapping)

    # Remove o bloco \bibliographystyle{...} ... \bibliography{...} (com
    # possíveis \def\bibfont{...} e \nocite{*} no meio, como no template
    # da revista) e substitui pelo conteúdo já resolvido do .bbl.
    pattern = re.compile(
        r"\\bibliographystyle\{[^}]*\}.*?\\bibliography\{[^}]*\}",
        re.DOTALL,
    )
    replacement = "\\section{Bibliografia}\n\n{\\footnotesize\n" + bbl_body + "\n}"
    text, n = pattern.subn(lambda m: replacement, text, count=1)
    if n == 0:
        print("AVISO: não encontrei o bloco \\bibliographystyle/\\bibliography.", file=sys.stderr)

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"OK: {tex_path} atualizado com {len(mapping)} chaves resolvidas (via .bbl).")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    mode = sys.argv[1]
    if mode == "manual" and len(sys.argv) == 4:
        run_manual(sys.argv[2], sys.argv[3])
    elif mode == "bibtex" and len(sys.argv) == 5:
        run_bibtex(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(__doc__)
        sys.exit(1)
