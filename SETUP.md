# Blog Hugo — Documentação de Setup

## Estrutura do Projeto

```
~/Documentos/blog/
├── hugo.toml                  # Configuração do Hugo
├── themes/PaperMod/           # Tema (git submodule)
├── content/posts/             # Posts em Markdown
├── static/images/             # Imagens (a extrair do .wpress)
├── scripts/
│   ├── extract_wpress.py      # Extrai database.sql e imagens do backup WP
│   └── wp_to_hugo.py          # Converte SQL do WP em posts Markdown Hugo
└── abc-erickcoelho-xyz-*.wpress  # Backup WordPress (431 MB)
```

---

## O que foi feito

### 1. Hugo instalado
- Versão: Hugo Extended 0.146.0
- Instalado via `.deb` do GitHub Releases
- Comando: `sudo dpkg -i /tmp/hugo.deb`

### 2. Site Hugo criado
- Tema: PaperMod (instalado como git submodule)
- Idioma: pt-br
- Configurado em `hugo.toml`

### 3. Scripts de migração do WordPress

#### `scripts/extract_wpress.py`
Extrai o arquivo `.wpress` (backup do plugin All-in-One WP Migration).

**Formato do .wpress (confirmado por inspeção binária):**
- 255 bytes: nome do arquivo (null-padded)
- 14 bytes: tamanho lógico como string decimal (null-padded)
- 4108 bytes: preâmbulo (timestamp + nulls)
- N bytes: conteúdo real

**O que extrai:**
- `database.sql` → salvo em `/tmp/wp_database.sql`
- `wp-content/uploads/**` → salvo em `static/images/`

**Problema conhecido:** As imagens foram encontradas (12.568 entradas processadas) mas extraídas como 0. A lógica de detecção do magic bytes das imagens precisa ser ajustada — o preâmbulo das imagens pode ter tamanho diferente de 4108 bytes.

**Rodar:**
```bash
python3 scripts/extract_wpress.py
```

#### `scripts/wp_to_hugo.py`
Converte o dump SQL do WordPress em arquivos Markdown para o Hugo.

**O que faz:**
- Detecta o prefixo das tabelas automaticamente (era `SERVMASK_PREFIX_` neste caso)
- Lê `wp_posts` (filtrado por `post_status='publish'` e `post_type='post'`)
- Extrai categorias e tags das tabelas `wp_terms`, `wp_term_taxonomy`, `wp_term_relationships`
- Converte HTML → Markdown com `html2text`
- Remove shortcodes WordPress
- Gera frontmatter YAML com título, data, categorias e tags
- Salva em `content/posts/{slug}.md`

**Problema conhecido:** Só encontrou 2 posts publicados, mas o blog tinha mais. Possíveis causas:
1. O parser de VALUES do SQL falha em registros multilinhas com caracteres especiais
2. Alguns posts podem estar com status diferente no banco (ex: `private`)
3. O regex de INSERT pode não capturar todos os blocos

**Rodar:**
```bash
python3 scripts/wp_to_hugo.py
```

---

## Estado atual (sessão 3)

### O que foi feito
- Migração do WordPress concluída: 6 posts publicados + 4 rascunhos importados
- Páginas importadas: `sobre.md`, `links.md`, `now.md` (em `content/`)
- Posts convertidos para Page Bundles (`content/posts/nome/index.md`)
- Tema trocado de PaperMod → **hugo-theme-stack** (submodule em `themes/hugo-theme-stack/`)
- Hugo atualizado para **0.160.1 Extended**
- Imagens de destaque configuradas via campo `image:` no frontmatter dos posts que têm imagem
- Posts sem imagem têm comentário `# image: adicione-aqui.jpg` no frontmatter

### Pendências

#### A — Deploy: GitHub + Netlify
```bash
# Criar repositório no GitHub
gh repo create meu-blog --public

git add .
git commit -m "feat: setup Hugo blog with Stack theme"
git remote add origin https://github.com/SEU_USER/meu-blog.git
git push -u origin master
```

No Netlify (netlify.com):
1. "Add new site" → "Import from Git"
2. Conectar GitHub → selecionar o repositório
3. Build command: `hugo`
4. Publish directory: `public`
5. Environment variable: `HUGO_VERSION = 0.160.1`

#### B — Galeria de fotos em /fotografia (planejado, não implementado)
Plano detalhado em: `~/.claude/plans/stateless-doodling-engelbart.md`

**Resumo do plano:**
- Criar `themes/erick-blog/` copiando o Stack como base
- Adicionar layouts de galeria para a seção `fotografia/` dentro do tema próprio
- Integrar PhotoSwipe (lightbox) e grid responsivo apenas nas páginas de fotografia
- Álbuns aparecem no feed da home misturados com posts (via `mainSections = ["posts", "fotografia"]`)
- Cada álbum = pasta `content/fotografia/nome-album/` com `index.md` + fotos
- Capa do álbum: campo `image: capa.jpg` no frontmatter + `params.cover: true` nos resources

---

## Comandos úteis

```bash
# Ver o blog localmente
hugo server -D

# Criar novo post
hugo new content posts/nome-do-post.md

# Build para produção
hugo
```

---

## Informações do backup WordPress

- Arquivo: `abc-erickcoelho-xyz-20260315-160316-2l31ink3kq1b.wpress`
- Tamanho: 430.9 MB
- Plugin: All-in-One WP Migration v7.102
- WordPress: 6.9.4
- Site original: `https://abc.erickcoelho.xyz`
- Banco: `u666796860_wnMRM`
- Prefixo de tabelas no dump: `SERVMASK_PREFIX_` (substituído por `wp_` na instalação real)
