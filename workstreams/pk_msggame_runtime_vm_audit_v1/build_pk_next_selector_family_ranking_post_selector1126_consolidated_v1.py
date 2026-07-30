#!/usr/bin/env python3
"""Rank remaining PK selector families on the selector-1126 checkpoint.

The graph walk is inherited from the frozen post-selector748 ranking
implementation, but every mutable audit constant is rebound to the immutable
selector-1126 targeted delta checkpoint. Older artifacts and mutable progress
aliases are neither read nor rewritten.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
PREDECESSOR_BUILDER = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_selector748_consolidated_v1.py"
)
DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector1126_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "runtime_vm_integration."
    "post_selector1126_consolidated_checkpoint.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector1126_consolidated.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector1126_consolidated.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector1126-consolidated.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector1126-consolidated-source-free.v1"
)
METHOD = (
    "selector1126_checkpoint_pending_reachable_0143_"
    "seven_way_selector_ranking"
)
OWNED_SELECTORS = (538, 568, 1096, 1174, 610, 550, 748, 1126)

EXPECTED_LEDGER_SHA256 = (
    "3198DC9F7A06809636D0C43F5740A65B5D4C50E7226D53AA7C52B7D893EFA06E"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256 = (
    "BD38D0EE71B59ADFEB8146760B91E82A7E09604E17B770760F13C94CB32704A5"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "B25D15DB919FC4E3CF3A68E7C10938F581C233F04DA111F1C8D0ECA0A3F86D62"
)
EXPECTED_PK_PENDING_ROWS = 6_761
EXPECTED_PK_PENDING_ROOTS = 4_288
EXPECTED_PK_PENDING_ROOT_SHA256 = (
    "3F2349644ADE00A928655E04B3B5E4AB57BD74E94D99F855C0139914BCB104BA"
)
EXPECTED_REACHABLE_CALL_TARGETS = 157
EXPECTED_OWNED_CALL_TARGETS = 9
EXPECTED_NON_SEVEN_WAY_TARGETS = 26
EXPECTED_ELIGIBLE_FAMILIES = 122
EXPECTED_ELIGIBLE_UNION_ROWS = 1_557
EXPECTED_ELIGIBLE_UNION_SHA256 = (
    "ED6B1DD71E4DE2375075138ED8C8E7DD743E4452E35984092404ED0D9D40269B"
)
EXPECTED_RECOMMENDED_SELECTOR = "0:142"
EXPECTED_RECOMMENDED_TERMINALS = tuple(
    f"0:{record_id}" for record_id in range(1440, 1447)
)
EXPECTED_RECOMMENDED_PENDING_ROWS = 118
EXPECTED_RECOMMENDED_PENDING_ROOTS = 56
EXPECTED_RECOMMENDED_PENDING_SITES = 56
EXPECTED_RECOMMENDED_CANDIDATE_SITES = 109
EXPECTED_RECOMMENDED_SOURCE_SITES = 115
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES = 6
EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES = 0

COMPARABLE_ACTUAL_PROMOTIONS = {
    568: 225,
    1096: 206,
    1174: 197,
    610: 167,
    550: 121,
    748: 101,
    1126: 118,
}
COMPARABLE_PENDING_UPPER_BOUNDS = {
    568: 331,
    1096: 247,
    1174: 224,
    610: 192,
    550: 171,
    748: 162,
    1126: 141,
}
EXPECTED_POINT_ESTIMATE = 91
EXPECTED_ESTIMATE_RANGE = (74, 104)

# Frozen after the first reproducible write/check cycle.
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "25976376FD87090644DD399A40A92114C7BB55CA8146C60AF2C0286746F0B2E6"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "7B56C40AB130AB879049D35B42DA13A6C676C34C5C8BD3865280DB5CA823ED03"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREDECESSOR_WRAPPER = load_module(
    PREDECESSOR_BUILDER,
    "pk_next_selector_post_1126_predecessor_helpers_v1",
)
RANKING = PREDECESSOR_WRAPPER.RANKING

for _name in (
    "DEFAULT_STEAM_ROOT",
    "DEFAULT_LEDGER",
    "CHECKPOINT_PUBLIC",
    "DEFAULT_PRIVATE_OUTPUT",
    "DEFAULT_PUBLIC_OUTPUT",
    "PRIVATE_SCHEMA",
    "PUBLIC_SCHEMA",
    "METHOD",
    "OWNED_SELECTORS",
    "EXPECTED_LEDGER_SHA256",
    "EXPECTED_CHECKPOINT_PUBLIC_SHA256",
    "EXPECTED_PK_CANDIDATE_SHA256",
    "EXPECTED_PK_PENDING_ROWS",
    "EXPECTED_PK_PENDING_ROOTS",
    "EXPECTED_PK_PENDING_ROOT_SHA256",
    "EXPECTED_REACHABLE_CALL_TARGETS",
    "EXPECTED_OWNED_CALL_TARGETS",
    "EXPECTED_NON_SEVEN_WAY_TARGETS",
    "EXPECTED_ELIGIBLE_FAMILIES",
    "EXPECTED_ELIGIBLE_UNION_ROWS",
    "EXPECTED_ELIGIBLE_UNION_SHA256",
    "EXPECTED_RECOMMENDED_SELECTOR",
    "EXPECTED_RECOMMENDED_TERMINALS",
    "EXPECTED_RECOMMENDED_PENDING_ROWS",
    "EXPECTED_RECOMMENDED_PENDING_ROOTS",
    "EXPECTED_RECOMMENDED_PENDING_SITES",
    "EXPECTED_RECOMMENDED_CANDIDATE_SITES",
    "EXPECTED_RECOMMENDED_SOURCE_SITES",
    "EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES",
    "EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES",
    "COMPARABLE_ACTUAL_PROMOTIONS",
    "COMPARABLE_PENDING_UPPER_BOUNDS",
    "EXPECTED_POINT_ESTIMATE",
    "EXPECTED_ESTIMATE_RANGE",
    "EXPECTED_PRIVATE_FILE_SHA256",
    "EXPECTED_PUBLIC_FILE_SHA256",
):
    setattr(RANKING, _name, globals()[_name])


RankingError = RANKING.RankingError
require = RANKING.require
sha256_bytes = RANKING.sha256_bytes
sha256_file = RANKING.sha256_file
canonical_sha256 = RANKING.canonical_sha256
serialized_json = RANKING.serialized_json
parse_coordinate = RANKING.parse_coordinate
parse_root = RANKING.parse_root
root_digest = RANKING.root_digest
coordinate_digest = RANKING.coordinate_digest
site_digest = RANKING.site_digest
build_outputs = RANKING.build_outputs
assert_source_free = RANKING.assert_source_free


def main(argv: Sequence[str] | None = None) -> int:
    return RANKING.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
