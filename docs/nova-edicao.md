# Como publicar uma nova edição

Este documento descreve o processo completo, testado na publicação do
Volume 4, Número 1, para pegar o material de uma edição (que vem de um
repositório LaTeX separado, ex.: `~/code/vol04num01`) e publicá-lo neste
site (Jekyll + GitHub Pages).

Ler também `CLAUDE.md` (na raiz) para um resumo rápido e as convenções
gerais do site (SEO, embedding no iframe da UFBA, identidade visual).

## Visão geral

1. Copiar os artigos (tex, pdf, imagens) do repositório fonte para uma
   pasta nova aqui, uma subpasta por artigo.
2. Pré-processar o `.tex` de cada artigo copiado (nunca o do repositório
   fonte) para resolver problemas que o pandoc sozinho não resolve:
   citações, bibliografia, figuras em TikZ.
3. Rodar o pandoc, artigo por artigo.
4. Corrigir os artefatos que o pandoc sempre deixa no HTML gerado.
5. Adicionar o front matter (YAML) de cada artigo e da edição.
6. Atualizar o índice do site (`index.html` da raiz) e criar um post de
   anúncio.
7. Testar localmente com Jekyll antes de dar push.

## 1. Copiar os arquivos

Para cada artigo da edição (as seções variam a cada edição — olhe as
pastas do repositório fonte, exceto `capa/` e `contracapa/`, que não viram
páginas do site):

```bash
SRC=~/code/volXXnumYY      # repositório fonte (LaTeX)
DST=~/code/revistahipatia.github.io/volXXnumYY

mkdir -p "$DST/<artigo>"
cp "$SRC/<artigo>/<artigo>.tex" "$SRC/<artigo>/<artigo>.pdf" "$DST/<artigo>/"
```

Para as imagens, **não copie a pasta inteira** — copie só o que é
realmente referenciado, para não arrastar rascunhos e figuras não
usadas:

```bash
grep -o 'includegraphics\[[^]]*\]{[^}]*}' "$SRC/<artigo>/<artigo>.tex"
```

Cuidados observados:
- Nomes de arquivo com espaço (ex.: `hipatia pentagono1.png`) devem ser
  renomeados com `_` ao copiar, e a referência correspondente ajustada no
  `.tex` copiado (o pandoc lida mal com espaço em nome de arquivo dentro
  de HTML/URL).
- `\includegraphics` quebrado em duas linhas dentro do argumento opcional
  (`[width=0.65\n\linewidth]`) funciona no pandoc, mas vale limpar para
  ficar numa linha só.

Depois, copie o PDF completo da edição e gere a capa:

```bash
cp ~/code/volXXnumYY/main.pdf "$DST/volXXnumYY.pdf"

pdftoppm -png -f 1 -l 1 -r 150 ~/code/volXXnumYY/capa/capa.pdf /tmp/capa
magick /tmp/capa-1.png -resize 673x963 "$DST/capa.png"
```

## 2. Pré-processar o `.tex` antes do pandoc

O pandoc não executa LaTeX de verdade — ele só faz o parsing da sintaxe.
Isso quebra duas coisas que sempre aparecem nos artigos desta revista:
citações/bibliografia e figuras em TikZ.

### 2.1 Bibliografia

Primeiro tente a via simples, se o artigo tiver um `.bib` de verdade (não
só um `.bbl`):

```bash
pandoc artigo.tex -f latex -t html5 -o artigo.html --mathjax \
  --bibliography=artigo.bib --citeproc
```

Isso já existia no README antigo do projeto (funcionou para pelo menos um
artigo antigo, `teorema.html` do Volume 1 Número 1) e pode poupar todo o
resto desta seção. **Confira o resultado** — se a citeproc não numerar
direito ou a formatação sair estranha, use o caminho manual abaixo.

Caminho manual, para os dois casos encontrados até agora:

**(a) Bibliografia digitada à mão** (`\begin{thebibliography}` com
`\bibitem{chave}` escritos direto no artigo, com `\cite{chave}` no texto
— casos de `historia.tex` e `panorama.tex` do Volume 4). A numeração
certa está no `.aux` gerado quando o autor compilou o artigo sozinho no
repositório fonte:

```bash
python3 scripts/resolve_citations.py manual \
  volXXnumYY/<artigo>/<artigo>.tex \
  ~/code/volXXnumYY/<artigo>/<artigo>.aux
```

**(b) Bibliografia via bibtex** (`\bibliographystyle` + `\bibliography{nome}`,
com `nome.bib` e `nome.bbl` compilados — caso de `tecnica.tex`). O pandoc
ignora `\bibliography{}` silenciosamente, então o conteúdo precisa vir do
`.bbl` já compilado:

```bash
cp ~/code/volXXnumYY/<artigo>/<artigo>.bbl volXXnumYY/<artigo>/
python3 scripts/resolve_citations.py bibtex \
  volXXnumYY/<artigo>/<artigo>.tex \
  ~/code/volXXnumYY/<artigo>/<artigo>.aux \
  volXXnumYY/<artigo>/<artigo>.bbl
```

Os dois modos já cuidam de duas armadilhas do pandoc (ver comentários no
próprio script para detalhes): `\newblock` fazendo o pandoc engolir o
grupo `{...}` seguinte inteiro, e `\textordfeminine` (o "ª") sendo
descartado silenciosamente.

