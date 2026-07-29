#!/usr/bin/env python3
"""Rank PK selector families after the consolidated post-292 wave 1."""

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
    / "build_pk_next_selector_family_ranking_"
    "post_selector292_consolidated_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    DIALOGUE_WORKSTREAM
    / "build_runtime_vm_"
    "post_selector292_wave1_consolidated_checkpoint_v1.py"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector292_wave1_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    DIALOGUE_WORKSTREAM
    / "runtime_vm_integration."
    "post_selector292_wave1_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_dialogue_wave_"
    "post_selector292_consolidated_closure_v1.py"
)
CLOSURE_COVERAGE_PATH = (
    WORKSTREAM
    / "public"
    / "pk_dialogue_wave_post_selector292_"
    "consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    WORKSTREAM
    / "public"
    / "pk_dialogue_wave_post_selector292_"
    "consolidated_closure_promotion.v1.json"
)
PROGRESS_BUILDER_PATH = (
    DIALOGUE_WORKSTREAM
    / "build_progress_"
    "post_selector292_wave1_consolidated_delta_v1.py"
)
PROGRESS_PUBLIC_PATH = (
    DIALOGUE_WORKSTREAM
    / "progress.post_selector292_wave1_consolidated.source_free.v1.json"
)
PROGRESS_ALIAS_PATH = DIALOGUE_WORKSTREAM / "progress.source_free.v1.json"

DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_post292_wave1.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_post292_wave1.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-post292-wave1.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-post292-wave1-source-free.v1"
)
METHOD = (
    "post292_wave1_closure_checkpoint_progress_pending_reachable_0143_"
    "owned_excluded_seven_way_selector_ranking_with_pairwise_overlap"
)
WAVE_SELECTORS = (286, 190, 736)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "5EECFCF4569D016F0433A81BD6441CA69EAA0FEF8A4A3A59B206F9B4ACBBE7F1"
)
EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "checkpoint_builder":
        "A74174C263654B8314E72C854B512B08D9CCE3BBF32696378A078B445C40A5C2",
    "checkpoint_private":
        "3A49375034F28AE3AB088D7A22DDCEE6252CA4C45F67B3B57F32FC449DF2BEFF",
    "checkpoint_public":
        "71930E0261038636E8B20D0E03C577A98B4E09E160C10429E68D88B2F88A4331",
    "closure_builder":
        "5E1E0D9FAFC2BC99ADA1577D07FB2A66FE2F9004F489D98FB1DD91CB5D5BCA7D",
    "closure_coverage":
        "52B908B14C78754B7D4E8900D55F6F3912938FA3D5178C8AC22560E6B740BDF4",
    "closure_promotion":
        "1DBBFDFC7B1CF7D189B04176698BDDDED5C2C09CD7B7B6CAB532D8DA66A0B887",
    "progress_builder":
        "03BB2894B0DBBA9DD387087BA0C292F183CD7CBBF7F4DE07C49E6D86E50BD1FE",
    "progress_immutable":
        "D77906D6319E1F037E7F3C54892DDDCE3A5268B6EBACD07A960509D01D41D528",
    "progress_alias":
        "D77906D6319E1F037E7F3C54892DDDCE3A5268B6EBACD07A960509D01D41D528",
}

