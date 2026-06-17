# fablize-for-hermes Quickstart

## Find the scripts path (automatic)

```bash
FABLIZE_ROOT=$(find ~/.hermes -name goals.py -path "*/fablize*" 2>/dev/null | head -1)
FABLIZE_ROOT=${FABLIZE_ROOT%/scripts/goals.py}
echo "fablize root: $FABLIZE_ROOT"
```

## Typical workflow

1. **Create a plan**
   ```bash
   python3 "$FABLIZE_ROOT/scripts/goals.py" create \
     --brief "Short description of the task" \
     --goal "step1::First verifiable objective" \
     --goal "step2::Second verifiable objective" \
     --goal "verify::Final verification story"
   ```

2. **Activate the first story**
   ```bash
   python3 "$FABLIZE_ROOT/scripts/goals.py" next
   ```

3. **Work the story** — produce evidence (run code, capture output, take screenshots).

4. **Checkpoint the story**
   ```bash
   python3 "$FABLIZE_ROOT/scripts/goals.py" checkpoint \
     --id G001 \
     --status complete \
     --evidence "What you actually did and observed"
   ```

5. **Repeat** `next` → work → `checkpoint` for each story.

6. **Final story** requires verification:
   ```bash
   python3 "$FABLIZE_ROOT/scripts/goals.py" checkpoint \
     --id G003 \
     --status complete \
     --evidence "Verification performed" \
     --verify-cmd "command you ran" \
     --verify-evidence "what the command showed"
   ```

## Resuming across sessions

```bash
python3 "$FABLIZE_ROOT/scripts/goals.py" status  # shows where you left off
python3 "$FABLIZE_ROOT/scripts/goals.py" next     # continue working
```
