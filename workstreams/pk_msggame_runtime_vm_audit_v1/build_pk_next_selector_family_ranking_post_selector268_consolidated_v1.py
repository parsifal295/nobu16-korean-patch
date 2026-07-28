#!/usr/bin/env python3
"""Bootstrap the next PK selector ranking after the selector-268 closure."""

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
    / "build_pk_next_selector_family_ranking_post_selector226_consolidated_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "build_runtime_vm_post_selector268_consolidated_checkpoint_v1.py"
)
DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector268_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "runtime_vm_integration."
    "post_selector268_consolidated_checkpoint.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector268_consolidated.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector268_consolidated.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector268-consolidated.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector268-consolidated-source-free.v1"
)
METHOD = (
    "selector268_closure_checkpoint_pending_reachable_0143_"
    "owned_excluded_seven_way_selector_ranking"
)
OWNED_SELECTORS = (
    538, 568, 1096, 1174, 610, 550, 748, 1126, 142, 514, 628, 1198,
    178, 1090, 760, 508, 742, 322, 1162, 376, 364, 1168, 226, 268,
)

EXPECTED_CHECKPOINT_BUILDER_SHA256: str | None = (
    "6E4FEFF52329BA9A4A6AACB74910FC0DB05C0659F02277680102C4447BFA5B3A"
)
EXPECTED_LEDGER_SHA256: str | None = (
    "0936BD050D1BB529848AD861B951D178A3521C086BC41027C4ED4A5B4FBC79C3"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256: str | None = (
    "FD8A708ED92756AB2024861A1B97550F8229889282E7B58CDEFAEEDFC0C2ECE3"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "92B86808931C1FD34320BC5A9BFD05B7AD704FA9392534FF8DE8F6293F413DAD"
)
EXPECTED_PK_PENDING_ROWS = 6_232
EXPECTED_PK_PENDING_ROOTS: int | None = 4_065
EXPECTED_PK_PENDING_ROOT_SHA256: str | None = (
    "C03842AA4902DC41D3A8A68A32FB574F341FE4D589A3DC87DDA2DC1B6E2A4024"
)
EXPECTED_REACHABLE_CALL_TARGETS: int | None = 150
EXPECTED_OWNED_CALL_TARGETS: int | None = 26
EXPECTED_NON_SEVEN_WAY_TARGETS: int | None = 23
EXPECTED_ELIGIBLE_FAMILIES: int | None = 101
EXPECTED_ELIGIBLE_UNION_ROWS: int | None = 791
EXPECTED_ELIGIBLE_UNION_SHA256: str | None = (
    "7A9E6D69EFBA78615D66F91ACB0088261676DDBECEE61A3B24E062289A722B9D"
)
EXPECTED_RECOMMENDED_SELECTOR: str | None = "0:1078"
EXPECTED_RECOMMENDED_TERMINALS: tuple[str, ...] | None = (
    "0:2560",
    "0:2561",
    "0:2562",
    "0:2563",
    "0:2564",
    "0:2565",
    "0:2566",
)
EXPECTED_RECOMMENDED_PENDING_ROWS: int | None = 43
EXPECTED_RECOMMENDED_PENDING_ROOTS: int | None = 20
EXPECTED_RECOMMENDED_PENDING_SITES: int | None = 20
EXPECTED_RECOMMENDED_CANDIDATE_SITES: int | None = 43
EXPECTED_RECOMMENDED_SOURCE_SITES: int | None = 44
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES: int | None = 1
EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES: int | None = 0
EXPECTED_POINT_ESTIMATE: int | None = 28
EXPECTED_ESTIMATE_RANGE: tuple[int, int] | None = (0, 42)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "11D2A291C8C8E52681C95D6D74650DA6AD22D89EE0AECA1E59166DD4E6D574E0"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "1C156F9E650B5067C4BE8C46B808AC165E99677FFF6D991D53AAA1901E83C19A"
)

BOOTSTRAP_PIN_NAMES = (
    "EXPECTED_CHECKPOINT_BUILDER_SHA256",
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
    "pk_next_selector_post_268_predecessor_helpers_v1",
)
RANKING = PREDECESSOR_WRAPPER.RANKING
CORE_BUILD_OUTPUTS = PREDECESSOR_WRAPPER.CORE_BUILD_OUTPUTS

COMPARABLE_ACTUAL_PROMOTIONS = dict(
    PREDECESSOR_WRAPPER.COMPARABLE_ACTUAL_PROMOTIONS
)
COMPARABLE_ACTUAL_PROMOTIONS[268] = 14
COMPARABLE_PENDING_UPPER_BOUNDS = dict(
    PREDECESSOR_WRAPPER.COMPARABLE_PENDING_UPPER_BOUNDS
)
COMPARABLE_PENDING_UPPER_BOUNDS[268] = 44

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
        "post-selector268 ranking bootstrap is not frozen: "
        + ",".join(missing),
    )
    require(
        sha256_file(CHECKPOINT_BUILDER_PATH)
        == EXPECTED_CHECKPOINT_BUILDER_SHA256,
        "post-selector268 checkpoint builder drifted",
    )
    private, public = CORE_BUILD_OUTPUTS(*args, **kwargs)
    eligible = {row["selector_coordinate"] for row in public["ranking"]}
    require(
        not eligible & {f"0:{selector}" for selector in OWNED_SELECTORS},
        "an owned selector reappeared in the ranking",
    )
    require(
        "0:268" not in eligible,
        "selector268 reappeared after its consolidated closure",
    )
    return private, public


RANKING.build_outputs = build_outputs


def main(argv: Sequence[str] | None = None) -> int:
    return RANKING.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
