#!/usr/bin/env python3
"""DRAFT: rank PK selector families after consolidated post-292 wave 6.

Wave-6 result pins are deliberately unresolved.  Do not promote this draft
until the wave-6 closure/checkpoint/progress artifacts are frozen.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
REPO = next(
    parent
    for parent in SCRIPT.parents
    if (
        parent
        / "workstreams"
        / "pk_msggame_runtime_vm_audit_v1"
    ).is_dir()
)
WORKSTREAM = REPO / "workstreams" / "pk_msggame_runtime_vm_audit_v1"
DIALOGUE_WORKSTREAM = (
    REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
)
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"

PREDECESSOR_BUILDER = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_post292_wave5_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    DIALOGUE_WORKSTREAM
    / "build_runtime_vm_"
    "post_selector292_wave6_consolidated_checkpoint_v1.py"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector292_wave6_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    DIALOGUE_WORKSTREAM
    / "runtime_vm_integration."
    "post_selector292_wave6_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_dialogue_wave_"
    "post_selector292_wave6_consolidated_closure_v1.py"
)
CLOSURE_COVERAGE_PATH = (
    WORKSTREAM
    / "public"
    / "pk_dialogue_wave_post_selector292_wave6_"
    "consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    WORKSTREAM
    / "public"
    / "pk_dialogue_wave_post_selector292_wave6_"
    "consolidated_closure_promotion.v1.json"
)
PROGRESS_BUILDER_PATH = (
    DIALOGUE_WORKSTREAM
    / "build_progress_"
    "post_selector292_wave6_consolidated_delta_v1.py"
)
PROGRESS_PUBLIC_PATH = (
    DIALOGUE_WORKSTREAM
    / "progress.post_selector292_wave6_consolidated.source_free.v1.json"
)
PROGRESS_ALIAS_PATH = DIALOGUE_WORKSTREAM / "progress.source_free.v1.json"

DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_post292_wave6.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_post292_wave6.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-post292-wave6.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-post292-wave6-source-free.v1"
)
METHOD = (
    "post292_wave6_closure_checkpoint_progress_pending_reachable_0143_"
    "owned_excluded_seven_way_selector_ranking_with_pairwise_overlap"
)
WAVE_SELECTORS = (
    772, 160, 616, 280, 1204, 256, 634, 778, 298,
    898, 1036, 1072, 70, 850, 862, 928, 940, 202,
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "DE1082D629B91D52EAA946005D7783E31506A963D7D9793E35D4F292CF6C710E"
)
EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "checkpoint_builder":
        "E595CB9AF6F48F494BBF8351774BDC2A04BE12EB0086B831A580057433E87B40",
    "checkpoint_private":
        "7016A0AB5EFD5B0FD223818F860B5757A914188A8EE58C2AD3BE6D14BC393F61",
    "checkpoint_public":
        "987E9644DD5DC235C74E52858546C9196BA15203871A7FE9DDEBF121697435F3",
    "closure_builder":
        "742158D5379CC104C838AAC7BDB18ADEE769EC63FF56BE814E44DE9B15D3241A",
    "closure_coverage":
        "9E0593B6908D0DF4CF638D396642DE8CC42871FB39EFAE82349E87023CDA049F",
    "closure_promotion":
        "6417063FB6339F9A254F4575F529AED44ACDA5E9FBD1F378EB7309D371F7E136",
    "progress_builder":
        "CB288CF5C509B9FBC252A3FACCA5080080E197EF5547F2C4B38F0BF3D1B4D4B2",
    "progress_immutable":
        "58A10BDE56CAC75D6B57CC6E2BACFD7BE49B506D2350E6402E7FCA16CE6A44F4",
    "progress_alias":
        "58A10BDE56CAC75D6B57CC6E2BACFD7BE49B506D2350E6402E7FCA16CE6A44F4",
}

EXPECTED_PK_CANDIDATE_SHA256: str | None = (
    "DC8F4F47EA9DDD81BA6DD788ECE55FD303FA5C228925E6E947E4E7F5C1007804"
)
EXPECTED_PK_PENDING_ROWS: int | None = 5_922
EXPECTED_PK_PENDING_ROOTS: int | None = 3_946
EXPECTED_PK_PENDING_ROOT_SHA256: str | None = (
    "FD9CB041DE3C59E574CF0251E1DA78313BDC817EFD6658FE9CC06130E67AF4D2"
)
EXPECTED_REACHABLE_CALL_TARGETS: int | None = 142
EXPECTED_OWNED_CALL_TARGETS: int | None = 65
EXPECTED_NON_SEVEN_WAY_TARGETS: int | None = 22
EXPECTED_ELIGIBLE_FAMILIES: int | None = 55
EXPECTED_ELIGIBLE_UNION_ROWS: int | None = 216
EXPECTED_ELIGIBLE_UNION_SHA256: str | None = (
    "E16A142185A2E570CD3B84602BD1A1C11F038C8961DD031270D9EAC7BB7E03C0"
)
EXPECTED_RECOMMENDED_SELECTOR: str | None = "0:700"
EXPECTED_RECOMMENDED_TERMINALS: tuple[str, ...] | None = (
    "0:2105", "0:2106", "0:2107", "0:2108",
    "0:2109", "0:2110", "0:2111",
)
EXPECTED_RECOMMENDED_PENDING_ROWS: int | None = 12
EXPECTED_RECOMMENDED_PENDING_ROOTS: int | None = 7
EXPECTED_RECOMMENDED_PENDING_SITES: int | None = 7
EXPECTED_RECOMMENDED_CANDIDATE_SITES: int | None = 78
EXPECTED_RECOMMENDED_SOURCE_SITES: int | None = 82
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES: int | None = 4
EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES: int | None = 0
EXPECTED_POINT_ESTIMATE: int | None = 8
EXPECTED_ESTIMATE_RANGE: tuple[int, int] | None = (0, 12)
EXPECTED_TOP_SIX_OVERLAP_SHA256: str | None = (
    "8602D98053BBED4B8569A0B4DF61A0F53642EEAEC214AF5D70553FD446FFFF07"
)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "FED6181AE978C3A476F6DEDEDC80BF995B3B79A740662BFCFBAA6D96E962169A"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "4C573A461A9E0FF3C1D0056982375434D4C1453E32D3A22B649C79A2D7DB42AA"
)

EXPECTED_PROGRESS_TRANSITION: dict[str, int | None] = {
    "pending_before": 5_956,
    "pending_after": 5_922,
    "eligible_before": 46_847,
    "eligible_after": 46_881,
    "pk_promotions_before": 14_727,
    "pk_promotions_after": 14_761,
    "promoted_total_before": 30_378,
    "promoted_total_after": 30_412,
    "retranslated_before": 46_502,
    "retranslated_after": 46_536,
    "wave_promotions": 34,
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


class PostWave6RankingError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PostWave6RankingError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREDECESSOR = load_module(
    PREDECESSOR_BUILDER, "pk_post_post292_wave6_predecessor"
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
    PREDECESSOR.PREDECESSOR.configure_predecessor_module()
    PREDECESSOR.PREDECESSOR.PREDECESSOR.configure_ranking()


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
    require(not missing, "post292 wave6 inputs absent: " + ",".join(missing))
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
        "post-wave5 ranking predecessor drifted",
    )
    if frozen:
        for name, digest in observed.items():
            require(
                digest == EXPECTED_INPUT_SHA256[name],
                f"post292 wave6 input drifted: {name}",
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
        "wave6 checkpoint/closure/progress transition drifted",
    )
    if frozen:
        require(
            transition == EXPECTED_PROGRESS_TRANSITION,
            "wave6 frozen transition pins drifted",
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
    original_require = RANKING.require
    try:
        RANKING.require = lambda _condition, _message: None
        replacements, _pending = RANKING.load_official_ledger(DEFAULT_LEDGER)
        current_path = (
            DEFAULT_STEAM_ROOT / "MSG_PK" / "JP" / "msggame.bin"
        )
        candidate = RANKING.ENGINE.rebuild_packed_with_literals(
            current_path.read_bytes(), replacements
        )
        RANKING.EXPECTED_PK_CANDIDATE_SHA256 = sha256_bytes(candidate)
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
            "post-post292-wave6 ranking pins unresolved: "
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
        artifact["post292_wave6_inputs"] = dict(observed)
        artifact["post292_wave6_transition"] = transition
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


def draft_bootstrap_report(
    private: Mapping[str, Any],
    public: Mapping[str, Any],
    observed: Mapping[str, str],
) -> dict[str, Any]:
    """Emit every unresolved constant needed to freeze this draft."""
    report = bootstrap_report(private, public, observed)
    scope = public["scope"]
    recommendation = public["recommendation"]
    tractability = recommendation["tractability"]
    top_private = next(
        row
        for row in private["direct_targets"]
        if row["target_coordinate"] == recommendation["selector_coordinate"]
    )
    candidate_sites = set(top_private["candidate_call_sites"])
    source_sites = set(top_private["source_call_sites"])
    report["freeze_constants"] = {
        "EXPECTED_INPUT_SHA256": dict(observed),
        "EXPECTED_PK_CANDIDATE_SHA256":
            private["inputs"]["pk_rebuilt_candidate_sha256"],
        "EXPECTED_PK_PENDING_ROWS": scope["official_pending_rows"],
        "EXPECTED_PK_PENDING_ROOTS": scope["official_pending_root_count"],
        "EXPECTED_PK_PENDING_ROOT_SHA256":
            scope["official_pending_root_sha256"],
        "EXPECTED_REACHABLE_CALL_TARGETS":
            scope["reachable_0143_call_target_count"],
        "EXPECTED_OWNED_CALL_TARGETS":
            public["exclusions"]["already_owned_reachable_call_targets"],
        "EXPECTED_NON_SEVEN_WAY_TARGETS":
            public["exclusions"]["non_seven_way_reachable_call_targets"],
        "EXPECTED_ELIGIBLE_FAMILIES":
            scope["eligible_fixed_seven_way_family_count"],
        "EXPECTED_ELIGIBLE_UNION_ROWS":
            scope["eligible_family_current_pending_union_rows"],
        "EXPECTED_ELIGIBLE_UNION_SHA256":
            scope["eligible_family_current_pending_union_coordinate_sha256"],
        "EXPECTED_RECOMMENDED_SELECTOR":
            recommendation["selector_coordinate"],
        "EXPECTED_RECOMMENDED_TERMINALS":
            top_private["jump_closure"]["terminal_coordinates"],
        "EXPECTED_RECOMMENDED_PENDING_ROWS":
            top_private["current_pending_row_count"],
        "EXPECTED_RECOMMENDED_PENDING_ROOTS":
            top_private["reachable_pending_root_count"],
        "EXPECTED_RECOMMENDED_PENDING_SITES":
            tractability["direct_pending_call_site_count"],
        "EXPECTED_RECOMMENDED_CANDIDATE_SITES":
            tractability["candidate_call_site_count"],
        "EXPECTED_RECOMMENDED_SOURCE_SITES":
            top_private["source_call_site_count"],
        "EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES":
            len(source_sites - candidate_sites),
        "EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES":
            len(candidate_sites - source_sites),
        "EXPECTED_POINT_ESTIMATE":
            recommendation["estimated_actual_promotion_rows"],
        "EXPECTED_ESTIMATE_RANGE":
            recommendation["estimated_actual_promotion_range"],
        "EXPECTED_TOP_SIX_OVERLAP_SHA256":
            private["top_six_pairwise_overlap"]["sha256"],
        "EXPECTED_PRIVATE_FILE_SHA256":
            sha256_bytes(serialized_json(private)),
        "EXPECTED_PUBLIC_FILE_SHA256":
            sha256_bytes(serialized_json(public)),
        "EXPECTED_PROGRESS_TRANSITION":
            private["post292_wave6_transition"],
    }
    return report


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
                draft_bootstrap_report(private, public, observed),
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
