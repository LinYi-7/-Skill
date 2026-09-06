#!/usr/bin/env python3
"""Render a structured draft to a simple, escaped, inline-style HTML preview."""
import argparse, html, json
from pathlib import Path
from urllib.parse import urlsplit

def esc(text): return html.escape(str(text),quote=True)

def image_src(value):
    value=str(value).strip()
    if not value or any(ord(c)<32 for c in value): raise ValueError('Invalid image source')
    parsed=urlsplit(value)
    if parsed.scheme not in ('','https'): raise ValueError('Use a local relative path or HTTPS image URL')
    if not parsed.scheme and (value.startswith(('/', '\\')) or '\\' in value or '..' in Path(value).parts):
        raise ValueError('Local image paths must be relative without traversal')
    return esc(value)

def render(data):
    if not isinstance(data,dict) or not data.get('title') or not isinstance(data.get('blocks'),list):
        raise ValueError('Expected title and blocks array')
    title=esc(data['title'])
    pieces=[f'<h1 style="font-size:24px;line-height:1.45;margin:0 0 16px;font-weight:700;">{title}</h1>']
    if data.get('subtitle'):
        pieces.append(f'<p style="font-size:14px;color:#555;line-height:1.8;margin:0 0 24px;">{esc(data["subtitle"])}</p>')
    styles={'p':'margin:0 0 14px;font-size:16px;line-height:1.8;',
            'h2':'margin:28px 0 12px;font-size:20px;line-height:1.5;font-weight:700;',
            'note':'margin:12px 0 20px;padding:12px;background:#F0F7F2;color:#34503F;font-size:13px;line-height:1.7;'}
    for block in data['blocks']:
        kind=block.get('type')
        if kind in styles:
            tag='h2' if kind=='h2' else 'p'
            pieces.append(f'<{tag} style="{styles[kind]}">{esc(block.get("text",""))}</{tag}>')
        elif kind=='image':
            src=image_src(block['src'])
            pieces.append(f'<section style="margin:20px 0;"><img src="{src}" alt="{esc(block.get("alt",""))}" style="max-width:100%;height:auto;display:block;margin:0 auto;"/>')
            if block.get('caption'): pieces.append(f'<p style="font-size:13px;color:#555;line-height:1.6;margin:8px 0 0;">{esc(block["caption"])}</p>')
            pieces.append('</section>')
        else: raise ValueError(f'Unsupported block type: {kind}')
    lang=esc(data.get('lang','zh-CN'))
    return f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title></head><body style="margin:0;background:#fff;color:#222;font-family:system-ui,-apple-system,BlinkMacSystemFont,Arial,sans-serif;"><section style="max-width:640px;margin:0 auto;padding:28px 20px;overflow-wrap:anywhere;">'+''.join(pieces)+'</section></body></html>'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('output');a=p.parse_args()
    data=json.loads(Path(a.input).read_text(encoding='utf-8'))
    Path(a.output).write_text(render(data),encoding='utf-8')
    print('Created HTML draft; verify images and target-editor rendering before publication.')

if __name__=='__main__': main()
