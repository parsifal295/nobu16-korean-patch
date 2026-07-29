#!/usr/bin/env python3
"""Rank PK selector families after the consolidated post-292 wave 3."""

from __future__ import annotations

import argparse
import hashlib
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
    / "build_pk_next_selector_family_ranking_post_post292_wave2_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    DIALOGUE_WORKSTREAM
    / "build_runtime_vm_"
    "post_selector292_wave3_consolidated_checkpoint_v1.py"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector292_wave3_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    DIALOGUE_WORKSTREAM
    / "runtime_vm_integration."
    "post_selector292_wave3_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_dialogue_wave_"
    "post_selector292_wave3_consolidated_closure_v1.py"
)
CLOSURE_COVERAGE_PATH = (
    WORKSTREAM
    / "public"
    / "pk_dialogue_wave_post_selector292_wave3_"
    "consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    WORKSTREAM
    / "public"
    / "pk_dialogue_wave_post_selector292_wave3_"
    "consolidated_closure_promotion.v1.json"
)
PROGRESS_BUILDER_PATH = (
    DIALOGUE_WORKSTREAM
    / "build_progress_"
    "post_selector292_wave3_consolidated_delta_v1.py"
)
PROGRESS_PUBLIC_PATH = (
    DIALOGUE_WORKSTREAM
    / "progress.post_selector292_wave3_consolidated.source_free.v1.json"
)
PROGRESS_ALIAS_PATH = DIALOGUE_WORKSTREAM / "progress.source_free.v1.json"

DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_post292_wave3.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_post292_wave3.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-post292-wave3.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-post292-wave3-source-free.v1"
)
METHOD = (
    "post292_wave3_closure_checkpoint_progress_pending_reachable_0143_"
    "owned_excluded_seven_way_selector_ranking_with_pairwise_overlap"
)
WAVE_SELECTORS = (1132, 1042, 274)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "D1AEEB02BD36BB95BC1408BB3AAEDE59F4F6F04C95C90AF589600152E5F1FF8A"
)
EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "checkpoint_builder":
        "359D6F8FEF6F91A50041E1437EF941867CB2401A672C7F0535218F01E242D998",
    "checkpoint_private":
        "3AEE8906C75A77C5808A28D3BAD62509BA2A32FF69C80AA68FAEA3C99CA72FDE",
    "checkpoint_public":
        "6B8E2A8701A0FE248909DE9FB0C6F9F448B4C37F98CBA47370A9F04259D30359",
    "closure_builder":
        "293634B76696D3E2DEADFB82F94381C33F0E59EA373CE50BAC904E0A8B465722",
    "closure_coverage":
        "786E04A50D4E6DE44F7B09B9AB14A237FD24A8AFC796D2B608BE8A2508BC49F4",
    "closure_promotion":
        "86847F29A38D9AC9888F70DB9E02671C819ADBF134B9EE97DA89A8FDD0139D69",
    "progress_builder":
        "6CB967B57CBC2C1A3189FBA9A4F0442BA9DE45660C139D63F59EB8E8F8884C7D",
    "progress_immutable":
        "7BE116E17F8400C88EEA54304EE9B2BCEFE932C6D7643BA1CD44C675FD798333",
    "progress_alias":
        "7BE116E17F8400C88EEA54304EE9B2BCEFE932C6D7643BA1CD44C675FD798333",
}

