# Margem

Tema Hugo pessoal para blogs de escrita e fotografia. Orgânico, tipográfico, sem excessos.

---

## Estética

| Elemento | Valor |
|---|---|
| **Fundo** | `#EDEAE4` — pedra clara, cinza-quente |
| **Texto** | `#1A1714` — quase preto com tom quente |
| **Accent** | `#C97D5A` — âmbar suave |
| **Muted** | `#8B8070` — bege-cinza |
| **Títulos** | DM Serif Display (Google Fonts) |
| **Corpo** | DM Sans (Google Fonts) |

---

## Requisitos

- Hugo Extended **0.120+** (necessário para compilar SCSS)
- Conexão à internet no build (Google Fonts via CDN)

---

## Estrutura de arquivos

```
themes/margem/
├── theme.toml
├── README.md
├── assets/
│   └── scss/
│       └── main.scss          # Todos os estilos (variáveis, componentes)
└── layouts/
    ├── _default/
    │   ├── baseof.html        # Template base (head + header + main + footer)
    │   ├── single.html        # Post ou página individual
    │   └── list.html          # Listagem de seção (ex: /posts/)
    ├── index.html             # Homepage — feed misto de posts e álbuns
    ├── fotografia/
    │   ├── list.html          # Grade de álbuns em /fotografia/
    │   └── single.html        # Álbum individual com lightbox (PhotoSwipe v5)
    └── partials/
        ├── head.html          # <head>: meta, fonts, CSS
        ├── header.html        # Navegação superior
        ├── footer.html        # Rodapé
        ├── post-card.html     # Card reutilizável para posts e álbuns no feed
        └── album-card.html    # Card de álbum para a grade /fotografia/
```

---

## Configuração do site (`hugo.toml`)

```toml
theme = "margem"

[params]
  description  = "Seu texto de bio aqui"
  mainSections = ["posts", "fotografia"]  # seções que aparecem no feed da home

[params.author]
  name = "Seu Nome"

[params.footer]
  since = 2021  # ano inicial no copyright

[menu]
  [[menu.main]]
    name   = "Início"
    url    = "/"
    weight = 1
  [[menu.main]]
    name   = "Posts"
    url    = "/posts/"
    weight = 2
  [[menu.main]]
    name   = "Fotografia"   # separador visual aparece antes deste item
    url    = "/fotografia/"
    weight = 3
  [[menu.main]]
    name   = "Sobre"
    url    = "/sobre/"
    weight = 4
  [[menu.main]]
    name   = "Links"
    url    = "/links/"
    weight = 5
  [[menu.main]]
    name   = "Instante"
    url    = "/now/"
    weight = 6
```

> O separador visual `|` no menu aparece automaticamente antes do item chamado **"Fotografia"**.

---

## Seção de fotografia

### Criar a seção

```
content/
└── fotografia/
    └── _index.md
```

`content/fotografia/_index.md`:
```yaml
---
title: "Fotografia"
---
```

### Criar um álbum

Cada álbum é um **Page Bundle** — uma pasta com `index.md` e as fotos dentro:

```
content/fotografia/nome-do-album/
├── index.md
├── capa.jpg       # imagem de capa (usada no card da grade)
├── foto-01.jpg
├── foto-02.jpg
└── ...
```

`index.md` de exemplo:
```yaml
---
title: "Brasília em janeiro"
date: 2026-01-18
description: "Entre o concreto e o cerrado"
photos_count: 24   # opcional — se omitir, o tema conta as imagens automaticamente
---

Texto opcional sobre o álbum (aparece abaixo das fotos).
```

**Capa do álbum:** o tema procura por `capa.*` ou `cover.*` na pasta.
Se nenhum dos dois existir, o card exibe um placeholder na cor do tema.

**Lightbox:** ao abrir um álbum, todas as imagens `.jpg`, `.jpeg`, `.png` e `.webp`
da pasta são exibidas em grade com lightbox [PhotoSwipe v5](https://photoswipe.com/).

---

## Seção de posts

Posts seguem o padrão Hugo normal como Page Bundles:

```
content/posts/nome-do-post/
├── index.md
└── imagem-destaque.jpg   # opcional
```

`index.md` de exemplo:
```yaml
---
title: "Título do post"
date: 2026-01-12
description: "Subtítulo ou resumo curto"
image: imagem-destaque.jpg   # opcional
---

Conteúdo em Markdown...
```

---

## Customização de estilos

Todas as variáveis de design ficam no topo de `assets/scss/main.scss`:

```scss
:root {
  --bg:       #EDEAE4;   /* fundo principal */
  --bg-card:  #E5E1DA;   /* fundo de cards */
  --bg-hover: #DEDAD2;   /* hover de cards e menu */
  --text:     #1A1714;   /* texto principal */
  --muted:    #8B8070;   /* texto secundário */
  --border:   #D4CFC7;   /* bordas e separadores */
  --accent:   #C97D5A;   /* cor de destaque (âmbar) */
  --accent-l: #F2E6DC;   /* accent claro (fundo de tags) */

  --font-title: 'DM Serif Display', Georgia, serif;
  --font-body:  'DM Sans', system-ui, sans-serif;

  --container: 720px;    /* largura máxima do conteúdo */
  --radius:    3px;      /* arredondamento de bordas */
}
```

Para trocar a paleta ou fontes, edite apenas essas variáveis.

---

## Desenvolvimento local

```bash
hugo server -D
```

O `-D` inclui rascunhos (`draft: true`), útil durante a criação de conteúdo.
