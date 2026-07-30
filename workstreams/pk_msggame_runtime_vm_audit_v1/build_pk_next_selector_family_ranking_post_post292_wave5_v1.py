#!/usr/bin/env python3
"""Rank PK selector families after the consolidated post-292 wave 5."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_WORKSTREAM = (
    REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
)
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"

PREDECESSOR_BUILDER = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_post292_wave4_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    DIALOGUE_WORKSTREAM
    / "build_runtime_vm_"
    "post_selector292_wave5_consolidated_checkpoint_v1.py"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector292_wave5_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    DIALOGUE_WORKSTREAM
    / "runtime_vm_integration."
    "post_selector292_wave5_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_dialogue_wave_"
    "post_selector292_wave5_consolidated_closure_v1.py"
)
CLOSURE_COVERAGE_PATH = (
    WORKSTREAM
    / "public"
    / "pk_dialogue_wave_post_selector292_wave5_"
    "consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    WORKSTREAM
    / "public"
    / "pk_dialogue_wave_post_selector292_wave5_"
    "consolidated_closure_promotion.v1.json"
)
PROGRESS_BUILDER_PATH = (
    DIALOGUE_WORKSTREAM
    / "build_progress_"
    "post_selector292_wave5_consolidated_delta_v1.py"
)
PROGRESS_PUBLIC_PATH = (
    DIALOGUE_WORKSTREAM
    / "progress.post_selector292_wave5_consolidated.source_free.v1.json"
)
PROGRESS_ALIAS_PATH = DIALOGUE_WORKSTREAM / "progress.source_free.v1.json"

DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_post292_wave5.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_post292_wave5.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-post292-wave5.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-post292-wave5-source-free.v1"
)
METHOD = (
    "post292_wave5_closure_checkpoint_progress_pending_reachable_0143_"
    "owned_excluded_seven_way_selector_ranking_with_pairwise_overlap"
)
WAVE_SELECTORS = (148, 904, 724)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "C9C283FB540888BE8897167B930FEB64552428C4BD0236EA1DE54467E67C76B6"
)
EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "checkpoint_builder":
        "6CDD2AD811840DA5A4EB7294C8DF8B94C62189A84978F16DFF16DA3F49D87F68",
    "checkpoint_private":
        "ABC78C74996A5C9467DB92C1EBB55A940A2A39099E9A12A5D565954D4AB68F12",
    "checkpoint_public":
        "D2928654B9CD246366567E5FF996EB0A58F9044962EADBB79F3921BA2ABC680A",
    "closure_builder":
        "D0DD4BCDF2AD641F1334149F46748B0F7D3966E2FEBBD8FFD78DAD6AE1065FFD",
    "closure_coverage":
        "8C21B4218759B5AB7F428EE621A5565C3844320A13B2D5D260D64B8CB2D61DF6",
    "closure_promotion":
        "4B2CC357762CB5AE498D600FED1EBAB9776889E796C73B1C31D9C34ED82A64C0",
    "progress_builder":
        "115CFA3D0AE0371EB169EDC164C80CEF345033AFA98788EF4DFFC6C11E7C25AA",
    "progress_immutable":
        "4814E2A465E01D9874DC63123C177C8C425C75D4657F0B04278809E1C788E97F",
    "progress_alias":
        "4814E2A465E01D9874DC63123C177C8C425C75D4657F0B04278809E1C788E97F",
}

EXPECTED_PK_CANDIDATE_SHA256: str | None = (
    "41CBC25028A3251C954597B2EA6797E503D8F8D6887D79C99BB7191FEBD5617F"
)
EXPECTED_PK_PENDING_ROWS: int | None = 5_956
EXPECTED_PK_PENDING_ROOTS: int | None = 3_960
EXPECTED_PK_PENDING_ROOT_SHA256: str | None = (
    "6ADDEC9D6654C6633C4FDB1E8AF71C2BAB5A70B2802866B2FEFEC6BE41CAB4BC"
)
EXPECTED_REACHABLE_CALL_TARGETS: int | None = 145
EXPECTED_OWNED_CALL_TARGETS: int | None = 47
EXPECTED_NON_SEVEN_WAY_TARGETS: int | None = 23
EXPECTED_ELIGIBLE_FAMILIES: int | None = 75
EXPECTED_ELIGIBLE_UNION_ROWS: int | None = 372
EXPECTED_ELIGIBLE_UNION_SHA256: str | None = (
    "9525504E8E787B117A5A6C845D2FE346C2A676FF9D314895707C68DCDD21E69A"
)
EXPECTED_RECOMMENDED_SELECTOR: str | None = "0:772"
EXPECTED_RECOMMENDED_TERMINALS: tuple[str, ...] | None = (
    "0:2189",
    "0:2190",
    "0:2191",
    "0:2192",
    "0:2193",
    "0:2194",
    "0:2195",
)
EXPECTED_RECOMMENDED_PENDING_ROWS: int | None = 15
EXPECTED_RECOMMENDED_PENDING_ROOTS: int | None = 5
EXPECTED_RECOMMENDED_PENDING_SITES: int | None = 5
EXPECTED_RECOMMENDED_CANDIDATE_SITES: int | None = 32
EXPECTED_RECOMMENDED_SOURCE_SITES: int | None = 33
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES: int | None = 1
EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES: int | None = 0
EXPECTED_POINT_ESTIMATE: int | None = 9
EXPECTED_ESTIMATE_RANGE: tuple[int, int] | None = (0, 15)
EXPECTED_TOP_SIX_OVERLAP_SHA256: str | None = (
    "62075BAC589C12E858471CF600725A16611D9BEB1EB312A600F21D78E2262D80"
)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "071D7F15C860B8F8D051C89815CFC591BBC65F7B8FE12D1C779796C6F38E21F7"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "29D3286D710C9B4072ECA71A18C7EC11270163315F7022227D02BAFCF234E46B"
)

EXPECTED_PROGRESS_TRANSITION: dict[str, int | None] = {
    "pending_before": 5_970,
    "pending_after": 5_956,
    "eligible_before": 46_833,
    "eligible_after": 46_847,
    "pk_promotions_before": 14_713,
    "pk_promotions_after": 14_727,
    "promoted_total_before": 30_364,
    "promoted_total_after": 30_378,
    "retranslated_before": 46_488,
    "retranslated_after": 46_502,
    "wave_promotions": 14,
}

RANKING_PIN_NAMES = (
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
    "EXPECTED_POINT_ESTIMATE",
    "EXPECTED_ESTIMATE_RANGE",
    "EXPECTED_TOP_SIX_OVERLAP_SHA256",
    "EXPECTED_PRIVATE_FILE_SHA256",
    "EXPECTED_PUBLIC_FILE_SHA256",
)


class PostWave5RankingError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PostWave5RankingError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREDECESSOR = load_module(
    PREDECESSOR_BUILDER, "pk_post_post292_wave5_predecessor"
)
RANKING = PREDECESSOR.RANKING
CORE_BUILD_OUTPUTS = PREDECESSOR.CORE_BUILD_OUTPUTS
OWNED_SELECTORS = tuple(PREDECESSOR.OWNED_SELECTORS) + WAVE_SELECTORS
COMPARABLE_ACTUAL_PROMOTIONS = dict(
    PREDECESSOR.COMPARABLE_ACTUAL_PROMOTIONS
)
COMPARABLE_PENDING_UPPER_BOUNDS = dict(
    PREDECESSOR.COMPARABLE_PENDING_UPPER_BOUNDS
)

sha256_file = RANKING.sha256_file
sha256_bytes = RANKING.sha256_bytes
serialized_json = RANKING.serialized_json
assert_source_free = RANKING.assert_source_free
add_pairwise_overlaps = PREDECESSOR.add_pairwise_overlaps
bootstrap_report = PREDECESSOR.bootstrap_report


def configure_predecessor_module() -> None:
    values = {
        "DEFAULT_STEAM_ROOT": DEFAULT_STEAM_ROOT,
        "DEFAULT_LEDGER": DEFAULT_LEDGER,
        "CHECKPOINT_PUBLIC": CHECKPOINT_PUBLIC,
        "DEFAULT_PRIVATE_OUTPUT": DEFAULT_PRIVATE_OUTPUT,
        "DEFAULT_PUBLIC_OUTPUT": DEFAULT_PUBLIC_OUTPUT,
        "PRIVATE_SCHEMA": PRIVATE_SCHEMA,
        "PUBLIC_SCHEMA": PUBLIC_SCHEMA,
        "METHOD": METHOD,
        "OWNED_SELECTORS": OWNED_SELECTORS,
        "EXPECTED_INPUT_SHA256": EXPECTED_INPUT_SHA256,
        "EXPECTED_PK_CANDIDATE_SHA256":
            EXPECTED_PK_CANDIDATE_SHA256,
        "EXPECTED_PK_PENDING_ROWS": EXPECTED_PK_PENDING_ROWS,
        "EXPECTED_PK_PENDING_ROOTS": EXPECTED_PK_PENDING_ROOTS,
        "EXPECTED_PK_PENDING_ROOT_SHA256":
            EXPECTED_PK_PENDING_ROOT_SHA256,
        "EXPECTED_REACHABLE_CALL_TARGETS":
            EXPECTED_REACHABLE_CALL_TARGETS,
        "EXPECTED_OWNED_CALL_TARGETS": EXPECTED_OWNED_CALL_TARGETS,
        "EXPECTED_NON_SEVEN_WAY_TARGETS":
            EXPECTED_NON_SEVEN_WAY_TARGETS,
        "EXPECTED_ELIGIBLE_FAMILIES": EXPECTED_ELIGIBLE_FAMILIES,
        "EXPECTED_ELIGIBLE_UNION_ROWS":
            EXPECTED_ELIGIBLE_UNION_ROWS,
        "EXPECTED_ELIGIBLE_UNION_SHA256":
            EXPECTED_ELIGIBLE_UNION_SHA256,
        "EXPECTED_RECOMMENDED_SELECTOR":
            EXPECTED_RECOMMENDED_SELECTOR,
        "EXPECTED_RECOMMENDED_TERMINALS":
            EXPECTED_RECOMMENDED_TERMINALS,
        "EXPECTED_RECOMMENDED_PENDING_ROWS":
            EXPECTED_RECOMMENDED_PENDING_ROWS,
        "EXPECTED_RECOMMENDED_PENDING_ROOTS":
            EXPECTED_RECOMMENDED_PENDING_ROOTS,
        "EXPECTED_RECOMMENDED_PENDING_SITES":
            EXPECTED_RECOMMENDED_PENDING_SITES,
        "EXPECTED_RECOMMENDED_CANDIDATE_SITES":
            EXPECTED_RECOMMENDED_CANDIDATE_SITES,
        "EXPECTED_RECOMMENDED_SOURCE_SITES":
            EXPECTED_RECOMMENDED_SOURCE_SITES,
        "EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES":
            EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES,
        "EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES":
            EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES,
        "COMPARABLE_ACTUAL_PROMOTIONS":
            COMPARABLE_ACTUAL_PROMOTIONS,
        "COMPARABLE_PENDING_UPPER_BOUNDS":
            COMPARABLE_PENDING_UPPER_BOUNDS,
        "EXPECTED_POINT_ESTIMATE": EXPECTED_POINT_ESTIMATE,
        "EXPECTED_ESTIMATE_RANGE": EXPECTED_ESTIMATE_RANGE,
        "EXPECTED_PRIVATE_FILE_SHA256":
            EXPECTED_PRIVATE_FILE_SHA256,
        "EXPECTED_PUBLIC_FILE_SHA256":
            EXPECTED_PUBLIC_FILE_SHA256,
    }
    paths = {
        "CHECKPOINT_BUILDER_PATH": CHECKPOINT_BUILDER_PATH,
        "CLOSURE_BUILDER_PATH": CLOSURE_BUILDER_PATH,
        "CLOSURE_COVERAGE_PATH": CLOSURE_COVERAGE_PATH,
        "CLOSURE_PROMOTION_PATH": CLOSURE_PROMOTION_PATH,
        "PROGRESS_BUILDER_PATH": PROGRESS_BUILDER_PATH,
        "PROGRESS_PUBLIC_PATH": PROGRESS_PUBLIC_PATH,
        "PROGRESS_ALIAS_PATH": PROGRESS_ALIAS_PATH,
    }
    for name, value in {**values, **paths}.items():
        setattr(PREDECESSOR, name, value)


configure_predecessor_module()


def configure_ranking() -> None:
    configure_predecessor_module()
    PREDECESSOR.configure_predecessor_module()
    PREDECESSOR.PREDECESSOR.configure_ranking()


def input_paths() -> dict[str, Path]:
    return {
        "checkpoint_builder": CHECKPOINT_BUILDER_PATH,
        "checkpoint_private": DEFAULT_LEDGER,
        "checkpoint_public": CHECKPOINT_PUBLIC,
        "closure_builder": CLOSURE_BUILDER_PATH,
        "closure_coverage": CLOSURE_COVERAGE_PATH,
        "closure_promotion": CLOSURE_PROMOTION_PATH,
        "progress_builder": PROGRESS_BUILDER_PATH,
        "progress_immutable": PROGRESS_PUBLIC_PATH,
        "progress_alias": PROGRESS_ALIAS_PATH,
    }


def unresolved_pins() -> tuple[str, ...]:
    values = [
        f"EXPECTED_INPUT_SHA256[{name}]"
        for name, value in EXPECTED_INPUT_SHA256.items()
        if value is None
    ]
    values.extend(
        name for name in RANKING_PIN_NAMES if globals()[name] is None
    )
    values.extend(
        f"EXPECTED_PROGRESS_TRANSITION[{name}]"
        for name, value in EXPECTED_PROGRESS_TRANSITION.items()
        if value is None
    )
    return tuple(values)


def observed_input_hashes() -> dict[str, str]:
    paths = input_paths()
    missing = [name for name, path in paths.items() if not path.is_file()]
    require(not missing, "post292 wave5 inputs absent: " + ",".join(missing))
    return {name: sha256_file(path) for name, path in paths.items()}


def load_source_free(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="ascii"))
    assert_source_free(value)
    require(
        value.get("steam_write_performed") is False
        or (
            path in {PROGRESS_PUBLIC_PATH, PROGRESS_ALIAS_PATH}
            and value["runtime_vm_integration"]["steam_write_performed"]
                is False
        ),
        f"Steam write guard failed: {path.name}",
    )
    return value


def validate_handoffs(
    observed: Mapping[str, str], *, frozen: bool
) -> dict[str, int]:
    require(
        sha256_file(PREDECESSOR_BUILDER)
        == EXPECTED_PREDECESSOR_BUILDER_SHA256,
        "post-wave4 ranking predecessor drifted",
    )
    if frozen:
        for name, digest in observed.items():
            require(
                digest == EXPECTED_INPUT_SHA256[name],
                f"post292 wave5 input drifted: {name}",
            )
    require(
        PROGRESS_ALIAS_PATH.read_bytes() == PROGRESS_PUBLIC_PATH.read_bytes(),
        "immutable progress and mutable alias differ",
    )
    checkpoint = load_source_free(CHECKPOINT_PUBLIC)
    coverage = load_source_free(CLOSURE_COVERAGE_PATH)
    promotion = load_source_free(CLOSURE_PROMOTION_PATH)
    progress = load_source_free(PROGRESS_PUBLIC_PATH)
    require(
        checkpoint["validation"]["full_integration_engine_invoked"] is False,
        "full integration rebuild was used",
    )
    require(
        promotion["result"]["source_only_actions"] == 0
        and coverage["result"]["source_only_actions"] == 0,
        "source-only action appeared",
    )
    result = checkpoint["result"]
    totals = progress["totals"]
    wave_promotions = int(promotion["result"]["promotions"])
    transition = {
        "pending_before":
            int(promotion["result"]["pending_before"]),
        "pending_after": int(result["runtime_review_pending"]),
        "eligible_before":
            int(result["fully_candidate_eligible"]) - wave_promotions,
        "eligible_after": int(result["fully_candidate_eligible"]),
        "pk_promotions_before":
            int(result["pk_msggame_promotion_count"]) - wave_promotions,
        "pk_promotions_after":
            int(result["pk_msggame_promotion_count"]),
        "promoted_total_before":
            int(result["promoted_total"]) - wave_promotions,
        "promoted_total_after": int(result["promoted_total"]),
        "retranslated_before":
            int(totals["scope_classification_counts"]["retranslated"])
            - wave_promotions,
        "retranslated_after":
            int(totals["scope_classification_counts"]["retranslated"]),
        "wave_promotions": wave_promotions,
    }
    require(
        transition["pending_after"]
        == int(promotion["result"]["pending_after"])
        and totals["runtime_review_pending"]
        == transition["pending_after"]
        and totals["fully_candidate_eligible"]
        == transition["eligible_after"]
        and progress["runtime_vm_integration"]["promoted_total"]
        == transition["promoted_total_after"],
        "wave5 checkpoint/closure/progress transition drifted",
    )
    if frozen:
        require(
            transition == EXPECTED_PROGRESS_TRANSITION,
            "wave5 frozen transition pins drifted",
        )
    return transition


def relaxed_core_outputs() -> tuple[dict[str, Any], dict[str, Any]]:
    configure_predecessor_module()
    configure_ranking()
    observed = observed_input_hashes()
    RANKING.EXPECTED_LEDGER_SHA256 = observed["checkpoint_private"]
    RANKING.EXPECTED_CHECKPOINT_PUBLIC_SHA256 = observed[
        "checkpoint_public"
    ]
    replacements, _pending = RANKING.load_official_ledger(DEFAULT_LEDGER)
    current_path = DEFAULT_STEAM_ROOT / "MSG_PK" / "JP" / "msggame.bin"
    candidate = RANKING.ENGINE.rebuild_packed_with_literals(
        current_path.read_bytes(), replacements
    )
    RANKING.EXPECTED_PK_CANDIDATE_SHA256 = sha256_bytes(candidate)
    original_require = RANKING.require
    try:
        RANKING.require = lambda _condition, _message: None
        return CORE_BUILD_OUTPUTS(
            steam_root=DEFAULT_STEAM_ROOT,
            ledger_path=DEFAULT_LEDGER,
            checkpoint_public_path=CHECKPOINT_PUBLIC,
        )
    finally:
        RANKING.require = original_require
        configure_ranking()


def build_outputs(
    *, allow_unfrozen: bool = False
) -> tuple[dict[str, Any], dict[str, Any], dict[str, str]]:
    if not allow_unfrozen:
        require(
            not unresolved_pins(),
            "post-post292-wave5 ranking pins unresolved: "
            + ",".join(unresolved_pins()),
        )
    observed = observed_input_hashes()
    transition = validate_handoffs(
        observed, frozen=not allow_unfrozen
    )
    configure_predecessor_module()
    configure_ranking()
    if allow_unfrozen:
        private, public = relaxed_core_outputs()
    else:
        private, public = CORE_BUILD_OUTPUTS(
            steam_root=DEFAULT_STEAM_ROOT,
            ledger_path=DEFAULT_LEDGER,
            checkpoint_public_path=CHECKPOINT_PUBLIC,
        )
    eligible = {row["selector_coordinate"] for row in public["ranking"]}
    require(
        not eligible & {f"0:{selector}" for selector in OWNED_SELECTORS},
        "an owned selector reappeared in the ranking",
    )
    overlap_sha256 = add_pairwise_overlaps(private, public)
    for artifact in (private, public):
        artifact["post292_wave5_inputs"] = dict(observed)
        artifact["post292_wave5_transition"] = transition
    public["privacy"]["shared_integration_mutated"] = False
    public["privacy"]["steam_write_performed"] = False
    assert_source_free(public)
    if not allow_unfrozen:
        require(
            overlap_sha256 == EXPECTED_TOP_SIX_OVERLAP_SHA256,
            "top-six overlap contract drifted",
        )
    return private, public, observed


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--bootstrap", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    private, public, observed = build_outputs(
        allow_unfrozen=args.bootstrap
    )
    private_bytes = serialized_json(private)
    public_bytes = serialized_json(public)
    if args.bootstrap:
        print(
            json.dumps(
                bootstrap_report(private, public, observed),
                ensure_ascii=True,
                sort_keys=True,
            )
        )
        return 0
    require(
        sha256_bytes(private_bytes) == EXPECTED_PRIVATE_FILE_SHA256,
        "private ranking digest drifted",
    )
    require(
        sha256_bytes(public_bytes) == EXPECTED_PUBLIC_FILE_SHA256,
        "public ranking digest drifted",
    )
    if args.write:
        require(
            DEFAULT_PRIVATE_OUTPUT.resolve().is_relative_to(
                DIALOGUE_TMP.resolve()
            ),
            "private output must remain below dialogue tmp",
        )
        DEFAULT_PRIVATE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_PUBLIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_PRIVATE_OUTPUT.write_bytes(private_bytes)
        DEFAULT_PUBLIC_OUTPUT.write_bytes(public_bytes)
    else:
        require(
            DEFAULT_PRIVATE_OUTPUT.read_bytes() == private_bytes,
            "private ranking artifact drifted",
        )
        require(
            DEFAULT_PUBLIC_OUTPUT.read_bytes() == public_bytes,
            "public ranking artifact drifted",
        )
    print(
        json.dumps(
            {
                "eligible_families": len(public["ranking"]),
                "private_sha256": sha256_bytes(private_bytes),
                "public_sha256": sha256_bytes(public_bytes),
                "recommended_selector":
                    public["recommendation"]["selector_coordinate"],
                "steam_write_performed": False,
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
