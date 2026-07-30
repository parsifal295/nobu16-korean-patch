#!/usr/bin/env python3
"""Bootstrap the next PK selector ranking after the selector-1168 closure."""

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
    / "build_pk_next_selector_family_ranking_post_selector364_consolidated_v1.py"
)
DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector1168_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "runtime_vm_integration."
    "post_selector1168_consolidated_checkpoint.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector1168_consolidated.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector1168_consolidated.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector1168-consolidated.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector1168-consolidated-source-free.v1"
)
METHOD = (
    "selector1168_closure_checkpoint_pending_reachable_0143_"
    "owned_excluded_seven_way_selector_ranking"
)
OWNED_SELECTORS = (
    538, 568, 1096, 1174, 610, 550, 748, 1126, 142, 514, 628, 1198,
    178, 1090, 760, 508, 742, 322, 1162, 376, 364, 1168,
)

# The closure state is known. Checkpoint and ranking-universe pins must remain
# unset until the post-selector1168 checkpoint is independently committed.
EXPECTED_LEDGER_SHA256: str | None = (
    "56FBAF8FB54CCFA7EAF10355F66FE6A730374804F48FB4CD9F8F15A99AEE9A91"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256: str | None = (
    "9A04C999B850A1024BBB9AE57F509CA1C879A5DC4D59BF717873FD17E609545F"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "EF84A8B8A18C1F2F1F72D3A650C01DC7B058F32A3536C130809C4FCB31C837C7"
)
EXPECTED_PK_PENDING_ROWS = 6_283
EXPECTED_PK_PENDING_ROOTS: int | None = 4_098
EXPECTED_PK_PENDING_ROOT_SHA256: str | None = (
    "D46F1EE0780680AF9917C178086B2D5B2DD67B7191C2F47AE81C6472354D3676"
)
EXPECTED_REACHABLE_CALL_TARGETS: int | None = 150
EXPECTED_OWNED_CALL_TARGETS: int | None = 24
EXPECTED_NON_SEVEN_WAY_TARGETS: int | None = 23
EXPECTED_ELIGIBLE_FAMILIES: int | None = 103
EXPECTED_ELIGIBLE_UNION_ROWS: int | None = 856
EXPECTED_ELIGIBLE_UNION_SHA256: str | None = (
    "FF08D08F9C78F07C29F3FB1EE6055BEB94398C5472130EB3A8E815D1E705B266"
)
EXPECTED_RECOMMENDED_SELECTOR: str | None = "0:226"
EXPECTED_RECOMMENDED_TERMINALS: tuple[str, ...] | None = tuple(
    f"0:{record_id}" for record_id in range(1538, 1545)
)
EXPECTED_RECOMMENDED_PENDING_ROWS: int | None = 46
EXPECTED_RECOMMENDED_PENDING_ROOTS: int | None = 33
EXPECTED_RECOMMENDED_PENDING_SITES: int | None = 33
EXPECTED_RECOMMENDED_CANDIDATE_SITES: int | None = 70
EXPECTED_RECOMMENDED_SOURCE_SITES: int | None = 75
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES: int | None = 5
EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES: int | None = 0

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
    508: 0,
    742: 6,
    322: 25,
    1162: 3,
    376: 0,
    364: 5,
    1168: 19,
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
    508: 61,
    742: 61,
    322: 57,
    1162: 55,
    376: 52,
    364: 48,
    1168: 48,
}
EXPECTED_POINT_ESTIMATE: int | None = 30
EXPECTED_ESTIMATE_RANGE: tuple[int, int] | None = (0, 45)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "F0AC863B20850BD149344E2524A373C051325FE5BF4D0E010CD59F65CFB907F2"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "FD4A36F6F150FC4EAB929924CB1D5B0092923607D8418BE1D0B4E36154FAB836"
)

BOOTSTRAP_PIN_NAMES = (
    "EXPECTED_LEDGER_SHA256",
    "EXPECTED_CHECKPOINT_PUBLIC_SHA256",
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
    "pk_next_selector_post_1168_predecessor_helpers_v1",
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
sha256_file = RANKING.sha256_file
serialized_json = RANKING.serialized_json
assert_source_free = RANKING.assert_source_free
CORE_BUILD_OUTPUTS = PREDECESSOR_WRAPPER.CORE_BUILD_OUTPUTS


def bootstrap_missing() -> tuple[str, ...]:
    return tuple(name for name in BOOTSTRAP_PIN_NAMES if globals()[name] is None)


def build_outputs(*args: Any, **kwargs: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    missing = bootstrap_missing()
    require(
        not missing,
        "post-selector1168 ranking bootstrap is not frozen: "
        + ",".join(missing),
    )
    private, public = CORE_BUILD_OUTPUTS(*args, **kwargs)
    eligible = {row["selector_coordinate"] for row in public["ranking"]}
    require(
        not eligible & {f"0:{selector}" for selector in OWNED_SELECTORS},
        "an owned selector reappeared in the ranking",
    )
    require(
        not eligible & {"0:508", "0:376", "0:364", "0:1168"},
        "a closed selector reappeared in the ranking",
    )
    return private, public


RANKING.build_outputs = build_outputs


def main(argv: Sequence[str] | None = None) -> int:
    return RANKING.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
