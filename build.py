"""Build the site: src/ -> docs/ (served by GitHub Pages from main:/docs).

    python build.py

Each page is src/<lang>/<page>.html: a front block (title, description) and the body. The layout,
the menu words and the settings (contact email, dates, store link) are shared; {{key}} in a body or
the layout is replaced from src/site.json and the language's entry in src/i18n.json. Standard
library only.
"""
import json
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / 'src'
OUT = ROOT / 'docs'
PAGES = ['index', 'privacy', 'terms', 'delete-data']


def front(text: str, path: Path) -> tuple[dict, str]:
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    if not m:
        raise SystemExit(f'{path}: no front block')
    meta = dict(line.split(': ', 1) for line in m.group(1).splitlines() if line.strip())
    return meta, text[m.end():]


def fill(text: str, values: dict, path: Path) -> str:
    def sub(m):
        if m.group(1) not in values:
            raise SystemExit(f'{path}: unknown {{{{{m.group(1)}}}}}')
        return str(values[m.group(1)])
    return re.sub(r'\{\{([a-z_]+)\}\}', sub, text)


def long_date(iso: str, lang: str) -> str:
    d = date.fromisoformat(iso)
    if lang == 'en':
        return f'{d:%B} {d.day}, {d.year}'
    return f'{d.year}年{d.month}月{d.day}日' if lang == 'ja' else f'{d.year} 年 {d.month} 月 {d.day} 日'


def main() -> None:
    site = json.loads((SRC / 'site.json').read_text('utf-8'))
    i18n = json.loads((SRC / 'i18n.json').read_text('utf-8'))
    layout = (SRC / 'layout.html').read_text('utf-8')
    langs = list(i18n)  # the first is the default, served at the root

    def folder(lang: str) -> str:
        return '' if lang == langs[0] else i18n[lang]['dir'] + '/'

    def file(page: str) -> str:
        return '' if page == 'index' else f'{page}.html'

    count = 0
    for lang in langs:
        words = i18n[lang]
        values = {**site, **{k: v for k, v in words.items() if isinstance(v, str)},
                  'updated_long': long_date(site['updated'], lang)}
        # Only the root 404 is served (for every missing path), so its links are absolute.
        for page in PAGES + (['404'] if lang == langs[0] else []):
            path = SRC / lang / f'{page}.html'
            meta, body = front(path.read_text('utf-8'), path)
            root = site['base_url'] if page == '404' else ('../' if folder(lang) else '')

            def link(p: str, other: str = lang) -> str:
                return (root + folder(other) + file(p)) or './'

            nav = '\n'.join(f'<a href="{link(p)}"{" aria-current=\"page\"" if p == page else ""}>'
                            f'{words["nav"][p]}</a>' for p in PAGES)
            switch = '\n'.join(f'<a href="{link(page if page != "404" else "index", o)}" hreflang="{o}" lang="{o}"'
                               f'{" aria-current=\"true\"" if o == lang else ""}>{i18n[o]["name"]}</a>'
                               for o in langs)
            heads = [] if page == '404' else (
                [f'<link rel="canonical" href="{site["base_url"]}{folder(lang)}{file(page)}">'] +
                [f'<link rel="alternate" hreflang="{o}" href="{site["base_url"]}{folder(o)}{file(page)}">'
                 for o in langs])
            here = {**values, 'lang': lang, 'root': root, 'page': page, 'home': link('index')}
            html = fill(layout, {
                **here, 'title': words['app'] if page == 'index' else f'{meta["title"]} · {words["app"]}',
                'description': meta['description'], 'nav': nav, 'switch': switch,
                'heads': '\n'.join(heads), 'body': fill(body, here, path).strip(),
            }, SRC / 'layout.html')
            out = OUT / folder(lang)
            out.mkdir(parents=True, exist_ok=True)
            (out / f'{page}.html').write_text(html, 'utf-8', newline='\n')
            count += 1
    shutil.copyfile(SRC / 'style.css', OUT / 'style.css')
    (OUT / '.nojekyll').write_text('', 'utf-8')
    if site.get('domain'):
        (OUT / 'CNAME').write_text(site['domain'] + '\n', 'utf-8')
    elif (OUT / 'CNAME').exists():
        (OUT / 'CNAME').unlink()
    if '@example.' in site['email']:
        print('warning: src/site.json still has the placeholder contact email')
    print(f'built {count} pages into {OUT.name}/')


if __name__ == '__main__':
    main()