EXPECTED_PK_CANDIDATE_SHA256: str | None = (
    "C47390C28DE697CAD3F57A72A079F4D8CEA897F6E343CFCE704851BCC3507060"
)
EXPECTED_PK_PENDING_ROWS = 6_084
EXPECTED_PK_PENDING_ROOTS: int | None = 4_011
EXPECTED_PK_PENDING_ROOT_SHA256: str | None = (
    "C7448C64D58D2FEE9ACFBBC5839DE655507B9A562EEE5B77EAB2B1A04D0B248A"
)
EXPECTED_REACHABLE_CALL_TARGETS: int | None = 148
EXPECTED_OWNED_CALL_TARGETS: int | None = 35
EXPECTED_NON_SEVEN_WAY_TARGETS: int | None = 23
EXPECTED_ELIGIBLE_FAMILIES: int | None = 90
EXPECTED_ELIGIBLE_UNION_ROWS: int | None = 568
EXPECTED_ELIGIBLE_UNION_SHA256: str | None = (
    "62BCDCFCDBE6FED4A48C72F16C4506F70826143CA78AB55DA0349E2966D2804D"
)
EXPECTED_RECOMMENDED_SELECTOR: str | None = "0:1048"
EXPECTED_RECOMMENDED_TERMINALS: tuple[str, ...] | None = (
    "0:2525",
    "0:2526",
    "0:2527",
    "0:2528",
    "0:2529",
    "0:2530",
    "0:2531",
)
EXPECTED_RECOMMENDED_PENDING_ROWS: int | None = 31
EXPECTED_RECOMMENDED_PENDING_ROOTS: int | None = 13
EXPECTED_RECOMMENDED_PENDING_SITES: int | None = 13
EXPECTED_RECOMMENDED_CANDIDATE_SITES: int | None = 21
EXPECTED_RECOMMENDED_SOURCE_SITES: int | None = 22
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES: int | None = 1
EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES: int | None = 0
EXPECTED_POINT_ESTIMATE: int | None = 20
EXPECTED_ESTIMATE_RANGE: tuple[int, int] | None = (0, 30)
EXPECTED_TOP_SIX_OVERLAP_SHA256: str | None = (
    "09B1995797D1F603D1C9D2C1DF08A61108651AFF293B97F21542AD60A28BD758"
)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "F9B4FA36CE51443CD7BC034572DF63C701C10483B31E1A6CA6D1427A6D4B363B"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "EB1DAE24ACE692F17B69A94701B5B8093A05D6D0AB3F4C0DD4D5BCFC5873480B"
)

