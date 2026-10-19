"""Check tracked Markdown language and repository-relative links without dependencies.

Run from any directory: python scripts/check-documentation.py [--git PATH].
Application localization, native samples, and historical commit messages are outside
this documentation-only check. Remote links are not fetched. Requires a checkout
containing tracked Markdown, including in sparse checkouts.
"""
import argparse
import re
import subprocess
import unicodedata
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


def slug(text):
    text = re.sub(r'!?\[([^]]*)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text).replace('`', '').strip().lower()
    return ''.join(c for c in text if c in '_- ' or
                   unicodedata.category(c)[0] in 'LN').replace(' ', '-')


def anchors(text):
    result = set(re.findall(r'<(?:a|span)\b[^>]*\b(?:id|name)=["\']([^"\']+)', text))
    counts = {}
    fence = None
    for line in text.splitlines():
        match = re.match(r'^\s*(`{3,}|~{3,})', line)
        if match:
            marker = match[1][0]
            fence = None if fence == marker else marker if fence is None else fence
            continue
        if fence:
            continue
        match = re.match(r'^ {0,3}#{1,6}\s+(.+?)(?:\s+#+)?$', line)
        if match:
            key = slug(match[1]); count = counts.get(key, 0)
            counts[key] = count + 1
            result.add(key + ('-' + str(count) if count else ''))
    return result


def problems(root, tracked):
    documents = {p: root / p for p in tracked if p.lower().endswith('.md')}
    texts = {}
    for name, path in documents.items():
        if not path.is_file():
            yield name, 0, 'tracked Markdown absent; expand sparse checkout'
            continue
        text = path.read_text(encoding='utf-8-sig'); texts[name] = text
        for number, line in enumerate(text.splitlines(), 1):
            if re.search(r'[\u3400-\u9fff\uf900-\ufaff\U00020000-\U000323af]', line):
                yield name, number, 'non-English documentation (Han characters)'
    known_anchors = {name: anchors(text) for name, text in texts.items()}
    for name, text in texts.items():
        fence = None
        for number, line in enumerate(text.splitlines(), 1):
            marker = re.match(r'^\s*(`{3,}|~{3,})', line)
            if marker:
                char = marker[1][0]
                fence = None if fence == char else char if fence is None else fence
                continue
            if fence:
                continue
            for match in re.finditer(r'!?\[[^]\n]*\]\(([^)\n]+)\)', line):
                target = match[1].strip()
                if target.startswith('<'):
                    target = target[1:target.index('>')]
                else:
                    target = target.split(' "', 1)[0]
                parts = urlsplit(target)
                if parts.scheme or parts.netloc or not target:
                    continue
                path = unquote(parts.path)
                # Absolute machine paths are historical local pointers, not repo URLs.
                if path.startswith('/') or re.match(r'^[A-Za-z]:', path):
                    continue
                resolved = (root / PurePosixPath(name).parent / path).resolve() if path else (root / name)
                try:
                    relative = resolved.relative_to(root.resolve()).as_posix()
                except ValueError:
                    yield name, number, 'link escapes repository: ' + target
                    continue
                if relative not in tracked and not any(p.startswith(relative.rstrip('/') + '/') for p in tracked):
                    yield name, number, 'missing target: ' + target
                elif parts.fragment and relative in known_anchors and unquote(parts.fragment) not in known_anchors[relative]:
                    yield name, number, 'missing heading: ' + target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--git', default='git', help='Git executable (default: PATH)')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    raw = subprocess.check_output([args.git, '-C', str(root), 'ls-files', '-z'])
    tracked = set(raw.decode('utf-8').strip('\0').split('\0'))
    found = list(problems(root, tracked))
    for name, number, issue in found:
        print(f'{name}:{number}: {issue}')
    count = sum(p.lower().endswith('.md') for p in tracked)
    print(f'Checked {count} tracked Markdown files; {len(found)} problems.')
    return bool(found)


if __name__ == '__main__':
    raise SystemExit(main())