EXPECTED_PK_CANDIDATE_SHA256: str | None = (
    "4B2A09C787802B073109DE00B280FFC7FAB69FCF91C8D800EADCA3F072BE3C20"
)
EXPECTED_PK_PENDING_ROWS = 5_999
EXPECTED_PK_PENDING_ROOTS: int | None = 3_977
EXPECTED_PK_PENDING_ROOT_SHA256: str | None = (
    "E1AFD9402127D71F97D21BADC676C260528F8464ADD99D1742985D2619B798B5"
)
EXPECTED_REACHABLE_CALL_TARGETS: int | None = 145
EXPECTED_OWNED_CALL_TARGETS: int | None = 41
EXPECTED_NON_SEVEN_WAY_TARGETS: int | None = 23
EXPECTED_ELIGIBLE_FAMILIES: int | None = 81
EXPECTED_ELIGIBLE_UNION_ROWS: int | None = 452
EXPECTED_ELIGIBLE_UNION_SHA256: str | None = (
    "149957ABEC5A89B3F0B8D5329B214AEB4AB8EB2349C63D1FB4E8C1FB3A4DE076"
)
EXPECTED_RECOMMENDED_SELECTOR: str | None = "0:754"
EXPECTED_RECOMMENDED_TERMINALS: tuple[str, ...] | None = (
    "0:2168",
    "0:2169",
    "0:2170",
    "0:2171",
    "0:2172",
    "0:2173",
    "0:2174",
)
EXPECTED_RECOMMENDED_PENDING_ROWS: int | None = 20
EXPECTED_RECOMMENDED_PENDING_ROOTS: int | None = 8
EXPECTED_RECOMMENDED_PENDING_SITES: int | None = 8
EXPECTED_RECOMMENDED_CANDIDATE_SITES: int | None = 29
EXPECTED_RECOMMENDED_SOURCE_SITES: int | None = 30
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES: int | None = 1
EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES: int | None = 0
EXPECTED_POINT_ESTIMATE: int | None = 13
EXPECTED_ESTIMATE_RANGE: tuple[int, int] | None = (0, 20)
EXPECTED_TOP_SIX_OVERLAP_SHA256: str | None = (
    "698BF311BD560D7AA7ACFFA30C4672A58A7B7A97E513A5BB16393CF36C409FD3"
)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "4AEE497E71537DD8C2F6FECB8F0F30EB8E3009F6A601C74B774DDF6D84FAAAC6"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "C8C8C39CFAAB85DF737C0E09F3CED69187D5C41529296A156AAAA89C6E6EDBF7"
)

EXPECTED_PROGRESS_TRANSITION = {
    "pending_before": 6_022,
    "pending_after": 5_999,
    "eligible_before": 46_781,
    "eligible_after": 46_804,
    "pk_promotions_before": 14_661,
    "pk_promotions_after": 14_684,
    "promoted_total_before": 30_312,
    "promoted_total_after": 30_335,
    "retranslated_before": 46_436,
    "retranslated_after": 46_459,
    "wave_promotions": 23,
}

RANKING_PIN_NAMES = (
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
    "EXPECTED_TOP_SIX_OVERLAP_SHA256",
    "EXPECTED_PRIVATE_FILE_SHA256",
    "EXPECTED_PUBLIC_FILE_SHA256",
)


class PostWave2RankingError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PostWave2RankingError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREDECESSOR = load_module(
    PREDECESSOR_BUILDER, "pk_post_post292_wave3_predecessor"
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
overlap_values = PREDECESSOR.overlap_values
add_pairwise_overlaps = PREDECESSOR.add_pairwise_overlaps
bootstrap_report = PREDECESSOR.bootstrap_report


def configure_ranking() -> None:
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
        "EXPECTED_LEDGER_SHA256":
            EXPECTED_INPUT_SHA256["checkpoint_private"],
        "EXPECTED_CHECKPOINT_PUBLIC_SHA256":
            EXPECTED_INPUT_SHA256["checkpoint_public"],
        "EXPECTED_PK_CANDIDATE_SHA256": EXPECTED_PK_CANDIDATE_SHA256,
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
        "EXPECTED_ELIGIBLE_UNION_ROWS": EXPECTED_ELIGIBLE_UNION_ROWS,
        "EXPECTED_ELIGIBLE_UNION_SHA256":
            EXPECTED_ELIGIBLE_UNION_SHA256,
        "EXPECTED_RECOMMENDED_SELECTOR": EXPECTED_RECOMMENDED_SELECTOR,
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
        "COMPARABLE_ACTUAL_PROMOTIONS": COMPARABLE_ACTUAL_PROMOTIONS,
        "COMPARABLE_PENDING_UPPER_BOUNDS":
            COMPARABLE_PENDING_UPPER_BOUNDS,
        "EXPECTED_POINT_ESTIMATE": EXPECTED_POINT_ESTIMATE,
        "EXPECTED_ESTIMATE_RANGE": EXPECTED_ESTIMATE_RANGE,
        "EXPECTED_PRIVATE_FILE_SHA256": EXPECTED_PRIVATE_FILE_SHA256,
        "EXPECTED_PUBLIC_FILE_SHA256": EXPECTED_PUBLIC_FILE_SHA256,
    }
    for name, value in values.items():
        setattr(RANKING, name, value)


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
    return tuple(values)