EXPECTED_PROGRESS_TRANSITION = {
    "pending_before": 6_130,
    "pending_after": 6_084,
    "eligible_before": 46_673,
    "eligible_after": 46_719,
    "pk_promotions_before": 14_553,
    "pk_promotions_after": 14_599,
    "promoted_total_before": 30_204,
    "promoted_total_after": 30_250,
    "retranslated_before": 46_328,
    "retranslated_after": 46_374,
    "wave_promotions": 46,
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


class PostWaveRankingError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PostWaveRankingError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREDECESSOR = load_module(
    PREDECESSOR_BUILDER, "pk_post_post292_wave1_predecessor"
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


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest().upper()


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
    require(not missing, "post292 wave1 inputs absent: " + ",".join(missing))
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
        "post-selector292 ranking predecessor drifted",
    )
    if frozen:
        for name, digest in observed.items():
            require(
                digest == EXPECTED_INPUT_SHA256[name],
                f"post292 wave1 input drifted: {name}",
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
        == transition["wave_promotions"],
        "wave promotion count drifted",
    )
    require(
        promotion["result"]["pending_before"]
        == transition["pending_before"]
        and promotion["result"]["pending_after"]
        == transition["pending_after"],
        "closure pending transition drifted",
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


def overlap_values(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> dict[str, list[str]]:
    left_candidate = set(map(str, left["candidate_call_sites"]))
    right_candidate = set(map(str, right["candidate_call_sites"]))
    left_source = set(map(str, left["source_call_sites"]))
    right_source = set(map(str, right["source_call_sites"]))
    return {
        "candidate_call_sites":
            sorted(left_candidate & right_candidate, key=RANKING.site_key),
        "pending_coordinates":
            sorted(
                set(map(str, left["current_pending_coordinates"]))
                & set(map(str, right["current_pending_coordinates"])),
                key=RANKING.parse_coordinate,
            ),
        "reachable_pending_roots":
            sorted(
                set(map(str, left["reachable_pending_roots"]))
                & set(map(str, right["reachable_pending_roots"])),
                key=RANKING.parse_root,
            ),
        "source_only_call_sites":
            sorted(
                (left_source - left_candidate)
                & (right_source - right_candidate),
                key=RANKING.site_key,
            ),
        "terminal_coordinates":
            sorted(
                set(
                    map(
                        str,
                        left["jump_closure"]["terminal_coordinates"],
                    )
                )
                & set(
                    map(
                        str,
                        right["jump_closure"]["terminal_coordinates"],
                    )
                ),
                key=RANKING.parse_root,
            ),
    }


def add_pairwise_overlaps(
    private: dict[str, Any], public: dict[str, Any]
) -> str:
    direct = {
        str(row["target_coordinate"]): row
        for row in private["direct_targets"]
    }
    ranked = [
        str(row["selector_coordinate"]) for row in public["ranking"][:6]
    ]
    private_rows = []
    public_rows = []
    for left_index, left_coordinate in enumerate(ranked):
        for right_coordinate in ranked[left_index + 1:]:
            values = overlap_values(
                direct[left_coordinate], direct[right_coordinate]
            )
            counts = {
                name: len(coordinates)
                for name, coordinates in values.items()
            }
            private_rows.append({
                "counts": counts,
                "left_selector_coordinate": left_coordinate,
                "overlaps": values,
                "overlap_sha256": {
                    name: canonical_sha256(coordinates)
                    for name, coordinates in values.items()
                },
                "right_selector_coordinate": right_coordinate,
            })
            public_rows.append({
                **counts,
                "left_selector_coordinate": left_coordinate,
                "right_selector_coordinate": right_coordinate,
            })
    overlap_sha256 = canonical_sha256(private_rows)
    private["top_six_pairwise_overlap"] = {
        "pair_count": len(private_rows),
        "rows": private_rows,
        "sha256": overlap_sha256,
    }
    public["top_six_pairwise_overlap"] = {
        "dimensions": [
            "candidate_call_sites",
            "pending_coordinates",
            "reachable_pending_roots",
            "source_only_call_sites",
            "terminal_coordinates",
        ],
        "pair_count": len(public_rows),
        "private_exact_overlap_sha256": overlap_sha256,
        "ranked_selector_count": len(ranked),
        "rows": public_rows,
    }
    return overlap_sha256


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
            "post-post292-wave1 ranking pins unresolved: "
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
        artifact["post292_wave1_inputs"] = dict(observed)
        artifact["post292_wave1_transition"] = dict(
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


def bootstrap_report(
    private: Mapping[str, Any],
    public: Mapping[str, Any],
    observed: Mapping[str, str],
) -> dict[str, Any]:
    top = public["ranking"][0]
    top_private = next(
        row
        for row in private["direct_targets"]
        if row["target_coordinate"] == top["selector_coordinate"]
    )
    private_bytes = serialized_json(private)
    public_bytes = serialized_json(public)
    return {
        "candidate_sha256":
            private["inputs"]["pk_rebuilt_candidate_sha256"],
        "eligible_family_count":
            public["scope"]["eligible_fixed_seven_way_family_count"],
        "eligible_union_rows":
            public["scope"]["eligible_family_current_pending_union_rows"],
        "input_sha256": dict(observed),
        "non_seven_way_call_targets":
            public["exclusions"]["non_seven_way_reachable_call_targets"],
        "owned_call_targets":
            public["exclusions"]["already_owned_reachable_call_targets"],
        "pending_root_count":
            public["scope"]["official_pending_root_count"],
        "pending_root_sha256":
            public["scope"]["official_pending_root_sha256"],
        "point_estimate":
            public["recommendation"]["estimated_actual_promotion_rows"],
        "private_sha256": sha256_bytes(private_bytes),
        "public_sha256": sha256_bytes(public_bytes),
        "reachable_call_targets":
            public["scope"]["reachable_0143_call_target_count"],
        "recommended": {
            **top,
            "terminals":
                top_private["jump_closure"]["terminal_coordinates"],
        },
        "top_six_overlap_sha256":
            private["top_six_pairwise_overlap"]["sha256"],
    }


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
