#!/usr/bin/env python3
"""Rank remaining PK selector families on the selector-610 checkpoint.

The graph walk is inherited from the frozen post-selector1174 ranking
implementation, but every mutable audit constant is rebound to the immutable
selector-610 delta checkpoint. Older ranking artifacts are never read as
current state and are never rewritten.
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
    / "build_pk_next_selector_family_ranking_post_selector568_1096_1174_v1.py"
)
DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector610_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "runtime_vm_integration."
    "post_selector610_consolidated_checkpoint.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector610_consolidated.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector610_consolidated.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector610-consolidated.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector610-consolidated-source-free.v1"
)
METHOD = (
    "selector610_checkpoint_pending_reachable_0143_"
    "seven_way_selector_ranking"
)
OWNED_SELECTORS = (538, 568, 1096, 1174, 610)

EXPECTED_LEDGER_SHA256 = (
    "0218C3D198C9930C8920ED8DAEB2DDD85987878035AC59DD5ECC8179D38DE12B"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256 = (
    "42BB33CD2F7553EE3E251DDD78933F85D181F140AA133C5843F6DBDF379B53D3"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "F80EA5958757F097885279BAB53A8456758BB99B1CE47E214FE0F54AB7152807"
)
EXPECTED_PK_PENDING_ROWS = 7_101
EXPECTED_PK_PENDING_ROOTS = 4_458
EXPECTED_PK_PENDING_ROOT_SHA256 = (
    "9BB1F19D488EE5FCEB1A96D8256195B63949CEF65503CBF99356D58E84900D59"
)
EXPECTED_REACHABLE_CALL_TARGETS = 161
EXPECTED_OWNED_CALL_TARGETS = 6
EXPECTED_NON_SEVEN_WAY_TARGETS = 26
EXPECTED_ELIGIBLE_FAMILIES = 129
EXPECTED_ELIGIBLE_UNION_ROWS = 1_898
EXPECTED_ELIGIBLE_UNION_SHA256 = (
    "B1888A96933DD632C04E4653F8CFBA9B14EF8606A32E54C1EA3D1257F4D4D3E5"
)
EXPECTED_RECOMMENDED_SELECTOR = "0:550"
EXPECTED_RECOMMENDED_TERMINALS = tuple(
    f"0:{record_id}" for record_id in range(1930, 1937)
)
EXPECTED_RECOMMENDED_PENDING_ROWS = 171
EXPECTED_RECOMMENDED_PENDING_ROOTS = 91
EXPECTED_RECOMMENDED_PENDING_SITES = 92
EXPECTED_RECOMMENDED_CANDIDATE_SITES = 169
EXPECTED_RECOMMENDED_SOURCE_SITES = 177
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES = 8
EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES = 0

COMPARABLE_ACTUAL_PROMOTIONS = {
    568: 225,
    1096: 206,
    1174: 197,
    610: 167,
}
COMPARABLE_PENDING_UPPER_BOUNDS = {
    568: 331,
    1096: 247,
    1174: 224,
    610: 192,
}
EXPECTED_POINT_ESTIMATE = 137
EXPECTED_ESTIMATE_RANGE = (116, 150)

# Frozen after the first reproducible write/check cycle.
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "3784403CDA34B66468D4387F4207DE314719A518078FBDAD657392EF507C7123"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "068E4BBF93AEE68F551E87D038542EC7FAE0153925853A000EEDE0BD133BC553"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RANKING = load_module(
    PREDECESSOR_BUILDER,
    "pk_next_selector_post_610_predecessor_helpers_v1",
)

# Rebind every stateful input and every assertion affected by selector 610.
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
