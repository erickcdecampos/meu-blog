#!/usr/bin/env python3
"""
Converte posts do WordPress (dump SQL) para arquivos Markdown do Hugo.

Lê /tmp/wp_database.sql e gera arquivos em content/posts/.
"""

import os
import re
import sys
import html
from datetime import datetime

try:
    import html2text
    HAS_HTML2TEXT = True
except ImportError:
    HAS_HTML2TEXT = False
    print("AVISO: html2text não encontrado. Usando conversão básica.")

SQL_FILE = '/tmp/wp_database.sql'
POSTS_OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts')


# ---------------------------------------------------------------------------
# Parsing do SQL
# ---------------------------------------------------------------------------

def _find_statement_end(text, start):
    """Encontra o ';' que termina um INSERT, ignorando ';' dentro de strings SQL."""
    i = start
    in_string = False
    escaped = False
    while i < len(text):
        c = text[i]
        if escaped:
            escaped = False
            i += 1
            continue
        if c == '\\' and in_string:
            escaped = True
            i += 1
            continue
        if c == "'" and not in_string:
            in_string = True
            i += 1
            continue
        if c == "'" and in_string:
            if i + 1 < len(text) and text[i + 1] == "'":
                i += 2
                continue
            in_string = False
            i += 1
            continue
        if not in_string and c == ';':
            return i
        i += 1
    return i


def parse_sql_inserts(sql_text, table_name):
    """Extrai todas as linhas de um INSERT INTO table_name (...) VALUES (...)"""
    # Pega os nomes das colunas
    col_pattern = re.compile(
        rf"CREATE TABLE `{table_name}`\s*\((.*?)\)\s*(?:ENGINE|;)",
        re.DOTALL | re.IGNORECASE
    )
    col_match = col_pattern.search(sql_text)
    columns = []
    if col_match:
        for line in col_match.group(1).split('\n'):
            line = line.strip()
            m = re.match(r'`(\w+)`', line)
            if m and not line.upper().startswith(('PRIMARY', 'KEY', 'UNIQUE', 'INDEX', 'CONSTRAINT')):
                columns.append(m.group(1))

    # Localiza cada INSERT e extrai o bloco VALUES com scanner ciente de aspas
    # (evita parar em ';' dentro do conteúdo HTML/CSS dos posts)
    rows = []
    header_pattern = re.compile(
        rf"INSERT INTO `{table_name}`(?:\s*\([^)]*\))?\s*VALUES\s*",
        re.IGNORECASE
    )
    for m in header_pattern.finditer(sql_text):
        start = m.end()
        end = _find_statement_end(sql_text, start)
        values_str = sql_text[start:end]
        for row in parse_values_rows(values_str):
            if columns:
                rows.append(dict(zip(columns, row)))
            else:
                rows.append(row)

    return rows


def parse_values_rows(values_str):
    """Parse múltiplos (...) do VALUES, respeitando strings com vírgulas e escapes."""
    rows = []
    i = 0
    values_str = values_str.strip()

    while i < len(values_str):
        if values_str[i] != '(':
            i += 1
            continue
        i += 1  # pula '('
        fields = []
        current = []
        in_string = False
        escaped = False

        while i < len(values_str):
            c = values_str[i]

            if escaped:
                current.append(c)
                escaped = False
                i += 1
                continue

            if c == '\\' and in_string:
                current.append(c)
                escaped = True
                i += 1
                continue

            if c == "'" and not in_string:
                in_string = True
                i += 1
                continue

            if c == "'" and in_string:
                # Verifica se é '' (escape de aspas no SQL)
                if i + 1 < len(values_str) and values_str[i + 1] == "'":
                    current.append("'")
                    i += 2
                    continue
                in_string = False
                i += 1
                continue

            if not in_string:
                if c == ',':
                    fields.append(''.join(current).strip())
                    current = []
                    i += 1
                    continue
                if c == ')':
                    fields.append(''.join(current).strip())
                    rows.append(fields)
                    i += 1
                    break

            current.append(c)
            i += 1

        # Pula vírgula entre rows
        while i < len(values_str) and values_str[i] in (' ', '\n', '\r', ','):
            i += 1

    return rows


