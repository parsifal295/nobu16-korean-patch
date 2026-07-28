#!/usr/bin/env python3
"""Rank remaining PK selector families on the selector-1090 checkpoint."""

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
    / "build_pk_next_selector_family_ranking_post_selector178_consolidated_v1.py"
)
DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector1090_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "runtime_vm_integration."
    "post_selector1090_consolidated_checkpoint.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector1090_consolidated.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector1090_consolidated.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector1090-consolidated.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector1090-consolidated-source-free.v1"
)
METHOD = (
    "selector1090_checkpoint_pending_reachable_0143_"
    "seven_way_selector_ranking"
)
OWNED_SELECTORS = (
    538, 568, 1096, 1174, 610, 550, 748, 1126, 142, 514, 628, 1198,
    178, 1090,
)

EXPECTED_LEDGER_SHA256 = (
    "CDF7539F8E6A6F0D024A7357854A0AFE45E91F3CBD144822E1DEF8730A9A373F"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256 = (
    "C01950D1B342D45FF8C6FBEB3D7EFD0B5087592D0585EC1A60A668FE0C0B0D93"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "396A8DF109A0693C439F990049477F5DE6E10720854D73057F3DFA1702002CCF"
)
EXPECTED_PK_PENDING_ROWS = 6_368
EXPECTED_PK_PENDING_ROOTS = 4_128
EXPECTED_PK_PENDING_ROOT_SHA256 = (
    "22A5E66C53B57FFF95708626ADCA78E11E3FD3C64AF6C7D1599C307273062375"
)
EXPECTED_REACHABLE_CALL_TARGETS = 153
EXPECTED_OWNED_CALL_TARGETS = 15
EXPECTED_NON_SEVEN_WAY_TARGETS = 25
EXPECTED_ELIGIBLE_FAMILIES = 113
EXPECTED_ELIGIBLE_UNION_ROWS = 1_109
EXPECTED_ELIGIBLE_UNION_SHA256 = (
    "1B38384DE24510BF80550CFD1CE8C4D8FE3D5B89738ED9A757A6A4E4EBE5E575"
)
EXPECTED_RECOMMENDED_SELECTOR = "0:760"
EXPECTED_RECOMMENDED_TERMINALS = tuple(
    f"0:{record_id}" for record_id in range(2175, 2182)
)
EXPECTED_RECOMMENDED_PENDING_ROWS = 67
EXPECTED_RECOMMENDED_PENDING_ROOTS = 21
EXPECTED_RECOMMENDED_PENDING_SITES = 21
EXPECTED_RECOMMENDED_CANDIDATE_SITES = 32
EXPECTED_RECOMMENDED_SOURCE_SITES = 35
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES = 3
EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES = 0

COMPARABLE_ACTUAL_PROMOTIONS = {
    568: 225,
    1096: 206,
    1174: 197,
    610: 167,
    550: 121,
    748: 101,
    1126: 118,
    142: 116,
    514: 98,
    628: 58,
    1198: 25,
    178: 32,
    1090: 64,
}
COMPARABLE_PENDING_UPPER_BOUNDS = {
    568: 331,
    1096: 247,
    1174: 224,
    610: 192,
    550: 171,
    748: 162,
    1126: 141,
    142: 118,
    514: 113,
    628: 90,
    1198: 83,
    178: 81,
    1090: 80,
}
EXPECTED_POINT_ESTIMATE = 50
EXPECTED_ESTIMATE_RANGE = (20, 66)

# Frozen after the first reproducible write/check cycle.
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "34D58ADEDDA221918574ED4ACC67024053DE5B1E39CB013A08164E09F80B9415"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "9B983CD00B272C3BF84BD2770FEA04696776993E32168AC4212BA725ABD95439"
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
    "pk_next_selector_post_1090_predecessor_helpers_v1",
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
