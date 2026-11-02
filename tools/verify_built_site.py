"""Check real Jekyll output for missing local links, assets, and fragment targets."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
import sys

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / '_site'
HOST = 'yfeng0206.github.io'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path, self.ids, self.links, self.controls = path, set(), [], []
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        if attrs.get('name') and tag == 'a':
            self.ids.add(attrs['name'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])
        for key in ('aria-labelledby', 'aria-describedby', 'aria-controls'):
            self.controls.extend(attrs.get(key, '').split())


def main():
    if not (BUILD / 'index.html').is_file():
        sys.exit('Run a Jekyll build first; _site/index.html is missing.')
    pages = {p.resolve(): Page(p) for p in BUILD.rglob('*.html')}
    errors = []
    count = 0
    for path, page in pages.items():
        rel = path.relative_to(BUILD)
        for target in page.controls:
            if target not in page.ids:
                errors.append(f'{rel}: missing ARIA target {target}')
        for link in page.links:
            parsed = urlparse(link)
            if parsed.scheme not in ('', 'http', 'https'):
                continue
            if parsed.netloc and parsed.netloc != HOST:
                continue
            base = 'https://' + HOST + '/' + rel.as_posix()
            resolved = urlparse(urljoin(base, link))
            target = (BUILD / unquote(resolved.path).lstrip('/')).resolve()
            if not target.is_relative_to(BUILD.resolve()):
                errors.append(f'{rel}: link escapes build directory: {link}')
                continue
            if target.is_dir():
                target = target / 'index.html'
            if not target.is_file():
                errors.append(f'{rel}: missing local target {link}')
                continue
            count += 1
            fragment = unquote(resolved.fragment)
            if fragment and target in pages and fragment not in pages[target].ids:
                errors.append(f'{rel}: missing fragment {link}')
    if errors:
        sys.exit('\n'.join(errors))
    print(f'Checked {len(pages)} built HTML pages and {count} local links/assets; all targets resolve.')


if __name__ == '__main__':
    main()