### 2.2 Figuras em TikZ

O pandoc não sabe renderizar `\begin{tikzpicture}` — a figura
simplesmente não aparece no HTML. Em vez de tentar recompilar o tikz
isoladamente (viu a fonte/escala/pacotes ficar diferente do PDF
publicado), **extraia a figura já renderizada do PDF final do artigo**:

1. Renderize a(s) página(s) relevante(s) em alta resolução e olhe onde
   está a figura:
   ```bash
   pdftoppm -png -r 300 -f <pagina> -l <pagina> artigo.pdf /tmp/pagina
   ```
   Leia a imagem gerada (ex.: com a ferramenta Read do Claude Code) para
   achar a posição aproximada. Se for difícil acertar de primeira, gere
   uma versão com grade de coordenadas sobreposta (linhas a cada 100px
   com `magick ... -draw "line ..."`) para ler as coordenadas com
   precisão antes de cortar.
2. Corte, apare a margem branca e adicione uma borda de volta:
   ```bash
   ./scripts/crop_figure.sh artigo.pdf <pagina> <x> <y> <largura> <altura> \
     volXXnumYY/<artigo>/nome_da_figura.png
   ```
3. No `.tex` copiado, troque cada bloco `\begin{tikzpicture}...\end{tikzpicture}`
   por `\includegraphics[width=0.85\linewidth]{nome_da_figura.png}`. Com
   poucas figuras isso é mais rápido a mão; com muitas, um `re.sub` com
   `re.DOTALL` e uma lista de nomes de imagem na ordem em que aparecem
   funciona bem (foi o que foi feito no Volume 4).

Confira sempre se a imagem cortada não tem outra figura ou texto
sobreposto por engano (a única forma confiável é abrir a imagem cortada e
olhar).

## 3. Rodar o pandoc

```bash
cd volXXnumYY/<artigo>
pandoc <artigo>.tex -f latex -t html5 -o <artigo>.html --mathjax
```

## 4. Corrigir artefatos do HTML gerado

```bash
python3 scripts/postprocess_html.py volXXnumYY/*/*.html
```

Isso remove dois artefatos que aparecem sempre:
- Um `<p><span>NN</span></p>` solto logo no início de
  `<div class="thebibliography">` (sobra do argumento `{99}` de
  `\begin{thebibliography}{99}`).
- Os argumentos de posição/largura do `\begin{wrapfigure}{L}{1.7cm}`
  (usado nas mini-bios no fim de cada artigo) aparecendo como texto
  visível (`<span>L</span><span>1.7cm</span>`) do lado da foto.

Depois disso, dê uma conferida manual no HTML de cada artigo por outros
problemas específicos daquele artigo (ambientes de teorema/definição
customizados, `\theoremstyle` em inglês vs português, tabelas, etc. — ver
`CLAUDE.md` para a lista de classes CSS já preparadas para esses casos).

## 5. Front matter

Cada `<artigo>.html` recebe, no topo:

```yaml
---
layout: artigo
title: "Título do artigo"
subtitle: <Nome da Seção>
author: <Autor(es)>
description: "Uma frase resumindo o artigo, para SEO/redes sociais."
---
```

E o `index.html` da edição (`volXXnumYY/index.html`):

```yaml
---
layout: edicao
edition: Volume X, Número Y
title: "Volume X, Número Y"
description: "Uma frase resumindo a edição."
image: capa.png
pdfurl: volXXnumYY.pdf
sections:
- section: <Nome da Seção>
  title: <Título do artigo>
  author: <Autor(es)>
  pages: <inicio>-<fim>
  url: <pasta-do-artigo>
# ... uma entrada por artigo, na ordem do sumário
---
```

Os números de página vêm de `hipatia.cls`, no repositório fonte
(`\newcommand{\xxxpage}{N}` para cada seção — dá a página inicial; a
final é `inicial + páginas_do_pdf_do_artigo - 1`, com
`pdfinfo <artigo>.pdf`).

## 6. Atualizar o índice do site

Em `index.html` (raiz), adicione a edição na lista `editions:`.

Crie `_posts/AAAA-MM-DD-nova-edicao.md`:

```yaml
---
title:  "Nova edição"
---

Está no ar mais uma edição da
**Revista de Matemática Hipátia** (Volume X, Número Y).
```

## 7. Testar localmente

```bash
cd ~/code/revistahipatia.github.io
bundle exec jekyll build
```

**Atenção**: se você já tiver um `bundle exec jekyll serve` rodando em
background, ele normalmente reconstrói sozinho ao detectar mudanças nos
arquivos — mas isso **não funciona de forma confiável neste tipo de
ambiente** (sandbox sem suporte completo a inotify). Depois de qualquer
mudança, rode `bundle exec jekyll build` manualmente e só então recarregue
a página; não confie no auto-reload.

Se for a primeira vez rodando no ambiente, `bundle install` pode falhar
com erro de permissão tentando escrever no gem path do sistema — nesse
caso:

```bash
bundle config set --local path 'vendor/bundle'
bundle install
```

Confira pelo menos: matemática renderizando (MathJax), imagens com o
caminho certo, bibliografia numerada e com o heading "Bibliografia",
figuras de TikZ extraídas aparecendo, mini-bios no fim de cada artigo.
