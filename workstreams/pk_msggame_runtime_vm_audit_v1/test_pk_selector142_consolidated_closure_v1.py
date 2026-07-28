#!/usr/bin/env python3
"""Targeted regressions for the selector-142 consolidated closure."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BUILDER_PATH = WORKSTREAM / "build_pk_selector142_consolidated_closure_v1.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "selector142_closure_tested", BUILDER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_builder()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="ascii"))


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def test_builder_check() -> None:
    result = subprocess.run(
        [sys.executable, str(BUILDER_PATH), "--check"],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "coordinate_union_rows": 162,
        "owner_decision_rows": 162,
        "pending_after": 6645,
        "promotions": 116,
        "source_only_actions": 0,
        "status": "PASS",
        "steam_write_performed": False,
    }


def test_frozen_output_hashes() -> None:
    expected = {
        B.PRIVATE_DECISIONS_OUTPUT: B.EXPECTED_OUTPUT_SHA256[
            "private_decisions"
        ],
        B.PRIVATE_EVIDENCE_OUTPUT: B.EXPECTED_OUTPUT_SHA256[
            "private_evidence"
        ],
        B.PUBLIC_COVERAGE_OUTPUT: B.EXPECTED_OUTPUT_SHA256[
            "public_coverage"
        ],
        B.PUBLIC_PROMOTION_OUTPUT: B.EXPECTED_OUTPUT_SHA256[
            "public_promotion"
        ],
    }
    assert all(sha256_file(path) == digest for path, digest in expected.items())


def test_effective_union_is_disjoint() -> None:
    rows = load_jsonl(B.PRIVATE_DECISIONS_OUTPUT)
    assert len(rows) == 162
    assert len({row["coordinate"] for row in rows}) == 162
    actions = Counter(
        row["selector142_consolidated_update_action"] for row in rows
    )
    assert dict(actions) == B.EXPECTED_ACTION_COUNTS
    evidence = load_json(B.PRIVATE_EVIDENCE_OUTPUT)
    assert evidence["counts"]["owner_decision_rows"] == 162
    assert evidence["counts"]["coordinate_union_rows"] == 162
    assert evidence["counts"]["owner_overlaps"] == 0
    assert evidence["proof"]["chunk_coordinate_and_root_sets_disjoint"]


def test_promotion_and_pending_delta() -> None:
    result = load_json(B.PUBLIC_PROMOTION_OUTPUT)["result"]
    assert result["promotions"] == 116
    assert result["owner_renewals"] == 46
    assert result["owner_overrides"] == 101
    assert result["effective_renewals"] == 46
    assert result["effective_overrides"] == 101
    assert result["pending_before"] == 6761
    assert result["pending_after"] == 6645


def test_candidate_reverse_and_runtime_guards() -> None:
    coverage = load_json(B.PUBLIC_COVERAGE_OUTPUT)
    assert coverage["candidate"] == {
        "official_predecessor_sha256": B.EXPECTED_OFFICIAL_CANDIDATE_SHA256,
        "reviewed_sha256": B.EXPECTED_OUTPUT_SHA256["final_candidate"],
        "reverse_overlay_sha256": B.EXPECTED_OFFICIAL_CANDIDATE_SHA256,
    }
    proof = coverage["proof"]
    assert proof["all_owner_permutations_identical"]
    assert proof["record_control_gaps_preserved"]
    assert proof["protected_runtime_tokens_preserved"]
    assert proof["reverse_overlay_exact"]
    assert coverage["result"]["predecessor_overlaps"] == 0
    assert coverage["result"]["predecessor_supersessions"] == 0


def test_site_and_source_only_proof() -> None:
    coverage = load_json(B.PUBLIC_COVERAGE_OUTPUT)
    assert coverage["result"]["reviewed_sites"] == 109
    assert coverage["result"]["source_call_sites"] == 115
    assert coverage["result"]["source_only_sites"] == 6
    assert coverage["result"]["source_only_actions"] == 0
    assert (
        coverage["guards"]["source_only_proof_sha256"]
        == B.EXPECTED_OUTPUT_SHA256["source_only_proof"]
    )


def test_non_display_rows_are_not_coerced() -> None:
    predecessors = {
        (row["resource"], row["coordinate"]): row
        for row in load_jsonl(B.OFFICIAL_LEDGER_PATH)
    }
    for row in load_jsonl(B.PRIVATE_DECISIONS_OUTPUT):
        predecessor = predecessors[(row["resource"], row["coordinate"])]
        expected = (
            "pending"
            if "runtime_promotion"
            in row["selector142_consolidated_update_action"]
            else "verified"
        )
        assert predecessor["runtime_review"] == expected
        assert predecessor["scope_classification"] != "confirmed_non_display"


def test_public_artifacts_are_source_free() -> None:
    tracked = (
        BUILDER_PATH,
        SCRIPT,
        B.PUBLIC_COVERAGE_OUTPUT,
        B.PUBLIC_PROMOTION_OUTPUT,
    )
    cjk = re.compile(
        r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
        r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
    )
    coordinate = re.compile(r"\b\d+:\d+(?::\d+){0,2}\b")
    for path in tracked:
        content = path.read_text(encoding="utf-8")
        assert cjk.search(content) is None
        assert coordinate.search(content) is None
    for path in (B.PUBLIC_COVERAGE_OUTPUT, B.PUBLIC_PROMOTION_OUTPUT):
        content = path.read_text(encoding="ascii")
        assert '"translation"' not in content
        assert '"reviewed_translation"' not in content


def test_steam_was_not_written() -> None:
    steam = B.BASE.RANKING.DEFAULT_STEAM_ROOT / "MSG_PK/JP/msggame.bin"
    assert sha256_file(steam) == B.BASE.EXPECTED_CURRENT_SHA256
    assert load_json(B.PUBLIC_COVERAGE_OUTPUT)["steam_write_performed"] is False
    assert load_json(B.PUBLIC_PROMOTION_OUTPUT)["steam_write_performed"] is False


def main() -> int:
    tests = [
        value
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
