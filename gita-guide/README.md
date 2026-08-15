# gita-guide

A [Claude Agent Skill](https://docs.claude.com/en/docs/claude-code/skills) that answers
questions about the **Bhagavad Gita** and **Vedanta** in the voice and framework of
**Swami Sarvapriyananda** (Vedanta Society of New York) — and cites the *exact* session
of his verse-by-verse Gita series where he covers the material.

## What it does

- Answers Gita/Vedanta questions grounded in Swami Sarvapriyananda's Advaita framework
  (see `references/vedanta-core.md`), not a generic summary.
- Cites the **exact video** for any chapter/verse, from a real, verse-by-verse index of
  his [Bhagavad Gita playlist](https://www.youtube.com/playlist?list=PL2imXor63HtS4ewIKryBL4ZVeiaH8Ij4R)
  (152+ sessions, Chapter 1 → Chapter 13 and growing).
- **Self-updating:** on each run it checks the playlist for new sessions and refreshes
  the index automatically (`scripts/update_index.py`).
- Falls back to broader search (his other Vedanta lectures, the web) when the series
  hasn't reached a chapter yet — honestly, without inventing citations.
- Answers in depth in chat by default, and can render a **light/dark HTML web page** or a
  shareable page on request.

## Install

Copy the `gita-guide/` folder into your skills directory:

```bash
# Claude Code (personal skills)
cp -r gita-guide ~/.claude/skills/

# or a project's skills
cp -r gita-guide /path/to/project/.claude/skills/
```

Then just ask a Gita or Vedanta question — e.g. *"What does Krishna mean by acting without
attachment to results?"* or *"Explain Gita 2.47"* — and the skill triggers automatically.
Ask for *"a page I can share"* to get the HTML version.

## Layout

```
gita-guide/
├── SKILL.md                     # instructions + triggering description
├── references/
│   ├── vedanta-core.md          # Swami Sarvapriyananda's framework, vocabulary, analogies
│   ├── gita-video-index.md      # verse-by-verse session map (human-readable)
│   └── gita-video-index.json    # same data, for the scripts
├── scripts/
│   ├── find_session.py          # look up the session covering a chapter/verse
│   └── update_index.py          # refresh the index from the live playlist
└── assets/
    └── answer-template.html     # light/dark web-page template
```

## Requirements

Python 3 (standard library only — no packages to install). Network access is used only to
refresh the playlist index; everything else works offline.

## A note on fidelity

This skill represents Swami Sarvapriyananda's teaching and the Advaita Vedanta tradition as
faithfully as it can, and points you to his own words on video. It's offered as his
perspective and the tradition's — not as authoritative religious ruling, and not as medical
or psychological advice.
