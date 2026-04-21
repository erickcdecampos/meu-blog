#!/usr/bin/env python3
"""
Extrai arquivos de um backup .wpress (All-in-One WP Migration).

Formato confirmado por inspeção binária:
  [255 bytes: nome do arquivo, null-padded]
  [14 bytes: tamanho LÓGICO como decimal string, null-padded]
  [4108 bytes: preâmbulo (timestamp + nulls)]
  [tamanho-lógico bytes: conteúdo real do arquivo]

Próxima entrada começa em: offset_atual + 255 + 14 + 4108 + tamanho_lógico
"""

import os
import sys
import re

SQL_OUTPUT = '/tmp/wp_database.sql'
IMAGES_OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'static', 'images')

NAME_SIZE = 255
FILESIZE_SIZE = 14
PREAMBLE_SIZE = 4108

# SQL pode ter um preâmbulo diferente — detectamos pelo magic
SQL_MAGIC = [b'-- Database:', b'-- MySQL', b'-- MariaDB', b'SET SQL', b'/*!']
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.tiff', '.tif'}


def find_wpress_file():
    blog_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    for fname in os.listdir(blog_dir):
        if fname.endswith('.wpress'):
            return os.path.join(blog_dir, fname)
    return None


def find_sql_start(data):
    """Encontra o offset do início real do SQL dentro dos bytes lidos."""
    for magic in SQL_MAGIC:
        idx = data.find(magic)
        if idx != -1:
            return idx
    return PREAMBLE_SIZE  # fallback


def extract_wpress(wpress_path, sql_out, images_out):
    os.makedirs(images_out, exist_ok=True)
    file_total = os.path.getsize(wpress_path)

    print(f"Abrindo: {wpress_path}")
    print(f"Tamanho: {file_total / 1024 / 1024:.1f} MB\n")

    sql_extracted = False
    images_extracted = 0
    total_entries = 0
    pos = 0

    with open(wpress_path, 'rb') as f:
        while pos < file_total:
            f.seek(pos)

            name_raw = f.read(NAME_SIZE)
            if len(name_raw) < NAME_SIZE:
                break

            filename = name_raw.rstrip(b'\x00').decode('utf-8', errors='replace').strip()

            size_raw = f.read(FILESIZE_SIZE)
            if len(size_raw) < FILESIZE_SIZE:
                break

            size_str = size_raw.rstrip(b'\x00').decode('ascii', errors='replace').strip()

            if not filename or not size_str.isdigit():
                pos += 1
                continue

            logical_size = int(size_str)
            content_start = pos + NAME_SIZE + FILESIZE_SIZE
            physical_size = PREAMBLE_SIZE + logical_size
            next_entry_pos = content_start + physical_size
            total_entries += 1

            if total_entries % 200 == 0:
                pct = pos * 100 // file_total
                print(f"  Entradas: {total_entries} | {pct}% ({pos // 1024 // 1024} MB)")

            # database.sql
            if filename == 'database.sql' or filename.endswith('/database.sql'):
                print(f"  [SQL] Encontrado: '{filename}' (lógico: {logical_size / 1024:.0f} KB)")
                f.seek(content_start)
                raw_content = f.read(min(8192, physical_size))
                sql_start_offset = find_sql_start(raw_content)

                f.seek(content_start + sql_start_offset)
                sql_bytes = f.read(physical_size - sql_start_offset)
                with open(sql_out, 'wb') as out:
                    out.write(sql_bytes)
                sql_extracted = True
                print(f"  [SQL] Salvo ({len(sql_bytes) / 1024:.0f} KB) → {sql_out}")

            # Imagens — detectadas pela extensão (o archive não guarda o path completo)
            else:
                basename = os.path.basename(filename)
                _, ext = os.path.splitext(basename.lower())
                if ext in IMAGE_EXTS and logical_size > 0:
                    dest_path = os.path.join(images_out, basename)
                    if not os.path.exists(dest_path):
                        f.seek(content_start + PREAMBLE_SIZE)
                        img_bytes = f.read(logical_size)
                        with open(dest_path, 'wb') as out:
                            out.write(img_bytes)
                    images_extracted += 1
                    if images_extracted % 100 == 0:
                        print(f"  [IMG] {images_extracted} imagens extraídas...")

            pos = next_entry_pos

    print(f"\n✓ Total de entradas processadas: {total_entries}")
    print(f"✓ database.sql extraído: {sql_extracted}")
    print(f"✓ Imagens extraídas: {images_extracted}")
    return sql_extracted, images_extracted


if __name__ == '__main__':
    wpress = find_wpress_file()
    if not wpress:
        print("ERRO: Arquivo .wpress não encontrado na pasta do blog.")
        sys.exit(1)

    sql_ok, imgs = extract_wpress(wpress, SQL_OUTPUT, IMAGES_OUTPUT)

    if not sql_ok:
        print("\nERRO: database.sql não foi encontrado no archive.")
        sys.exit(1)

    print("\nExtração concluída! Execute agora:")
    print("  python3 scripts/wp_to_hugo.py")
