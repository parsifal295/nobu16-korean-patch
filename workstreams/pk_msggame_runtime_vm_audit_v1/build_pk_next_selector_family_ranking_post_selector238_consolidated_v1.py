#!/usr/bin/env python3
"""Rank the next PK selector family after selector 238."""

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
    / "build_pk_next_selector_family_ranking_post_selector730_consolidated_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "build_runtime_vm_post_selector238_consolidated_checkpoint_v1.py"
)
DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector238_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "runtime_vm_integration."
    "post_selector238_consolidated_checkpoint.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector238_consolidated.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector238_consolidated.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector238-consolidated.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector238-consolidated-source-free.v1"
)
METHOD = (
    "selector238_closure_checkpoint_pending_reachable_0143_"
    "owned_excluded_seven_way_selector_ranking"
)
OWNED_SELECTORS = (
    538, 568, 1096, 1174, 610, 550, 748, 1126, 142, 514, 628, 1198,
    178, 1090, 760, 508, 742, 322, 1162, 376, 364, 1168, 226, 268, 1078,
    466, 562, 730, 238,
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "3BCA1BFD3A6F4E87975EC46C15E8EEA460AF0EE348C3D3BD199668DF76C271AD"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256: str | None = (
    "503A8500AFDB5A1041FA497A62634B3C30772DCE79628168C4208A898B45738B"
)
EXPECTED_LEDGER_SHA256: str | None = (
    "AC10F7E71CFAD259ABBC08139BE0DB848CF5309578045532A48991F40E0035AB"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256: str | None = (
    "0CAE7231474FBAE0BCE8E1E98D44225DCC5445EEEA435378E0D56BD1F83A5384"
)
EXPECTED_PK_CANDIDATE_SHA256: str | None = (
    "9E5C60A451DB7CCA7B046AFD8CFF199CB3665E003CB0C751120478F693D20C24"
)
EXPECTED_PK_PENDING_ROWS = 6_151
EXPECTED_PK_PENDING_ROOTS: int | None = 4_032
EXPECTED_PK_PENDING_ROOT_SHA256: str | None = (
    "213C2C506EEE6D7D1A8730A702336183AA7F869E21286DF30C78A1E93ED7FB05"
)
EXPECTED_REACHABLE_CALL_TARGETS: int | None = 149
EXPECTED_OWNED_CALL_TARGETS: int | None = 31
EXPECTED_NON_SEVEN_WAY_TARGETS: int | None = 23
EXPECTED_ELIGIBLE_FAMILIES: int | None = 95
EXPECTED_ELIGIBLE_UNION_ROWS: int | None = 646
EXPECTED_ELIGIBLE_UNION_SHA256: str | None = (
    "74A9BED929A4BCA956B9BEF1D7C07656F54995353C812F291CEF62AFB1C3E49B"
)
EXPECTED_RECOMMENDED_SELECTOR: str | None = "0:292"
EXPECTED_RECOMMENDED_TERMINALS: tuple[str, ...] | None = (
    "0:1615",
    "0:1616",
    "0:1617",
    "0:1618",
    "0:1619",
    "0:1620",
    "0:1621",
)
EXPECTED_RECOMMENDED_PENDING_ROWS: int | None = 33
EXPECTED_RECOMMENDED_PENDING_ROOTS: int | None = 11
EXPECTED_RECOMMENDED_PENDING_SITES: int | None = 11
EXPECTED_RECOMMENDED_CANDIDATE_SITES: int | None = 26
EXPECTED_RECOMMENDED_SOURCE_SITES: int | None = 31
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES: int | None = 5
EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES: int | None = 0
EXPECTED_POINT_ESTIMATE: int | None = 21
EXPECTED_ESTIMATE_RANGE: tuple[int, int] | None = (0, 32)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "89F45139F0D684F9FA87CF47A3C964B50EA4546851D79F8656F7B335025FB164"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "C29C242A66BE2AAC13F8C9C02CC4D42A1E02FBF7D839B5401E926F9A0407ACBF"
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
    "pk_next_selector_post_238_predecessor_helpers_v1",
)
RANKING = PREDECESSOR_WRAPPER.RANKING
CORE_BUILD_OUTPUTS = PREDECESSOR_WRAPPER.CORE_BUILD_OUTPUTS

COMPARABLE_ACTUAL_PROMOTIONS = dict(
    PREDECESSOR_WRAPPER.COMPARABLE_ACTUAL_PROMOTIONS
)
COMPARABLE_ACTUAL_PROMOTIONS[238] = 27
COMPARABLE_PENDING_UPPER_BOUNDS = dict(
    PREDECESSOR_WRAPPER.COMPARABLE_PENDING_UPPER_BOUNDS
)
COMPARABLE_PENDING_UPPER_BOUNDS[238] = 36

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
        "post-selector238 ranking bootstrap is not frozen: "
        + ",".join(missing),
    )
    require(
        sha256_file(PREDECESSOR_BUILDER)
        == EXPECTED_PREDECESSOR_BUILDER_SHA256,
        "post-selector730 ranking predecessor drifted",
    )
    require(
        sha256_file(CHECKPOINT_BUILDER_PATH)
        == EXPECTED_CHECKPOINT_BUILDER_SHA256,
        "post-selector238 checkpoint builder drifted",
    )
    private, public = CORE_BUILD_OUTPUTS(*args, **kwargs)
    eligible = {row["selector_coordinate"] for row in public["ranking"]}
    require(
        not eligible & {f"0:{selector}" for selector in OWNED_SELECTORS},
        "an owned selector reappeared in the ranking",
    )
    require(
        "0:238" not in eligible,
        "selector238 reappeared after its consolidated closure",
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
