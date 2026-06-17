<p align="center">
  <a href="README.md"><strong>English</strong></a> ·
  <a href="README.zh.md">简体中文</a> ·
  <a href="README.pt.md">Português (BR)</a>
</p>

# fablize-for-hermes — run like Fable, on Hermes Agent
![Banner](banner.png)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)



A port of [fablize](https://github.com/fivetaku/fablize) for the [Hermes Agent](https://hermes-agent.nousresearch.com/)
ecosystem. This project adapts fablize's verified procedures — verification grounding,
multi-story evidence gating, investigation protocol, and early-stop prevention — from
Claude Code's plugin system to Hermes Agent's skill system.

**fablize** makes any agent **see a task through to the end — with evidence and
verification — as procedure, not as luck.**

## The origin

[fablize](https://github.com/fivetaku/fablize) was born from a controlled comparison
of Claude Opus and "Fable 5" (19 A/B runs + 26 real sessions, ~1,500 tool calls).
The finding: on closed, answer-bearing work (code, logic, builds) the two models
were effectively tied. The gap was in *depth* — following an implication one step
further — and that turned out to be **model capability**, not injectable.

But the **procedure** of good work — actually running what you build, decomposing
multi-step tasks with evidence checkpoints, investigating bugs systematically —
*does transfer*. fablize ships only the procedures whose effect was verified.

## What transfers and what doesn't

| Trait | Transferable? | How fablize-for-hermes does it |
|---|---|---|
| Verification grounding (run & observe the artifact) | ✅ | Skill section 3 — run in real renderer, observe output, fix, re-run |
| Multi-story completion + evidence gate | ✅ | `scripts/goals.py` — decompose, checkpoint, refuse completion without proof |
| Systematic investigation (reproduce → hypotheses → causal chain) | ✅ | Skill section 2 + `packs/investigation-protocol.txt` |
| Early-stop prevention | ✅ | Skill foundation rule: no promises without tool calls |
| Out-of-spec defect discovery | ❌ not possible | Capability — the model finds it, or it doesn't |
| Open-ended creative detail | ❌ not possible | Capability — shows only where there is no fixed answer |
| Self-driven propagation depth | ❌ not possible | Capability — directed propagation transfers; self-started depth does not |

## What's included

### 1. Hermes Agent skill (`skills/fablize/SKILL.md`)

The core behavioral ruleset, structured as a Hermes Agent skill (YAML frontmatter +
markdown). Covers:

- **Foundation rules** — always-on: lead with outcome, ground claims in tool results,
  no early stops, confirm destructive actions
- **Multi-story loop** — decompose 2+ story tasks → complete with evidence →
  verification gate on the final story
- **Deep investigation** — reproduce → 3+ competing hypotheses → trace causal chain →
  verify before/after → report rejected hypotheses
- **Verification grounding** — run render/executable artifacts, observe, fix, re-run
  before declaring done
- **Capability ceiling** — escalate honestly when the model's ceiling is the blocker

### 2. Goal engine (`scripts/goals.py`)

A self-contained, stdlib-only Python script for multi-story decomposition with a
verification gate. State persists in `~/.hermes/fablize/` and survives session death.

```bash
goals.py create --brief "Build a dashboard" \
  --goal "design::Create the HTML layout" \
  --goal "implement::Add chart visualizations" \
  --goal "verify::Run and verify the dashboard renders correctly"
goals.py next
# ... work this story ...
goals.py checkpoint --id G001 --status complete --evidence "Layout created with sidebar and main panel"
goals.py status
```

### 3. Packs — contextual discipline files

- **`packs/verification-grounding-pack.txt`** — The grounding loop: run, observe,
  fix, re-run. For HTML, SVG, games, UI, charts, animations.
- **`packs/investigation-protocol.txt`** — The systematic debugging protocol:
  reproduce, competing hypotheses, causal chain, verify before/after.

### 4. Setup scripts (`setup/`)

- `setup.sh [--skill-only|--local|--global]` — Install the skill into Hermes and
  optionally inject the operating block into `AGENTS.md` or `CLAUDE.md`
- `uninstall.sh [--skill-only|--local|--global|--all]` — Reverse the setup

## Differences from original fablize

| Aspect | fablize (original) | fablize-for-hermes |
|---|---|---|
| Platform | Claude Code plugin | Hermes Agent skill |
| Routing | `UserPromptSubmit` hook via `hooks.json` | Skill content — agent loads and applies matching discipline |
| Early-stop | `finish-the-work.sh` Stop hook (JSON transcript) | Foundation rule in skill — agent self-enforces |
| State dir | `./.fablize/` (per-project) | `~/.hermes/fablize/` (Hermes-wide, survives sessions) |
| Scripts | In `scripts/` — run from repo root | Same scripts, adapted for Hermes paths |
| Setup | Injects into `CLAUDE.md` | Installs as Hermes skill + optionally injects block |

## Install

### Quick install (skill only)

```bash
git clone https://github.com/zeus/fablize-for-hermes.git
cd fablize-for-hermes
bash setup/setup.sh --skill-only
```

Then load the skill in your Hermes session:

```
skill_view(name='fablize')
```

### Full install (skill + always-on block)

```bash
bash setup/setup.sh --local    # injects block into ./AGENTS.md
bash setup/setup.sh --global   # injects block into ~/.claude/CLAUDE.md
```

### Uninstall

```bash
bash setup/uninstall.sh --all
```

## How it behaves

- **Trigger:** load the `fablize` skill, or trigger inline when the agent detects
  2+ stories, debugging, or render artifacts
- **2+ stories** → decompose + verification gate via `goals.py`
- **Debugging** → investigation protocol (reproduce → hypotheses → causal chain)
- **Render artifact** → verification grounding (run → observe → fix → re-run)
- **Hard task** → adaptive thinking + escalate to stronger model if stuck
- **Capability ceiling** → escalate honestly (the harness does not fake capability)

## Honest limits

- It cannot raise model capability. Open-ended creative quality and self-driven
  discovery are out of reach — that is a model-choice decision, not a harness one.
- The effect numbers come from the original fablize small-family self-measurement.
  The direction is solid; the decimals are not asserted.
- The early-stop rule relies on agent self-enforcement, not a deterministic hook.
  It is a guideline, not a guard.

## License

MIT — same as the original fablize. The upstream fablize by fivetaku is MIT licensed.
This port adapts the design and procedures to the Hermes Agent ecosystem.
