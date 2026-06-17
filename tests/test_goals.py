"""Tests for the fablize-for-hermes goal engine (scripts/goals.py).

Tests are functional: they run goals.py as a subprocess with a temporary
HERMES_FABLIZE_DIR to avoid polluting real state.
"""
import json
import os
import subprocess
import tempfile
from pathlib import Path

GOALS_PY = Path(__file__).resolve().parent.parent / "scripts" / "goals.py"


def _run(*args, env_override=None) -> subprocess.CompletedProcess:
    """Run goals.py with a fresh temp state dir. Returns CompletedProcess."""
    tmpdir = tempfile.mkdtemp()
    env = {**os.environ, "HERMES_FABLIZE_DIR": tmpdir}
    if env_override:
        env.update(env_override)
    result = subprocess.run(
        ["python3", str(GOALS_PY), *args],
        capture_output=True,
        text=True,
        env=env,
    )
    # Cleanup tmpdir after capture
    return result, tmpdir


def _cleanup(tmpdir: str):
    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------

class TestCreate:
    def test_create_single_goal(self):
        r, tmp = _run("create", "--brief", "test", "--goal", "a::do thing")
        assert r.returncode == 0
        assert "plan created" in r.stdout
        assert "G001" in r.stdout
        assert "a" in r.stdout

        state = Path(tmp) / "goals.json"
        assert state.exists()
        data = json.loads(state.read_text())
        assert len(data["goals"]) == 1
        assert data["goals"][0]["title"] == "a"
        assert data["goals"][0]["status"] == "pending"
        _cleanup(tmp)

    def test_create_multiple_goals(self):
        r, tmp = _run(
            "create", "--brief", "multi",
            "--goal", "one::first",
            "--goal", "two::second",
            "--goal", "three::third",
        )
        assert r.returncode == 0
        data = json.loads((Path(tmp) / "goals.json").read_text())
        assert len(data["goals"]) == 3
        assert data["goals"][0]["id"] == "G001"
        assert data["goals"][2]["id"] == "G003"
        _cleanup(tmp)

    def test_create_requires_goal(self):
        r, tmp = _run("create", "--brief", "empty")
        assert r.returncode != 0
        assert "at least one --goal" in r.stderr
        _cleanup(tmp)

    def test_create_requires_colon_format(self):
        r, tmp = _run("create", "--brief", "bad", "--goal", "no-colon")
        assert r.returncode != 0
        assert "format is" in r.stderr
        _cleanup(tmp)

    def test_create_refuses_overwrite_without_force(self):
        r, tmp = _run("create", "--brief", "first", "--goal", "a::alpha")
        assert r.returncode == 0
        r2, _ = _run("create", "--brief", "second", "--goal", "b::beta", env_override={"HERMES_FABLIZE_DIR": tmp})
        assert r2.returncode != 0
        assert "already exists" in r2.stderr
        _cleanup(tmp)

    def test_create_force_overwrite(self):
        r, tmp = _run("create", "--brief", "first", "--goal", "a::alpha")
        assert r.returncode == 0
        r2, _ = _run("create", "--brief", "second", "--goal", "b::beta", "--force", env_override={"HERMES_FABLIZE_DIR": tmp})
        assert r2.returncode == 0
        data = json.loads((Path(tmp) / "goals.json").read_text())
        assert data["brief"] == "second"
        _cleanup(tmp)


# ---------------------------------------------------------------------------
# next
# ---------------------------------------------------------------------------

class TestNext:
    def test_next_activates_first_pending(self):
        r, tmp = _run(
            "create", "--brief", "t", "--goal", "a::one", "--goal", "b::two",
        )
        assert r.returncode == 0
        r2, _ = _run("next", env_override={"HERMES_FABLIZE_DIR": tmp})
        assert r2.returncode == 0
        assert "handoff" in r2.stdout
        assert "G001" in r2.stdout
        data = json.loads((Path(tmp) / "goals.json").read_text())
        assert data["goals"][0]["status"] == "in_progress"
        assert data["goals"][1]["status"] == "pending"
        _cleanup(tmp)

    def test_next_resumes_active(self):
        r, tmp = _run(
            "create", "--brief", "t", "--goal", "a::one", "--goal", "b::two",
        )
        _run("next", env_override={"HERMES_FABLIZE_DIR": tmp})
        r2, _ = _run("next", env_override={"HERMES_FABLIZE_DIR": tmp})
        # Should still show G001 (already active), not advance
        assert "G001" in r2.stdout
        _cleanup(tmp)

    def test_next_says_done_when_all_complete(self):
        r, tmp = _run(
            "create", "--brief", "t", "--goal", "a::one", "--goal", "b::two",
        )
        _run("next", env_override={"HERMES_FABLIZE_DIR": tmp})
        # Complete G001 (not final, so no verify-cmd needed)
        _run(
            "checkpoint", "--id", "G001", "--status", "complete",
            "--evidence", "done", env_override={"HERMES_FABLIZE_DIR": tmp},
        )
        _run("next", env_override={"HERMES_FABLIZE_DIR": tmp})
        # Now G002 is active — complete it with verify gate
        _run(
            "checkpoint", "--id", "G002", "--status", "complete",
            "--evidence", "verified",
            "--verify-cmd", "echo ok",
            "--verify-evidence", "ok",
            env_override={"HERMES_FABLIZE_DIR": tmp},
        )
        r2, _ = _run("next", env_override={"HERMES_FABLIZE_DIR": tmp})
        assert "all stories complete" in r2.stdout
        _cleanup(tmp)


