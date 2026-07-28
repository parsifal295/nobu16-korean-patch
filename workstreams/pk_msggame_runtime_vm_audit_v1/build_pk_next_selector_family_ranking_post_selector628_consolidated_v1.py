#!/usr/bin/env python3
"""Rank remaining PK selector families on the selector-628 checkpoint."""

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
    / "build_pk_next_selector_family_ranking_post_selector514_consolidated_v1.py"
)
DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector628_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "runtime_vm_integration."
    "post_selector628_consolidated_checkpoint.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector628_consolidated.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector628_consolidated.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector628-consolidated.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector628-consolidated-source-free.v1"
)
METHOD = (
    "selector628_checkpoint_pending_reachable_0143_"
    "seven_way_selector_ranking"
)
OWNED_SELECTORS = (
    538, 568, 1096, 1174, 610, 550, 748, 1126, 142, 514, 628
)

EXPECTED_LEDGER_SHA256 = (
    "64F57157C47A72E42CBDBDA59C84AA142519CAAF7D4391983CEFD34362640147"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256 = (
    "D75600A25C086D41190589DA21C8B389ACD9A9BAD561B920F9BB25F5FB9E5B88"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "28267B6928CBDBF3E98FBB8E13A4733947A4EAC6A2BF04812A848C1091F9B186"
)
EXPECTED_PK_PENDING_ROWS = 6_489
EXPECTED_PK_PENDING_ROOTS = 4_183
EXPECTED_PK_PENDING_ROOT_SHA256 = (
    "D3A155DF5FE6AE78340358FA25CAD3C8A5F421A3CE36B9995A2018019FA89820"
)
EXPECTED_REACHABLE_CALL_TARGETS = 155
EXPECTED_OWNED_CALL_TARGETS = 11
EXPECTED_NON_SEVEN_WAY_TARGETS = 26
EXPECTED_ELIGIBLE_FAMILIES = 118
EXPECTED_ELIGIBLE_UNION_ROWS = 1_276
EXPECTED_ELIGIBLE_UNION_SHA256 = (
    "07478C0BDB35E07803D6F0C99CB3A2BB15A2EBC38DF5D10E9F3FDFE01BACE1AF"
)
EXPECTED_RECOMMENDED_SELECTOR = "0:1198"
EXPECTED_RECOMMENDED_TERMINALS = tuple(
    f"0:{record_id}" for record_id in range(2672, 2679)
)
EXPECTED_RECOMMENDED_PENDING_ROWS = 83
EXPECTED_RECOMMENDED_PENDING_ROOTS = 25
EXPECTED_RECOMMENDED_PENDING_SITES = 25
EXPECTED_RECOMMENDED_CANDIDATE_SITES = 46
EXPECTED_RECOMMENDED_SOURCE_SITES = 46
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES = 0
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
}
EXPECTED_POINT_ESTIMATE = 65
EXPECTED_ESTIMATE_RANGE = (52, 82)

# Frozen after the first reproducible write/check cycle.
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "A6D43C66FFCD82A114AF4C5FC70371E209FC61C56916905F0513946F3655A6BB"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "95F0B757ECBB58610415F8FAE0A5CAFAA94083D6950E94E20C549EC3AFC0534C"
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
    "pk_next_selector_post_628_predecessor_helpers_v1",
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
