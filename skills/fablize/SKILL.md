---
name: fablize
description: >
  A harness that makes any model see a task through to the end — with evidence and
  verification — as procedure, not as luck. Enforces verification grounding (run & observe
  artifacts before declaring done), multi-story decomposition with an evidence gate,
  a systematic investigation protocol, and early-stop prevention. Also available as a
  standalone project at https://github.com/fivetaku/fablize.
trigger: >
  Use when starting multi-step work (2+ sequential phases), debugging or root-cause
  investigation, building render/executable artifacts (HTML, SVG, games, charts, UIs),
  or when the user says "fablize", "see it through", "verify as you go",
  "split into goals".
---

# fablize — run like Fable

> **Principle:** a harness cannot raise a model's ceiling. It makes the model go all
> the way to its own ceiling — by enforcing verification, completion, and investigation
> as procedure. When the capability ceiling is the blocker (open-ended creative detail,
> self-driven discovery), escalate.
>
> **Apply only what the task signals** (smallest matching discipline; overlap only when
> genuinely multi-category).

## Foundation rules (always apply)

- **Lead with the outcome.** State what you're doing before you do it. Stay within
  requested scope — no incidental refactors, no scope creep.
- **Ground every completion claim** in a tool result from this session. "I wrote the
  file" is not completion — "I wrote the file and ran it, and here's the output" is.
- **Never end a turn by stating intent to do work without doing it.** If you catch
  yourself writing "I will now create X" or "Next, I'll implement Y", stop and make
  the tool call immediately. A turn that ends with a promise and no tool call is an
  early stop — re-engage yourself.
- **Confirm before destructive or hard-to-reverse actions** (deleting files, force-push,
  modifying production config).

---

## 1. Multi-story loop (2+ sequential stories)

Decompose the task into sequential stories and complete one at a time, producing
evidence as you go. Self-contained — no external system required. State persists in
`$HERMES_FABLIZE_DIR` (default: `~/.hermes/fablize/`) and survives session death;
resume with `goals.py status`.

**First-time use:** See `references/workflow-quickstart.md` for exact copy-pasteable
commands with the correct script path.

```bash
# Locate goals.py on this machine
FABLIZE_ROOT=$(find ~/.hermes -name goals.py -path "*/fablize*" 2>/dev/null | head -1)
FABLIZE_ROOT=${FABLIZE_ROOT%/scripts/goals.py}

# Create a plan
python3 "$FABLIZE_ROOT/scripts/goals.py" create --brief "<summary>" \
  --goal "title::verifiable objective" --goal "title::..."
  # The last goal must be a verification story
python3 "$FABLIZE_ROOT/scripts/goals.py" next         # activate a story + handoff
# ... work that story only ...
python3 "$FABLIZE_ROOT/scripts/goals.py" checkpoint --id G001 --status complete --evidence "<concrete evidence>"
# The final story is a verification gate:
# --verify-cmd "<command>" --verify-evidence "<result>" are REQUIRED
python3 "$FABLIZE_ROOT/scripts/goals.py" status       # first command when resuming
```

**Rules:**
- `complete` requires non-empty evidence (the engine refuses empty evidence)
- The **final goal** cannot complete without a verify command and its result (verification gate)
- If blocked, record `--status blocked` and report why
- Single-step tasks skip this loop entirely

---

## 2. Deep investigation (debugging / unknown cause / review)

When debugging, follow this discipline (also available at `references/investigation-protocol.txt`):

1. **Reproduce first.** Run the failing case and read the actual output before forming
   any hypothesis.
2. **Develop several competing hypotheses** — at least three — before investigating
   any single one. A symptom that pattern-matches to a known failure may have a different
   cause.
3. **For each hypothesis**, identify what evidence would confirm or refute it, then
   gather that evidence by reading the relevant code paths end to end. Track your
   confidence per hypothesis as evidence accumulates.
4. **Trace the full causal chain.** Do not stop at the first plausible cause: ask
   what *allowed* that cause to produce this symptom, and whether removing only the
   visible trigger would leave the defect latent. A fix that makes the test pass is
   not necessarily a fix that removes the defect.
5. **Verify before and after.** Confirm the root cause with evidence before changing
   code. After the fix, demonstrate that the failure mode itself is gone — not merely
   that the triggering condition no longer occurs in this environment.
6. **In your report**, state the hypotheses you rejected and the evidence that rejected
   them.

---

## 3. Verification grounding (render/executable artifacts — always)

For artifacts whose correctness only shows when run — HTML, SVG, games, UI, charts,
animations, scripts with observable output — do not stop at writing the file. Run it
in its natural execution environment and observe the actual output.

**The grounding loop, before completion:**

1. **RUN IT** in the real renderer. For web artifacts: headless browser (Playwright,
   Chrome `--headless --screenshot`), or serve and navigate. For SVG: render to PNG.
   For scripts: execute and capture stdout/stderr. For animations/games: drive it far
   enough that motion/state actually starts.
2. **OBSERVE THE OUTPUT.** Read the screenshot. Read the console for errors. Look at
   what actually rendered — layout intact? Anything obscured? Runtime errors a static
   check can't see? A produced-but-unobserved screenshot is not observation.
3. **FIX WHAT THE OBSERVATION REVEALS**, then re-run. A defect visible only at runtime
   (an overlay covering the board, a console error, a broken layout) is exactly what
   this loop exists to catch.
4. **Stop when you have actually looked and it's clean.** One clean render is enough.
   Do not re-render the same unchanged state to accumulate confidence. Re-render only
   after you change something.

A static parse (`xmllint`, `node --check`, `HTMLParser`) confirms the file is
**well-formed** — it does **not** confirm the artifact looks or behaves correctly.

Pure text, prose, configuration, or plain logic with its own test suite does not need
rendering — the relevant grounding is running the tests, which you already do.

---

## 4. At the capability ceiling (escalate)

Signals you have hit the model's ceiling:
- Stuck on the same problem 2+ times
- Open-ended creation where detail itself is the value
- Deep review that needs out-of-spec discovery

These are **capability**, not procedure, and a harness cannot fill them.

1. **Adaptive thinking** already scales with difficulty — if the model has an effort
   or thinking mode, recommend increasing it.
2. If still short, **hand off to a stronger model** in a fresh session with an evidence
   package (symptoms, attempts, failure point, repro steps).
3. Otherwise **report the limit honestly** and name where a human must step in.
