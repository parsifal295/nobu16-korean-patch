#!/usr/bin/env python3
"""No-pytest regression entrypoint for the PC-only canonical-title repair."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "canonical_title_repair", HERE / "build_translation_quality_msgev_pc_canonical_title_repair_v1.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load canonical title validator")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_canonical_title_repair_contract() -> None:
    result = MODULE.validate()
    assert result["status"] == "ok"
    assert result["candidate_count"] == 62
    assert result["superseded_temporary_candidate_id"] == 14638
    assert len(result["candidate_proofs"]) == 62
    assert all(proof["event_layout"]["proposal_within_current_budget"] for proof in result["candidate_proofs"])


def test_public_contract_is_source_free() -> None:
    contract = json.loads((HERE / "validation.v1.json").read_text(encoding="utf-8"))
    encoded = json.dumps(contract, ensure_ascii=True)
    assert '"translation"' not in encoded
    assert contract["scope"]["candidate_count"] == 62
    assert contract["write_scope"] == "none"


if __name__ == "__main__":
    test_canonical_title_repair_contract()
    test_public_contract_is_source_free()
    print("manual-tests: ok")
