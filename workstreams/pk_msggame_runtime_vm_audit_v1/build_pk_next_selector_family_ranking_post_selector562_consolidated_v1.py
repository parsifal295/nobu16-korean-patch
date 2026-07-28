#!/usr/bin/env python3
"""Scaffold the next PK selector ranking after selector 562."""

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
    / "build_pk_next_selector_family_ranking_post_selector466_consolidated_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "build_runtime_vm_post_selector562_consolidated_checkpoint_v1.py"
)
DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector562_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "runtime_vm_integration."
    "post_selector562_consolidated_checkpoint.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector562_consolidated.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector562_consolidated.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector562-consolidated.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector562-consolidated-source-free.v1"
)
METHOD = (
    "selector562_closure_checkpoint_pending_reachable_0143_"
    "owned_excluded_seven_way_selector_ranking"
)
OWNED_SELECTORS = (
    538, 568, 1096, 1174, 610, 550, 748, 1126, 142, 514, 628, 1198,
    178, 1090, 760, 508, 742, 322, 1162, 376, 364, 1168, 226, 268, 1078,
    466, 562,
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "ACF1EE6BD84482678CA0C64E882C65BF33E1048FF9E4CAEDA6DE3CEA22727E63"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256: str | None = (
    "F748FE30B4940004929879EDEC6A9463CB65F1117E19322394491244602C5362"
)
EXPECTED_LEDGER_SHA256: str | None = (
    "8E31995689359D5F8DD1F23FC7A894C07AC8BBB3C08EF2B87651E6E3E8B1086A"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256: str | None = (
    "5445CD4A9C9515A8732446DA397D0FF0BB66E657A17C14BEDC374CCC745CDF76"
)
EXPECTED_PK_CANDIDATE_SHA256: str | None = (
    "B7CBFA388BDD50F60CD5EEF88A63B62D357475925A0A3AA6D7DCA1A191607815"
)
EXPECTED_PK_PENDING_ROWS = 6_181
EXPECTED_PK_PENDING_ROOTS: int | None = 4_042
EXPECTED_PK_PENDING_ROOT_SHA256: str | None = (
    "4940062332D79121B35404BCDB33EA9BCBC8E60EB3054DF577D80FB7A12E1A11"
)
EXPECTED_REACHABLE_CALL_TARGETS: int | None = 150
EXPECTED_OWNED_CALL_TARGETS: int | None = 29
EXPECTED_NON_SEVEN_WAY_TARGETS: int | None = 23
EXPECTED_ELIGIBLE_FAMILIES: int | None = 98
EXPECTED_ELIGIBLE_UNION_ROWS: int | None = 694
EXPECTED_ELIGIBLE_UNION_SHA256: str | None = (
    "8CBE8EAA9A9CE9E54410D9C7660B37A81774177D59D8003AF6BA6ACE5C83DA0E"
)
EXPECTED_RECOMMENDED_SELECTOR: str | None = "0:730"
EXPECTED_RECOMMENDED_TERMINALS: tuple[str, ...] | None = (
    "0:2140",
    "0:2141",
    "0:2142",
    "0:2143",
    "0:2144",
    "0:2145",
    "0:2146",
)
EXPECTED_RECOMMENDED_PENDING_ROWS: int | None = 37
EXPECTED_RECOMMENDED_PENDING_ROOTS: int | None = 18
EXPECTED_RECOMMENDED_PENDING_SITES: int | None = 18
EXPECTED_RECOMMENDED_CANDIDATE_SITES: int | None = 41
EXPECTED_RECOMMENDED_SOURCE_SITES: int | None = 46
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES: int | None = 5
EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES: int | None = 0
EXPECTED_POINT_ESTIMATE: int | None = 24
EXPECTED_ESTIMATE_RANGE: tuple[int, int] | None = (0, 36)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "1A8479D8CE3EEFE52E853B1B8F1AE0D194FF63D9E7CB1C27D4B0936D32041056"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "85E6DED228DF9771A973BE907C0B1973D15E5EFF59BDADEE4C64BED6B84CDA66"
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
    "pk_next_selector_post_562_predecessor_helpers_v1",
)
RANKING = PREDECESSOR_WRAPPER.RANKING
CORE_BUILD_OUTPUTS = PREDECESSOR_WRAPPER.CORE_BUILD_OUTPUTS

COMPARABLE_ACTUAL_PROMOTIONS = dict(
    PREDECESSOR_WRAPPER.COMPARABLE_ACTUAL_PROMOTIONS
)
COMPARABLE_ACTUAL_PROMOTIONS[562] = 10
COMPARABLE_PENDING_UPPER_BOUNDS = dict(
    PREDECESSOR_WRAPPER.COMPARABLE_PENDING_UPPER_BOUNDS
)
COMPARABLE_PENDING_UPPER_BOUNDS[562] = 38

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
        "post-selector562 ranking bootstrap is not frozen: "
        + ",".join(missing),
    )
    require(
        sha256_file(PREDECESSOR_BUILDER)
        == EXPECTED_PREDECESSOR_BUILDER_SHA256,
        "post-selector466 ranking predecessor drifted",
    )
    require(
        sha256_file(CHECKPOINT_BUILDER_PATH)
        == EXPECTED_CHECKPOINT_BUILDER_SHA256,
        "post-selector562 checkpoint builder drifted",
    )
    private, public = CORE_BUILD_OUTPUTS(*args, **kwargs)
    eligible = {row["selector_coordinate"] for row in public["ranking"]}
    require(
        not eligible & {f"0:{selector}" for selector in OWNED_SELECTORS},
        "an owned selector reappeared in the ranking",
    )
    require(
        "0:562" not in eligible,
        "selector562 reappeared after its consolidated closure",
    )
    return private, public


RANKING.build_outputs = build_outputs


def main(argv: Sequence[str] | None = None) -> int:
    return RANKING.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
