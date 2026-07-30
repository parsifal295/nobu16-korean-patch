#!/usr/bin/env python3
"""Rank the next PK selector family after selector 292."""

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
    / "build_pk_next_selector_family_ranking_post_selector238_consolidated_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "build_runtime_vm_post_selector292_consolidated_checkpoint_v1.py"
)
DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector292_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "runtime_vm_integration."
    "post_selector292_consolidated_checkpoint.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector292_consolidated.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector292_consolidated.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector292-consolidated.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector292-consolidated-source-free.v1"
)
METHOD = (
    "selector292_closure_checkpoint_pending_reachable_0143_"
    "owned_excluded_seven_way_selector_ranking"
)
OWNED_SELECTORS = (
    538, 568, 1096, 1174, 610, 550, 748, 1126, 142, 514, 628, 1198,
    178, 1090, 760, 508, 742, 322, 1162, 376, 364, 1168, 226, 268, 1078,
    466, 562, 730, 238, 292,
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "52C8E1015F09BB30BA90FD2C8B86868C5B7CDE2E20575797333776BD10F12094"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256: str | None = (
    "CCF550E94624B4A8C0E8A343DAC700568F1FA91798948C25E63E96F3B18EF50E"
)
EXPECTED_LEDGER_SHA256: str | None = (
    "90644EA8E6F2EF99CA2020993930E551536F00E9BF4DFD244ED46640123E8725"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256: str | None = (
    "E76C849DFB6589B7C48B830D227C368ACA98B80F18FBBC2DD8CF146D455F9652"
)
EXPECTED_PK_CANDIDATE_SHA256: str | None = (
    "723589D4CC42165F93FF60F0711E96DAB6E84737C75954FA36819F780CD57A2C"
)
EXPECTED_PK_PENDING_ROWS = 6_130
EXPECTED_PK_PENDING_ROOTS: int | None = 4_026
EXPECTED_PK_PENDING_ROOT_SHA256: str | None = (
    "C02588DB27ACE3117D035CB3727EE8877232C746B142D16B8D9CD2B6D2A8CC44"
)
EXPECTED_REACHABLE_CALL_TARGETS: int | None = 148
EXPECTED_OWNED_CALL_TARGETS: int | None = 32
EXPECTED_NON_SEVEN_WAY_TARGETS: int | None = 23
EXPECTED_ELIGIBLE_FAMILIES: int | None = 93
EXPECTED_ELIGIBLE_UNION_ROWS: int | None = 623
EXPECTED_ELIGIBLE_UNION_SHA256: str | None = (
    "095307AC56B7C69817BDD070D2528EE9DF7231501AF8464618ADC37A24A07AB7"
)
EXPECTED_RECOMMENDED_SELECTOR: str | None = "0:286"
EXPECTED_RECOMMENDED_TERMINALS: tuple[str, ...] | None = (
    "0:1608",
    "0:1609",
    "0:1610",
    "0:1611",
    "0:1612",
    "0:1613",
    "0:1614",
)
EXPECTED_RECOMMENDED_PENDING_ROWS: int | None = 32
EXPECTED_RECOMMENDED_PENDING_ROOTS: int | None = 13
EXPECTED_RECOMMENDED_PENDING_SITES: int | None = 12
EXPECTED_RECOMMENDED_CANDIDATE_SITES: int | None = 57
EXPECTED_RECOMMENDED_SOURCE_SITES: int | None = 69
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES: int | None = 12
EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES: int | None = 0
EXPECTED_POINT_ESTIMATE: int | None = 20
EXPECTED_ESTIMATE_RANGE: tuple[int, int] | None = (0, 31)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "8DA36086B9AD7CE6AAC01F11F873AF87517183977E260DB396816917528E9819"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "B5CF3A4298190C783B83113FCCC0EDC6BD63C5F0E8A1A5292239E358B5AB3F21"
)

BOOTSTRAP_PIN_NAMES = (
    "EXPECTED_CHECKPOINT_BUILDER_SHA256",
    "EXPECTED_LEDGER_SHA256",
    "EXPECTED_CHECKPOINT_PUBLIC_SHA256",
    "EXPECTED_PK_CANDIDATE_SHA256",
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
    "EXPECTED_POINT_ESTIMATE",
    "EXPECTED_ESTIMATE_RANGE",
    "EXPECTED_PRIVATE_FILE_SHA256",
    "EXPECTED_PUBLIC_FILE_SHA256",
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
    "pk_next_selector_post_292_predecessor_helpers_v1",
)
RANKING = PREDECESSOR_WRAPPER.RANKING
CORE_BUILD_OUTPUTS = PREDECESSOR_WRAPPER.CORE_BUILD_OUTPUTS

COMPARABLE_ACTUAL_PROMOTIONS = dict(
    PREDECESSOR_WRAPPER.COMPARABLE_ACTUAL_PROMOTIONS
)
COMPARABLE_ACTUAL_PROMOTIONS[292] = 21
COMPARABLE_PENDING_UPPER_BOUNDS = dict(
    PREDECESSOR_WRAPPER.COMPARABLE_PENDING_UPPER_BOUNDS
)
COMPARABLE_PENDING_UPPER_BOUNDS[292] = 33

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
sha256_file = RANKING.sha256_file
serialized_json = RANKING.serialized_json
assert_source_free = RANKING.assert_source_free


def bootstrap_missing() -> tuple[str, ...]:
    return tuple(name for name in BOOTSTRAP_PIN_NAMES if globals()[name] is None)


def build_outputs(*args: Any, **kwargs: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    missing = bootstrap_missing()
    require(
        not missing,
        "post-selector292 ranking bootstrap is not frozen: "
        + ",".join(missing),
    )
    require(
        sha256_file(PREDECESSOR_BUILDER)
        == EXPECTED_PREDECESSOR_BUILDER_SHA256,
        "post-selector238 ranking predecessor drifted",
    )
    require(
        sha256_file(CHECKPOINT_BUILDER_PATH)
        == EXPECTED_CHECKPOINT_BUILDER_SHA256,
        "post-selector292 checkpoint builder drifted",
    )
    private, public = CORE_BUILD_OUTPUTS(*args, **kwargs)
    eligible = {row["selector_coordinate"] for row in public["ranking"]}
    require(
        not eligible & {f"0:{selector}" for selector in OWNED_SELECTORS},
        "an owned selector reappeared in the ranking",
    )
    require(
        "0:292" not in eligible,
        "selector292 reappeared after its consolidated closure",
    )
    require(
        public["ranking"]
        and public["ranking"][0]["selector_coordinate"]
            == EXPECTED_RECOMMENDED_SELECTOR,
        "recomputed ranking top drifted",
    )
    return private, public


RANKING.build_outputs = build_outputs


def main(argv: Sequence[str] | None = None) -> int:
    return RANKING.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