# ---------------------------------------------------------------------------
# checkpoint
# ---------------------------------------------------------------------------

class TestCheckpoint:
    def test_checkpoint_requires_active(self):
        r, tmp = _run(
            "create", "--brief", "t", "--goal", "a::one",
        )
        r2, _ = _run(
            "checkpoint", "--id", "G001", "--status", "complete",
            "--evidence", "done", env_override={"HERMES_FABLIZE_DIR": tmp},
        )
        assert r2.returncode != 0
        assert "not active" in r2.stderr
        _cleanup(tmp)

    def test_checkpoint_complete_requires_evidence(self):
        r, tmp = _run(
            "create", "--brief", "t", "--goal", "a::one",
        )
        _run("next", env_override={"HERMES_FABLIZE_DIR": tmp})
        r2, _ = _run(
            "checkpoint", "--id", "G001", "--status", "complete",
            "--evidence", "", env_override={"HERMES_FABLIZE_DIR": tmp},
        )
        assert r2.returncode != 0
        assert "non-empty --evidence" in r2.stderr
        _cleanup(tmp)

    def test_final_story_requires_verify_gate(self):
        r, tmp = _run(
            "create", "--brief", "t", "--goal", "a::only one",
        )
        _run("next", env_override={"HERMES_FABLIZE_DIR": tmp})
        r2, _ = _run(
            "checkpoint", "--id", "G001", "--status", "complete",
            "--evidence", "stuff", env_override={"HERMES_FABLIZE_DIR": tmp},
        )
        assert r2.returncode != 0
        assert "verify-cmd" in r2.stderr
        _cleanup(tmp)

    def test_checkpoint_updates_status(self):
        r, tmp = _run(
            "create", "--brief", "t", "--goal", "a::one",
        )
        _run("next", env_override={"HERMES_FABLIZE_DIR": tmp})
        r2, _ = _run(
            "checkpoint", "--id", "G001", "--status", "blocked",
            "--evidence", "stuck on X",
            env_override={"HERMES_FABLIZE_DIR": tmp},
        )
        assert r2.returncode == 0
        data = json.loads((Path(tmp) / "goals.json").read_text())
        assert data["goals"][0]["status"] == "blocked"
        _cleanup(tmp)

    def test_checkpoint_allows_failed_status(self):
        r, tmp = _run(
            "create", "--brief", "t", "--goal", "a::one",
        )
        _run("next", env_override={"HERMES_FABLIZE_DIR": tmp})
        r2, _ = _run(
            "checkpoint", "--id", "G001", "--status", "failed",
            "--evidence", "could not complete",
            env_override={"HERMES_FABLIZE_DIR": tmp},
        )
        assert r2.returncode == 0
        assert "failed" in r2.stdout
        _cleanup(tmp)

    def test_checkpoint_bad_id(self):
        r, tmp = _run(
            "create", "--brief", "t", "--goal", "a::one",
        )
        r2, _ = _run(
            "checkpoint", "--id", "G999", "--status", "complete",
            "--evidence", "x", env_override={"HERMES_FABLIZE_DIR": tmp},
        )
        assert r2.returncode != 0
        assert "not found" in r2.stderr
        _cleanup(tmp)


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

class TestStatus:
    def test_status_shows_progress(self):
        r, tmp = _run(
            "create", "--brief", "my task",
            "--goal", "a::one", "--goal", "b::two",
        )
        _run("next", env_override={"HERMES_FABLIZE_DIR": tmp})
        r2, _ = _run("status", env_override={"HERMES_FABLIZE_DIR": tmp})
        assert "0/2" in r2.stdout
        assert "▶ G001" in r2.stdout
        assert "· G002" in r2.stdout
        _cleanup(tmp)

    def test_status_no_plan(self):
        tmpdir = tempfile.mkdtemp()
        r = subprocess.run(
            ["python3", str(GOALS_PY), "status"],
            capture_output=True, text=True,
            env={**os.environ, "HERMES_FABLIZE_DIR": tmpdir},
        )
        assert r.returncode != 0
        assert "no plan" in r.stderr
        _cleanup(tmpdir)


# ---------------------------------------------------------------------------
# ledger
# ---------------------------------------------------------------------------

class TestLedger:
    def test_ledger_logs_events(self):
        r, tmp = _run(
            "create", "--brief", "t", "--goal", "a::one",
        )
        ledger = Path(tmp) / "ledger.jsonl"
        assert ledger.exists()
        lines = ledger.read_text().strip().split("\n")
        assert len(lines) >= 1
        assert json.loads(lines[0])["event"] == "plan_created"
        _cleanup(tmp)
