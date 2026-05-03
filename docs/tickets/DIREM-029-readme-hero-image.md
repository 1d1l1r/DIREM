# DIREM-029 — README Hero Image

## Status
Ready for implementation

## Workstream
Docs

## Purpose

Add the intended README hero image as a tracked repository asset.

## Scope

- add one README hero image under `docs/assets/`;
- render it at the top of `README.md`;
- do not commit unrelated images or drafts;
- do not change product code.

## Acceptance

- README shows the hero image on GitHub.
- Asset path is relative and stable.
- Only intended image asset is committed.
- No old `images/` folder is committed.
- No code changes.

## Checks

```bash
git status
git diff
```
