#!/usr/bin/env python3
"""Bootstrap the next PK selector ranking after the selector-466 closure."""

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
    / "build_pk_next_selector_family_ranking_post_selector1078_consolidated_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "build_runtime_vm_post_selector466_consolidated_checkpoint_v1.py"
)
DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector466_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "runtime_vm_integration."
    "post_selector466_consolidated_checkpoint.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector466_consolidated.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector466_consolidated.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector466-consolidated.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector466-consolidated-source-free.v1"
)
METHOD = (
    "selector466_closure_checkpoint_pending_reachable_0143_"
    "owned_excluded_seven_way_selector_ranking"
)
OWNED_SELECTORS = (
    538, 568, 1096, 1174, 610, 550, 748, 1126, 142, 514, 628, 1198,
    178, 1090, 760, 508, 742, 322, 1162, 376, 364, 1168, 226, 268, 1078,
    466,
)

EXPECTED_CHECKPOINT_BUILDER_SHA256: str | None = (
    "727BC2640FC993AB417960D7D29E96BC89C9A09803EB4038A2AB0F0285E319F3"
)
EXPECTED_LEDGER_SHA256: str | None = (
    "99450F568D8EDED40C7A7332F52DADA184EE6F11FB129CFDBCC758C7880DC197"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256: str | None = (
    "D3824B5CF7A8DE02626FF06CE40816086F7DFB8EF6A0A9E06686756A9B69EA5E"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "E2283160520383E455C9C26112E80E5DB5EDB89161A9842FF3BD8F4C7FFCAD45"
)
EXPECTED_PK_PENDING_ROWS = 6_191
EXPECTED_PK_PENDING_ROOTS: int | None = 4_046
EXPECTED_PK_PENDING_ROOT_SHA256: str | None = (
    "0D4A9BF4C86D3D34898A00108D98352295EB256EE7F0D5CEB38DB246C64AA5A1"
)
EXPECTED_REACHABLE_CALL_TARGETS: int | None = 150
EXPECTED_OWNED_CALL_TARGETS: int | None = 28
EXPECTED_NON_SEVEN_WAY_TARGETS: int | None = 23
EXPECTED_ELIGIBLE_FAMILIES: int | None = 99
EXPECTED_ELIGIBLE_UNION_ROWS: int | None = 725
EXPECTED_ELIGIBLE_UNION_SHA256: str | None = (
    "D0952974F333DF5C905B7AB5EB7294A26F06CCA35FD9EF7998B8AC487478120C"
)
EXPECTED_RECOMMENDED_SELECTOR: str | None = "0:562"
EXPECTED_RECOMMENDED_TERMINALS: tuple[str, ...] | None = (
    "0:1944",
    "0:1945",
    "0:1946",
    "0:1947",
    "0:1948",
    "0:1949",
    "0:1950",
)
EXPECTED_RECOMMENDED_PENDING_ROWS: int | None = 38
EXPECTED_RECOMMENDED_PENDING_ROOTS: int | None = 25
EXPECTED_RECOMMENDED_PENDING_SITES: int | None = 25
EXPECTED_RECOMMENDED_CANDIDATE_SITES: int | None = 54
EXPECTED_RECOMMENDED_SOURCE_SITES: int | None = 60
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES: int | None = 6
EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES: int | None = 0
EXPECTED_POINT_ESTIMATE: int | None = 24
EXPECTED_ESTIMATE_RANGE: tuple[int, int] | None = (0, 37)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "65F3BE24C8889641B2BF5193418ECD4D39FF069D486C005F4E88C00388AD1661"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "B0F0ED90FB11ED00EAAC1608583DA23C5F2F04A54CDFF4DFA5F57EEC624A258B"
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
    "pk_next_selector_post_466_predecessor_helpers_v1",
)
RANKING = PREDECESSOR_WRAPPER.RANKING
CORE_BUILD_OUTPUTS = PREDECESSOR_WRAPPER.CORE_BUILD_OUTPUTS

COMPARABLE_ACTUAL_PROMOTIONS = dict(
    PREDECESSOR_WRAPPER.COMPARABLE_ACTUAL_PROMOTIONS
)
COMPARABLE_ACTUAL_PROMOTIONS[466] = 24
COMPARABLE_PENDING_UPPER_BOUNDS = dict(
    PREDECESSOR_WRAPPER.COMPARABLE_PENDING_UPPER_BOUNDS
)
COMPARABLE_PENDING_UPPER_BOUNDS[466] = 41

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
        "post-selector466 ranking bootstrap is not frozen: "
        + ",".join(missing),
    )
    require(
        sha256_file(CHECKPOINT_BUILDER_PATH)
        == EXPECTED_CHECKPOINT_BUILDER_SHA256,
        "post-selector466 checkpoint builder drifted",
    )
    private, public = CORE_BUILD_OUTPUTS(*args, **kwargs)
    eligible = {row["selector_coordinate"] for row in public["ranking"]}
    require(
        not eligible & {f"0:{selector}" for selector in OWNED_SELECTORS},
        "an owned selector reappeared in the ranking",
    )
    require(
        "0:466" not in eligible,
        "selector466 reappeared after its consolidated closure",
    )
    return private, public


RANKING.build_outputs = build_outputs


def main(argv: Sequence[str] | None = None) -> int:
    return RANKING.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