def observed_input_hashes() -> dict[str, str]:
    paths = input_paths()
    missing = [name for name, path in paths.items() if not path.is_file()]
    require(not missing, "post292 wave3 inputs absent: " + ",".join(missing))
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


def validate_handoffs(observed: Mapping[str, str], *, frozen: bool) -> None:
    require(
        sha256_file(PREDECESSOR_BUILDER)
        == EXPECTED_PREDECESSOR_BUILDER_SHA256,
        "post-wave2 ranking predecessor drifted",
    )
    if frozen:
        for name, digest in observed.items():
            require(
                digest == EXPECTED_INPUT_SHA256[name],
                f"post292 wave3 input drifted: {name}",
            )
    require(
        PROGRESS_ALIAS_PATH.read_bytes() == PROGRESS_PUBLIC_PATH.read_bytes(),
        "immutable progress and mutable alias differ",
    )
    checkpoint = load_source_free(CHECKPOINT_PUBLIC)
    coverage = load_source_free(CLOSURE_COVERAGE_PATH)
    promotion = load_source_free(CLOSURE_PROMOTION_PATH)
    progress = load_source_free(PROGRESS_PUBLIC_PATH)
    result = checkpoint["result"]
    transition = EXPECTED_PROGRESS_TRANSITION
    require(
        (
            result["runtime_review_pending"],
            result["fully_candidate_eligible"],
            result["pk_msggame_promotion_count"],
            result["promoted_total"],
        )
        == (
            transition["pending_after"],
            transition["eligible_after"],
            transition["pk_promotions_after"],
            transition["promoted_total_after"],
        ),
        "checkpoint progress totals drifted",
    )
    require(
        checkpoint["validation"]["full_integration_engine_invoked"] is False,
        "full integration rebuild was used",
    )
    require(
        promotion["result"]["promotions"]
        == transition["wave_promotions"]
        and promotion["result"]["pending_before"]
        == transition["pending_before"]
        and promotion["result"]["pending_after"]
        == transition["pending_after"],
        "wave3 closure transition drifted",
    )
    require(
        promotion["result"]["source_only_actions"] == 0
        and coverage["result"]["source_only_actions"] == 0,
        "source-only action appeared",
    )
    totals = progress["totals"]
    require(
        (
            totals["runtime_review_pending"],
            totals["fully_candidate_eligible"],
            totals["scope_classification_counts"]["retranslated"],
            progress["runtime_vm_integration"]["promoted_total"],
        )
        == (
            transition["pending_after"],
            transition["eligible_after"],
            transition["retranslated_after"],
            transition["promoted_total_after"],
        ),
        "progress artifact totals drifted",
    )


def relaxed_core_outputs() -> tuple[dict[str, Any], dict[str, Any]]:
    configure_ranking()
    observed = observed_input_hashes()
    RANKING.EXPECTED_LEDGER_SHA256 = observed["checkpoint_private"]
    RANKING.EXPECTED_CHECKPOINT_PUBLIC_SHA256 = observed["checkpoint_public"]
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
            "post-post292-wave3 ranking pins unresolved: "
            + ",".join(unresolved_pins()),
        )
    observed = observed_input_hashes()
    validate_handoffs(observed, frozen=not allow_unfrozen)
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
        artifact["post292_wave3_inputs"] = dict(observed)
        artifact["post292_wave3_transition"] = dict(
            EXPECTED_PROGRESS_TRANSITION
        )
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
