#!/usr/bin/env python3
"""Rank remaining PK selector families on the selector-322 checkpoint."""

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
    / "build_pk_next_selector_family_ranking_post_selector742_consolidated_v1.py"
)
DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector322_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "runtime_vm_integration."
    "post_selector322_consolidated_checkpoint.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_selector322_consolidated.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_selector322_consolidated.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector322-consolidated.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-selector322-consolidated-source-free.v1"
)
METHOD = (
    "selector322_checkpoint_pending_reachable_0143_"
    "owned_excluded_seven_way_selector_ranking"
)
OWNED_SELECTORS = (
    538, 568, 1096, 1174, 610, 550, 748, 1126, 142, 514, 628, 1198,
    178, 1090, 760, 508, 742, 322,
)

EXPECTED_LEDGER_SHA256 = (
    "9A7E135544FA2F2A02A0D2B4941159CB92A3E4A495AF72B6CB335DE371351343"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256 = (
    "3C245CE82733F50F08E61B05A165B1038C4D5BBA5D3DAD38D46933B392101642"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "D0739EBB2E00B9034071165D00CA0D5E08D5F30A6400C8FF38CDA2867BA0203E"
)
EXPECTED_PK_PENDING_ROWS = 6_310
EXPECTED_PK_PENDING_ROOTS = 4_106
EXPECTED_PK_PENDING_ROOT_SHA256 = (
    "3CC7F8FFBC02B70B863ADDF28A61D6D660865A9BF0EDF6F147504A4A12A54F32"
)
EXPECTED_REACHABLE_CALL_TARGETS = 150
EXPECTED_OWNED_CALL_TARGETS = 20
EXPECTED_NON_SEVEN_WAY_TARGETS = 23
EXPECTED_ELIGIBLE_FAMILIES = 107
EXPECTED_ELIGIBLE_UNION_ROWS = 980
EXPECTED_ELIGIBLE_UNION_SHA256 = (
    "BD88DAB79201BBDB459BB3E4A254FF4BD9B70ECC8D8B53C3D93AE0A2CEDEED22"
)
EXPECTED_RECOMMENDED_SELECTOR = "0:1162"
EXPECTED_RECOMMENDED_TERMINALS = tuple(
    f"0:{record_id}" for record_id in range(1902, 1909)
)
EXPECTED_RECOMMENDED_PENDING_ROWS = 55
EXPECTED_RECOMMENDED_PENDING_ROOTS = 23
EXPECTED_RECOMMENDED_PENDING_SITES = 23
EXPECTED_RECOMMENDED_CANDIDATE_SITES = 61
EXPECTED_RECOMMENDED_SOURCE_SITES = 66
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES = 5
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
    508: 0,
    742: 6,
    322: 25,
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
}
EXPECTED_POINT_ESTIMATE = 38
EXPECTED_ESTIMATE_RANGE = (0, 54)

# Frozen after the first reproducible write/check cycle.
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "256EE354A7659F2F4815561AAA49A79072234512F265C18836BEBCDAB8370570"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "C6DFC4A15CE9070C4C5605D9768210C4DB590D6992A7D931AA1618B7554391D5"
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
    "pk_next_selector_post_322_predecessor_helpers_v1",
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
assert_source_free = RANKING.assert_source_free
CORE_BUILD_OUTPUTS = PREDECESSOR_WRAPPER.CORE_BUILD_OUTPUTS


def build_outputs(*args: Any, **kwargs: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    private, public = CORE_BUILD_OUTPUTS(*args, **kwargs)
    eligible = {row["selector_coordinate"] for row in public["ranking"]}
    require(
        not eligible & {f"0:{selector}" for selector in OWNED_SELECTORS},
        "an owned or zero-closure selector reappeared in the ranking",
    )
    return private, public


RANKING.build_outputs = build_outputs


def main(argv: Sequence[str] | None = None) -> int:
    return RANKING.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
