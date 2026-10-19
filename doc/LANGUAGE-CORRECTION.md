# English documentation correction

2026-10-19. The user explicitly rejected the former instruction to record development/research in Chinese and authorized this correction on both main and the research branch. `AGENTS.md` now requires English for documentation, research records, development notes, code comments, commit messages, and user communication unless the user requests another language. Existing optional application localization is a separate feature.

The audit found Han characters in 32 of 57 tracked Markdown files on the research branch: the root instruction guide, README heading link, TODO, scratch requests, 19 numbered engineering documents, documentation/resource indexes, and seven whole-game research documents. All were translated, including historical failure records, unperformed-test labels, commands, identifiers, numeric limits, hashes, and evidence links. Main receives its 25 affected files; the seven research-only documents stay on the research branch. No research implementation or application build is merged into main.

The translation retains all 46 checked and 70 unchecked TODO entries. The two numeric literals formatted with thousands separators in AGENTS retain their original values. An automated comparison checked all original inline code literals and numeric tokens; technical references were restored where shorthand had obscured them. The preserved original commit remains available in Git history. Exact pretranslation bytes and working backups stay outside Git.

Machine-readable [provenance](evidence/documentation-language.json) records original blob identities and before/after SHA-256 for translated files. Hashes establish identity, not translation correctness. Existing evidence JSON had no Han strings and was not rewritten. Original binaries, assets, saves, and evidence records were unchanged.

## Maintenance command

```sh
python scripts/check-documentation.py
```

Use `--git PATH` for a Git executable outside PATH. The dependency-free checker scans tracked Markdown, including AGENTS, and validates repository-relative inline file/heading links. It skips remote URLs and fenced examples; it does not validate external URLs, every Markdown syntax extension, natural-language meaning, or game correctness. Expand missing Markdown in sparse checkouts before running it. Application localization/data and immutable historical commits are outside this documentation check.

This correction adds no deployment, release, gameplay input, runtime experiment, application behavior change, or revalidation of historical test outcomes. Historical tests remain explicitly dated; they were not rerun merely because their records were translated. The checker has been exercised with invalid-language, missing-file, missing-heading, valid-heading, and fenced-example controls.
