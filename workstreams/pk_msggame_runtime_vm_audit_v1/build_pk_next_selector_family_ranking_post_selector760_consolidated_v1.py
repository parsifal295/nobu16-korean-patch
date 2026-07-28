#!/usr/bin/env python3
"""Rank remaining PK selector families on the selector-760 checkpoint."""

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
    / "build_pk_next_selector_family_ranking_post_selector1090_consolidated_v1.py"
)
DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector760_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "runtime_vm_integration."
    "post_selector760_consolidated_checkpoint.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector760_consolidated.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector760_consolidated.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector760-consolidated.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector760-consolidated-source-free.v1"
)
METHOD = (
    "selector760_checkpoint_pending_reachable_0143_"
    "seven_way_selector_ranking"
)
OWNED_SELECTORS = (
    538, 568, 1096, 1174, 610, 550, 748, 1126, 142, 514, 628, 1198,
    178, 1090, 760,
)

EXPECTED_LEDGER_SHA256 = (
    "797D27314E8E168E1F2BACF9174E7246B83BF6DEDB0AC3B6C925D6D076CAC8C3"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256 = (
    "3B67EC38FCECCD9B9592A39C426EC14F64EF9354C608C176730460E2C37D8B6D"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "03D128438A4A79F1C4C59D46996D93E8DBD10ECAF707E18E0A46A0B3AF29A2F5"
)
EXPECTED_PK_PENDING_ROWS = 6_341
EXPECTED_PK_PENDING_ROOTS = 4_121
EXPECTED_PK_PENDING_ROOT_SHA256 = (
    "8BC5E0EB2A2182D396A66C81EA1AAF120FE86C41D5F54728DA605C25D1D61E19"
)
EXPECTED_REACHABLE_CALL_TARGETS = 151
EXPECTED_OWNED_CALL_TARGETS = 16
EXPECTED_NON_SEVEN_WAY_TARGETS = 24
EXPECTED_ELIGIBLE_FAMILIES = 111
EXPECTED_ELIGIBLE_UNION_ROWS = 1_070
EXPECTED_ELIGIBLE_UNION_SHA256 = (
    "B2752170654538AA2CE6EDC943A33333BE939538C5013BEE942A43DAD6D839CE"
)
EXPECTED_RECOMMENDED_SELECTOR = "0:508"
EXPECTED_RECOMMENDED_TERMINALS = tuple(
    f"0:{record_id}" for record_id in range(1888, 1895)
)
EXPECTED_RECOMMENDED_PENDING_ROWS = 61
EXPECTED_RECOMMENDED_PENDING_ROOTS = 22
EXPECTED_RECOMMENDED_PENDING_SITES = 22
EXPECTED_RECOMMENDED_CANDIDATE_SITES = 74
EXPECTED_RECOMMENDED_SOURCE_SITES = 81
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES = 7
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
    760: 27,
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
    760: 67,
}
EXPECTED_POINT_ESTIMATE = 45
EXPECTED_ESTIMATE_RANGE = (18, 60)

# Frozen after the first reproducible write/check cycle.
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "0115A4E36611034AD1D0808447B588258C28915A8A8D03C0125497E31B01FBC4"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "26C15E6C8B930BD2BD7719477E0FBBD9817F415F10B464626234AB330F5F91A9"
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
    "pk_next_selector_post_760_predecessor_helpers_v1",
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
