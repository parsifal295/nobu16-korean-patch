#!/usr/bin/env python3
"""Targeted regression tests for selector-1126 closure and ledger delta."""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PK_AUDIT = REPO / "workstreams" / "pk_msggame_runtime_vm_audit_v1"
CLOSURE_BUILDER = (
    PK_AUDIT / "build_pk_selector1126_consolidated_closure_v1.py"
)
CHECKPOINT_BUILDER = (
    WORKSTREAM
    / "build_runtime_vm_post_selector1126_consolidated_checkpoint_v1.py"
)
PROGRESS_BUILDER = (
    WORKSTREAM / "build_progress_post_selector1126_consolidated_delta_v1.py"
)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


C = load_module(CLOSURE_BUILDER, "selector1126_closure_tested")
K = load_module(CHECKPOINT_BUILDER, "selector1126_checkpoint_tested")
P = load_module(PROGRESS_BUILDER, "selector1126_progress_tested")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="ascii"))


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]


def test_all_builders_check() -> None:
    expected = {
        CLOSURE_BUILDER: (
            '"coordinate_union_rows": 185',
            '"pending_after": 6761',
        ),
        CHECKPOINT_BUILDER: (
            "promoted=118 pending=6761",
            "full_integration_rebuild=false steam_write=false",
        ),
        PROGRESS_BUILDER: (
            "promoted=118 pending=6761",
            "full_dialogue_rebuild=false steam_write=false",
        ),
    }
    for builder, needles in expected.items():
        result = subprocess.run(
            [sys.executable, str(builder), "--check"],
            cwd=REPO,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert result.returncode == 0, result.stderr
        assert all(needle in result.stdout for needle in needles)


def test_closure_union_permutations_and_lineage() -> None:
    owner_rows = [
        load_jsonl(path)
        for path in C.CHUNK_DECISIONS
    ]
    owner_maps = [
        {row["coordinate"]: row["reviewed_translation"] for row in rows}
        for rows in owner_rows
    ]
    assert [len(rows) for rows in owner_rows] == [65, 49, 71]
    assert all(
        not set(owner_maps[left]) & set(owner_maps[right])
        for left in range(3)
        for right in range(left + 1, 3)
    )
    unions = []
    for order in itertools.permutations(range(3)):
        resolved = {}
        for owner in order:
            resolved.update(owner_maps[owner])
        unions.append(resolved)
    assert len(unions) == 6
    assert all(value == unions[0] for value in unions[1:])
    assert len(unions[0]) == 185
    decisions = load_jsonl(C.PRIVATE_DECISIONS_OUTPUT)
    assert len(decisions) == 185
    actions = Counter(
        row["selector1126_consolidated_update_action"] for row in decisions
    )
    assert dict(actions) == C.EXPECTED_ACTION_COUNTS
    coverage = load_json(C.PUBLIC_COVERAGE_OUTPUT)
    assert coverage["result"]["reviewed_sites"] == 114
    assert coverage["result"]["source_only_sites"] == 14
    assert coverage["result"]["source_only_actions"] == 0
    assert coverage["result"]["predecessor_overlaps"] == 1
    assert coverage["result"]["predecessor_supersessions"] == 1
    assert coverage["proof"]["all_owner_permutations_identical"]
    assert coverage["proof"]["reverse_overlay_exact"]
    assert coverage["candidate"] == {
        "official_predecessor_sha256": C.EXPECTED_OFFICIAL_CANDIDATE_SHA256,
        "reviewed_sha256": C.EXPECTED_FINAL_CANDIDATE_SHA256,
        "reverse_overlay_sha256": C.EXPECTED_OFFICIAL_CANDIDATE_SHA256,
    }


def test_frozen_hashes_and_tamper_rejection() -> None:
    expected = {
        C.PRIVATE_DECISIONS_OUTPUT:
            C.EXPECTED_OUTPUT_SHA256["private_decisions"],
        C.PRIVATE_EVIDENCE_OUTPUT:
            C.EXPECTED_OUTPUT_SHA256["private_evidence"],
        C.PUBLIC_COVERAGE_OUTPUT:
            C.EXPECTED_OUTPUT_SHA256["public_coverage"],
        C.PUBLIC_PROMOTION_OUTPUT:
            C.EXPECTED_OUTPUT_SHA256["public_promotion"],
        K.DEFAULT_PRIVATE_OUTPUT: K.EXPECTED_PRIVATE_OUTPUT_SHA256,
        K.DEFAULT_PUBLIC_OUTPUT: K.EXPECTED_PUBLIC_OUTPUT_SHA256,
        P.DEFAULT_PREDECESSOR_PROGRESS:
            P.EXPECTED_PREDECESSOR_PROGRESS_SHA256,
        P.DEFAULT_PROGRESS_OUTPUT: P.EXPECTED_PROGRESS_OUTPUT_SHA256,
        P.IMMUTABLE_PROGRESS_OUTPUT: P.EXPECTED_PROGRESS_OUTPUT_SHA256,
    }
    assert all(sha256_file(path) == digest for path, digest in expected.items())
    original = K.CLOSURE_DECISIONS_PATH
    with tempfile.TemporaryDirectory() as temp_dir:
        tampered = Path(temp_dir) / "tampered.jsonl"
        rows = original.read_text(encoding="utf-8").splitlines()
        first = json.loads(rows[0])
        first["runtime_review"] = "pending"
        rows[0] = json.dumps(first, ensure_ascii=False, sort_keys=True)
        tampered.write_text("\n".join(rows) + "\n", encoding="utf-8")
        K.configure_base()
        K.BASE.CLOSURE_DECISIONS_PATH = tampered
        try:
            K.BASE.load_closure_decisions()
        except Exception:
            pass
        else:
            raise AssertionError("tampered closure decision was accepted")
        finally:
            K.BASE.CLOSURE_DECISIONS_PATH = original


def test_targeted_checkpoint_raw_copy_and_progress() -> None:
    predecessor = K.PREDECESSOR_PRIVATE_PATH.read_bytes().splitlines(
        keepends=True
    )
    current = K.DEFAULT_PRIVATE_OUTPUT.read_bytes().splitlines(keepends=True)
    assert len(predecessor) == len(current) == 52_803
    changed = [
        index
        for index, pair in enumerate(zip(predecessor, current))
        if pair[0] != pair[1]
    ]
    assert len(changed) == 185
    assert 52_803 - len(changed) == 52_618
    report = load_json(K.DEFAULT_PUBLIC_OUTPUT)
    assert report["validation"]["full_integration_engine_invoked"] is False
    assert report["result"]["runtime_review_pending"] == 6_761
    assert report["result"]["fully_candidate_eligible"] == 46_042
    assert report["result"]["promoted_total"] == 29_573
    assert report["result"]["pk_msggame_promotion_count"] == 13_922
    progress = load_json(P.DEFAULT_PROGRESS_OUTPUT)
    totals = progress["totals"]
    scope = totals["scope_classification_counts"]
    assert totals["runtime_review_pending"] == 6_761
    assert totals["fully_candidate_eligible"] == 46_042
    assert scope["retranslated"] == 45_697
    assert scope["confirmed_non_display"] == 345
    integration = progress["runtime_vm_integration"]
    assert integration["selector748_consolidated_layer_included"] is True
    assert integration["selector1126_consolidated_layer_included"] is True
    assert integration["selector1126_targeted_progress_delta"][
        "full_dialogue_rebuild_performed"
    ] is False


def test_tracked_artifacts_are_source_free() -> None:
    cjk = re.compile(
        r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
        r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
    )
    coordinate = re.compile(r"\b\d+:\d+(?::\d+){0,2}\b")
    tracked = (
        CLOSURE_BUILDER,
        CHECKPOINT_BUILDER,
        PROGRESS_BUILDER,
        SCRIPT,
        C.PUBLIC_COVERAGE_OUTPUT,
        C.PUBLIC_PROMOTION_OUTPUT,
        K.DEFAULT_PUBLIC_OUTPUT,
        P.DEFAULT_PREDECESSOR_PROGRESS,
        P.DEFAULT_PROGRESS_OUTPUT,
        P.IMMUTABLE_PROGRESS_OUTPUT,
    )
    for path in tracked:
        content = path.read_text(encoding="utf-8")
        assert cjk.search(content) is None
        if path not in (
            P.DEFAULT_PREDECESSOR_PROGRESS,
            P.DEFAULT_PROGRESS_OUTPUT,
            P.IMMUTABLE_PROGRESS_OUTPUT,
        ):
            assert coordinate.search(content) is None
    for path in (
        C.PUBLIC_COVERAGE_OUTPUT,
        C.PUBLIC_PROMOTION_OUTPUT,
        K.DEFAULT_PUBLIC_OUTPUT,
        P.DEFAULT_PREDECESSOR_PROGRESS,
        P.DEFAULT_PROGRESS_OUTPUT,
        P.IMMUTABLE_PROGRESS_OUTPUT,
    ):
        content = path.read_text(encoding="ascii")
        assert '"reviewed_translation"' not in content


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
