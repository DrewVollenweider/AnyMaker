"""Index Ghidra's completed export and extract a small review file."""
import json, re
from pathlib import Path

root = Path(__file__).resolve().parent / 'output' / 'decompilation'
text = (root/'game-decompiled.c').read_text(encoding='utf-8')
log = (root/'exe-analysis.log').read_text(encoding='utf-8')
done = re.search(r'EXPORT COMPLETE: (\d+) decompiled; (\d+) functions visited', log)
if not done: raise ValueError('Export has not completed')
starts = list(re.finditer(r'^/\* ([0-9a-f]+) ([^\n]+) \*/$', text, re.M))
rows, excerpts = [], []
line, last_offset = 1, 0
terms = ('game.gcl', 'on_tick', 'VirtualAlloc(', 'VirtualProtect(', 'XInputGetState(', 'CreateFileW(', 'ReadFile(', 'WriteFile(')
for i, m in enumerate(starts):
    end = starts[i+1].start() if i+1 < len(starts) else len(text)
    code = text[m.end():end]
    matches = [t for t in terms if t in code]
    line += text.count('\n', last_offset, m.start()); last_offset = m.start()
    row = {'address': m[1], 'name': m[2], 'line': line,
           'characters': len(code), 'review_terms': matches}
    rows.append(row)
    if matches: excerpts.append((row, text[m.start():end]))
with (root/'exe-function-index.json').open('x', encoding='utf-8') as f:
    json.dump({'decompiled':int(done[1]), 'visited':int(done[2]), 'functions':rows}, f, indent=2)
with (root/'exe-review-excerpts.c').open('x', encoding='utf-8') as f:
    f.write('/* Selected static pseudocode; keyword matches are clues, not verified behavioral conclusions. */\n')
    for row, code in excerpts:
        f.write('\n/* REVIEW TERMS: '+', '.join(row['review_terms'])+' */\n'+code)
print(f'{done[1]} decompiled; {done[2]} visited; {len(excerpts)} review excerpts.')
for row, _ in excerpts:
    if 'game.gcl' in row['review_terms'] or 'on_tick' in row['review_terms']: print(row)
