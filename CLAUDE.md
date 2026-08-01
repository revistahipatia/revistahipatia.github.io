# Revista de Matemática Hipátia — site

Site Jekyll (hospedado no GitHub Pages, `revistahipatia.github.io`) da
Revista de Matemática Hipátia, publicação semestral do Departamento de
Matemática do IME/UFBA. Cada edição é convertida de LaTeX (compilado num
repositório fonte separado, ex.: `~/code/vol04num01`) para HTML via
pandoc.

**Para publicar uma nova edição, siga `docs/nova-edicao.md` passo a
passo.** Os scripts referenciados lá estão em `scripts/`. O restante
deste arquivo é contexto e convenções gerais do site.

## Estrutura

- `volXXnumYY/` — uma pasta por edição, com uma subpasta por artigo
  (`.tex` copiado + pré-processado, `.pdf`, imagens, `.html` gerado).
  `volXXnumYY/index.html` é o sumário da edição.
- `_layouts/` — `principal.html` (home), `edicao.html` (sumário de uma
  edição), `artigo.html` (um artigo), `pagina.html` (Equipe, Submissão).
- `assets/stylesheet.css` — todo o CSS do site (não há framework).
- `scripts/` — scripts de apoio para processar uma nova edição.
- `docs/nova-edicao.md` — o runbook completo.

## Embedding no site oficial da UFBA — restrição importante

O site oficial (`dmat.ufba.br/extensao/revista-hipátia`) mostra este site
dentro de um `<iframe>` **fixo em 500px de altura, com overflow
escondido**:

```html
<iframe src="https://revistahipatia.github.io/" width="100%" height="500px"
        style="overflow:hidden"
        sandbox="allow-top-navigation allow-scripts allow-forms allow-downloads allow-same-origin">
```

Por isso, **todo link de navegação (edições, artigos, downloads de PDF,
banner, menu) precisa ter `target="_top"`**, senão o usuário fica preso
navegando dentro dessa caixinha de 500px. Ao adicionar links novos em
qualquer layout, lembre de incluir `target="_top"`.

A home (`principal.html`) é o que aparece dentro dessa janela de 500px —
qualquer mudança nela deve continuar cabendo razoavelmente bem nesse
espaço.

## SEO

- `_config.yml` configura `jekyll-seo-tag` e `jekyll-sitemap`. Todo
  layout inclui `{% seo title=false %}` no `<head>` (o `title=false`
  evita duplicar a tag `<title>`, que já é escrita à mão em cada layout).
- Front matter usado pelo jekyll-seo-tag: `title`, `description`,
  `image`. Artigos já têm `title`/`subtitle`/`author`; ao criar um artigo
  novo, adicione também `description` (uma frase). Edições devem ter
  `title`, `description` e `image: capa.png`.
- `lang: pt-BR` está setado no `_config.yml` e em todo `<html lang="...">`
  dos layouts — não reverter para `en`.
- `robots.txt` e `sitemap.xml` (gerado automaticamente pelo jekyll-sitemap,
  não editar à mão).

## Identidade visual

- A moldura decorativa de meandros (`border-image` com `assets/meander.png`
  no `body`) é parte da identidade visual da revista — não remover nem
  substituir sem pedido explícito.
- Fonte: Libre Baskerville (Google Fonts, carregada em
  `_includes/font.html`) — cuidado ao editar esse arquivo, o nome da
  fonte no `font-family` já teve um erro de digitação (`Baskervville`)
  que fazia cair silenciosamente em serif genérico.
- Cor de destaque/links: `#3f5765` (tom escuro extraído do próprio
  `meander.png`), hover `#1f271c`.
- Ambientes de teorema/definição/problema do LaTeX (`\newtheorem`) viram
  `<div class="theorem">`, `<div class="theorem*">`, `<div class="lemma*">`,
  `<div class="definition">`, `<div class="problem*">` etc. no HTML do
  pandoc — essas classes já têm estilo de "caixa de destaque" em
  `stylesheet.css`; um artigo novo com esses ambientes já sai estilizado
  sem trabalho extra. Se aparecer uma classe nova (`\newtheorem` com nome
  diferente), adicione o seletor à mesma regra no CSS.

## Ambiente local (Jekyll/Ruby)

- `bundle install` pode falhar com erro de permissão no gem path do
  sistema neste tipo de ambiente; rodar
  `bundle config set --local path 'vendor/bundle'` antes resolve.
- `bundle exec jekyll serve --watch` **não reconstrói sozinho de forma
  confiável** neste tipo de ambiente (sandbox). Depois de qualquer
  mudança em arquivo, rode `bundle exec jekyll build` manualmente antes
  de recarregar a página no navegador.
- Nunca commitar `_site/`, `vendor/`, `.bundle/` (já estão no
  `.gitignore`).

## Antes de dar push

Só faça `git push` quando o usuário pedir explicitamente — mesmo depois
de implementar e commitar algo, espere confirmação antes de enviar ao
remoto.
