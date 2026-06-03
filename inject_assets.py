#!/usr/bin/env python3
"""
inject_assets.py
─────────────────
Uso: python3 inject_assets.py original_index.html new_index.html output.html

Este script extrai os base64 do seu index.html original e injeta no novo.
Execute no terminal (Mac, Linux ou Git Bash no Windows).

Exemplo:
  python3 inject_assets.py index_original.html index_novo.html index_final.html
"""

import sys
import re
import base64

def extract_base64_src(html, pattern):
    """Extract base64 data from a data:... src attribute"""
    match = re.search(pattern, html)
    if match:
        return match.group(1)
    return None

def extract_base64_from_audio(html):
    """Extract base64 from audio src"""
    match = re.search(r'<source\s+src="data:audio/[^;]+;base64,([^"]+)"', html)
    if match:
        return match.group(1)
    return None

def main():
    if len(sys.argv) < 4:
        print("Uso: python3 inject_assets.py original.html novo.html saida.html")
        sys.exit(1)

    original_file = sys.argv[1]
    new_file = sys.argv[2]
    output_file = sys.argv[3]

    print(f"Lendo original: {original_file}")
    with open(original_file, 'r', encoding='utf-8') as f:
        original = f.read()

    print(f"Lendo novo: {new_file}")
    with open(new_file, 'r', encoding='utf-8') as f:
        new_html = f.read()

    replacements = {}

    # ─── PHOTO (Michel's photo) ───
    # Looking for img src with base64 in hero/about section
    photo_patterns = [
        r'<img[^>]+alt="Michel[^"]*"[^>]+src="data:image/[^;]+;base64,([^"]{100,})"',
        r'src="data:image/png;base64,(/9j/[^"]{100,})"',  # JPEG in PNG container
        r'src="data:image/jpeg;base64,([^"]{100,})"',
    ]
    for p in photo_patterns:
        photo_b64 = extract_base64_src(original, p)
        if photo_b64 and len(photo_b64) > 1000:
            replacements['__PHOTO_BASE64__'] = photo_b64
            print(f"✓ Foto extraída ({len(photo_b64)//1024}KB)")
            break

    # ─── LOGO ───
    logo_patterns = [
        r'<img[^>]+alt="Lux[^"]*"[^>]+src="data:image/[^;]+;base64,([^"]{100,})"',
        r'nav-logo.*?src="data:image/[^;]+;base64,([^"]{100,})"',
    ]
    for p in logo_patterns:
        logo_b64 = extract_base64_src(original, p)
        if logo_b64 and len(logo_b64) > 200:
            replacements['__LOGO_BASE64__'] = logo_b64
            print(f"✓ Logo extraído ({len(logo_b64)//1024}KB)")
            break

    # ─── BOOK PDF ───
    # Looking for pdf base64 in download link or function
    book_patterns = [
        r'"data:application/pdf;base64,([^"]{1000,})"',
        r"'data:application/pdf;base64,([^']{1000,})'",
        r'book-dl-link.*?href="data:application/pdf;base64,([^"]{1000,})"',
    ]
    for p in book_patterns:
        book_b64 = extract_base64_src(original, p)
        if book_b64 and len(book_b64) > 1000:
            replacements['__BOOK_PDF_BASE64__'] = book_b64
            print(f"✓ Livro PDF extraído ({len(book_b64)//1024}KB)")
            break

    # ─── AUDIO ───
    audio_b64 = extract_base64_from_audio(original)
    if audio_b64 and len(audio_b64) > 100:
        replacements['__AUDIO_BASE64__'] = audio_b64
        print(f"✓ Áudio extraído ({len(audio_b64)//1024}KB)")

    # ─── WELLNESS BOOK HTML ───
    # Looking for wellness book HTML base64 in the original
    wellness_patterns = [
        r'wellness-dl-link.*?href="data:text/html;base64,([^"]{1000,})"',
        r'"data:text/html;base64,([^"]{1000,})"',
    ]
    for p in wellness_patterns:
        wellness_b64 = extract_base64_src(original, p)
        if wellness_b64 and len(wellness_b64) > 100:
            replacements['__WELLNESS_HTML_BASE64__'] = wellness_b64
            print(f"✓ Wellness Book extraído ({len(wellness_b64)//1024}KB)")
            break

    # ─── APPS SCRIPT URL ───
    apps_url_match = re.search(r"const APPS_SCRIPT_URL\s*=\s*'(https://script\.google\.com/[^']+)'", original)
    if not apps_url_match:
        apps_url_match = re.search(r'"(https://script\.google\.com/macros/s/[^"]+)"', original)
    if apps_url_match:
        new_html = new_html.replace(
            'https://script.google.com/macros/s/AKfycbxNimHpDoO6nF0EuE8oW3bSLf6pG3YkM1A8F42aBqj7y2YjIqpFrqJD4Oq7J2xZY5pL/exec',
            apps_url_match.group(1)
        )
        print(f"✓ Apps Script URL atualizado")

    # ─── APPLY REPLACEMENTS ───
    result = new_html
    for placeholder, value in replacements.items():
        # Replace in src attributes (without quotes)
        result = result.replace(placeholder, value)
        
        # Also replace in JS strings  
        result = result.replace(f"'{placeholder}'", f"'{value}'")

    # Report missing
    missing = []
    for placeholder in ['__PHOTO_BASE64__', '__LOGO_BASE64__', '__BOOK_PDF_BASE64__', '__AUDIO_BASE64__', '__WELLNESS_HTML_BASE64__']:
        if placeholder in result:
            missing.append(placeholder)

    if missing:
        print(f"\n⚠️  Placeholders não encontrados no original:")
        for m in missing:
            print(f"   {m}")
        print("   Verifique se o arquivo original tem esses assets em base64.")
    else:
        print("\n✅ Todos os assets injetados com sucesso!")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"\n✓ Arquivo salvo: {output_file}")
    print(f"  Tamanho: {len(result)//1024}KB")

if __name__ == '__main__':
    main()