def sql_unescape(s):
    """Decodifica sequências de escape MySQL preservadas literalmente pelo parser."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            nc = s[i + 1]
            if nc == 'n':
                result.append('\n')
            elif nc == 'r':
                result.append('\r')
            elif nc == 't':
                result.append('\t')
            elif nc == '\\':
                result.append('\\')
            elif nc == "'":
                result.append("'")
            elif nc == '"':
                result.append('"')
            else:
                result.append('\\')
                result.append(nc)
            i += 2
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


def unquote(val):
    """Remove aspas simples ao redor de um valor SQL."""
    val = val.strip()
    if val.startswith("'") and val.endswith("'"):
        val = val[1:-1]
    return sql_unescape(val)


# ---------------------------------------------------------------------------
# Conversão HTML → Markdown
# ---------------------------------------------------------------------------

def html_to_markdown(html_content):
    if not html_content or html_content == 'NULL':
        return ''

    # Decodifica escapes MySQL que o parser preservou literalmente (\n, \", \\, etc.)
    html_content = sql_unescape(html_content)

    # Decodifica entidades HTML
    content = html.unescape(html_content)

    # Remove shortcodes WordPress [caption], [gallery], etc.
    content = re.sub(r'\[caption[^\]]*\](.*?)\[/caption\]', r'\1', content, flags=re.DOTALL)
    content = re.sub(r'\[gallery[^\]]*\]', '', content)
    content = re.sub(r'\[/?[a-zA-Z_-]+[^\]]*\]', '', content)

    # Remapeia caminhos de imagens (usa só o basename pois o archive não tem subpastas)
    def _remap_img(m):
        attr = m.group(1)
        basename = m.group(2).rsplit('/', 1)[-1]
        return f'{attr}="/images/{basename}"'

    content = re.sub(
        r'(src|href)=["\']https?://[^"\']*?/wp-content/uploads/[^"\']+/([^"\'/?]+)["\']',
        _remap_img,
        content
    )

    if HAS_HTML2TEXT:
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0
        h.protect_links = True
        h.wrap_links = False
        return h.handle(content).strip()
    else:
        # Conversão básica sem html2text
        content = re.sub(r'<h([1-6])[^>]*>(.*?)</h\1>', lambda m: '#' * int(m.group(1)) + ' ' + m.group(2) + '\n', content, flags=re.DOTALL)
        content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', content, flags=re.DOTALL)
        content = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', content, flags=re.DOTALL)
        content = re.sub(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', r'[\2](\1)', content, flags=re.DOTALL)
        content = re.sub(r'<img[^>]*src=["\']([^"\']+)["\'][^>]*alt=["\']([^"\']*)["\'][^>]*/>', r'![\2](\1)', content)
        content = re.sub(r'<img[^>]*src=["\']([^"\']+)["\'][^>]*/>', r'![](\1)', content)
        content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', content, flags=re.DOTALL)
        content = re.sub(r'<br\s*/?>', '\n', content)
        content = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', content, flags=re.DOTALL)
        content = re.sub(r'<[^>]+>', '', content)
        return content.strip()


# ---------------------------------------------------------------------------
# Geração de slug
# ---------------------------------------------------------------------------

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[àáâãäå]', 'a', text)
    text = re.sub(r'[èéêë]', 'e', text)
    text = re.sub(r'[ìíîï]', 'i', text)
    text = re.sub(r'[òóôõö]', 'o', text)
    text = re.sub(r'[ùúûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'[ñ]', 'n', text)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not os.path.exists(SQL_FILE):
        print(f"ERRO: {SQL_FILE} não encontrado.")
        print("Execute primeiro: python3 scripts/extract_wpress.py")
        sys.exit(1)

    print(f"Lendo {SQL_FILE}...")
    with open(SQL_FILE, 'r', encoding='utf-8', errors='replace') as f:
        sql = f.read()
    print(f"SQL carregado: {len(sql) / 1024 / 1024:.1f} MB\n")

    # Detecta o prefixo das tabelas
    import re as _re
    prefix_match = _re.search(r'CREATE TABLE `(\w+)posts`', sql)
    if prefix_match:
        prefix = prefix_match.group(1)
    else:
        prefix = 'SERVMASK_PREFIX_'
    print(f"Prefixo das tabelas detectado: '{prefix}'\n")

    # Extrai posts
    print("Extraindo posts...")
    posts = parse_sql_inserts(sql, f'{prefix}posts')
    published = [p for p in posts if isinstance(p, dict)
                 and p.get('post_status') == 'publish'
                 and p.get('post_type') == 'post']
    print(f"  Total de entradas em {prefix}posts: {len(posts)}")
    print(f"  Posts publicados: {len(published)}\n")

    if not published:
        print("Nenhum post publicado encontrado.")
        print("Verifique se o SQL foi extraído corretamente.")
        sys.exit(1)

    # Extrai categorias e tags
    print("Extraindo taxonomias (categorias/tags)...")
    terms = parse_sql_inserts(sql, f'{prefix}terms')
    term_taxonomy = parse_sql_inserts(sql, f'{prefix}term_taxonomy')
    term_relationships = parse_sql_inserts(sql, f'{prefix}term_relationships')

    # Mapeia term_id → nome
    term_map = {}
    for t in terms:
        if isinstance(t, dict):
            term_map[t.get('term_id')] = t.get('name', '')

    # Mapeia term_taxonomy_id → (taxonomy, term_id)
    tt_map = {}
    for tt in term_taxonomy:
        if isinstance(tt, dict):
            tt_map[tt.get('term_taxonomy_id')] = {
                'taxonomy': tt.get('taxonomy'),
                'term_id': tt.get('term_id')
            }

    # Mapeia post_id → lista de (taxonomy, nome)
    post_terms = {}
    for rel in term_relationships:
        if isinstance(rel, dict):
            pid = rel.get('object_id')
            ttid = rel.get('term_taxonomy_id')
            if pid and ttid and ttid in tt_map:
                tt = tt_map[ttid]
                term_name = term_map.get(tt['term_id'], '')
                if term_name and term_name != 'Uncategorized' and term_name != 'Sem categoria':
                    post_terms.setdefault(pid, []).append((tt['taxonomy'], term_name))

    # Gera arquivos Markdown
    os.makedirs(POSTS_OUTPUT, exist_ok=True)
    created = 0
    skipped = 0

    print(f"Gerando arquivos Markdown em {POSTS_OUTPUT}...\n")

    for post in published:
        title = post.get('post_title', 'Sem título')
        if title == 'NULL' or not title:
            title = 'Sem título'

        content_raw = post.get('post_content', '')
        if content_raw == 'NULL':
            content_raw = ''

        post_date = post.get('post_date', '')
        post_id = post.get('ID', '')
        post_name = post.get('post_name', '')

        # Slug do arquivo
        if post_name and post_name != 'NULL' and post_name.strip():
            slug = post_name.strip()
        else:
            slug = slugify(title) or f'post-{post_id}'

        # Data
        try:
            dt = datetime.strptime(post_date, '%Y-%m-%d %H:%M:%S')
            date_str = dt.strftime('%Y-%m-%dT%H:%M:%S-03:00')
        except Exception:
            date_str = '2020-01-01T00:00:00-03:00'

        # Categorias e tags
        cats = []
        tags = []
        for taxonomy, name in post_terms.get(post_id, []):
            if taxonomy == 'category':
                cats.append(name)
            elif taxonomy == 'post_tag':
                tags.append(name)

        # Frontmatter
        frontmatter = f'---\ntitle: "{title.replace(chr(34), chr(39))}"\ndate: {date_str}\ndraft: false\n'
        if cats:
            cats_yaml = ', '.join(f'"{c}"' for c in cats)
            frontmatter += f'categories: [{cats_yaml}]\n'
        if tags:
            tags_yaml = ', '.join(f'"{t}"' for t in tags)
            frontmatter += f'tags: [{tags_yaml}]\n'
        frontmatter += '---\n\n'

        # Converte conteúdo
        markdown_content = html_to_markdown(content_raw)

        # Arquivo de saída
        filename = f'{slug}.md'
        filepath = os.path.join(POSTS_OUTPUT, filename)

        if os.path.exists(filepath):
            skipped += 1
            continue

        with open(filepath, 'w', encoding='utf-8') as out:
            out.write(frontmatter + markdown_content)

        created += 1
        print(f"  ✓ {filename}")

    print(f"\n{'='*50}")
    print(f"Posts criados: {created}")
    print(f"Posts pulados (já existiam): {skipped}")
    print(f"\nAgora rode: hugo server -D")
    print(f"E acesse: http://localhost:1313")


if __name__ == '__main__':
    main()
