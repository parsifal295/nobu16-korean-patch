#!/usr/bin/env python3
"""Rank PK selector families after the consolidated post-292 wave 2."""

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
    / "build_pk_next_selector_family_ranking_post_post292_wave1_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    DIALOGUE_WORKSTREAM
    / "build_runtime_vm_"
    "post_selector292_wave2_consolidated_checkpoint_v1.py"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector292_wave2_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    DIALOGUE_WORKSTREAM
    / "runtime_vm_integration."
    "post_selector292_wave2_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_dialogue_wave_"
    "post_selector292_wave2_consolidated_closure_v1.py"
)
CLOSURE_COVERAGE_PATH = (
    WORKSTREAM
    / "public"
    / "pk_dialogue_wave_post_selector292_wave2_"
    "consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    WORKSTREAM
    / "public"
    / "pk_dialogue_wave_post_selector292_wave2_"
    "consolidated_closure_promotion.v1.json"
)
PROGRESS_BUILDER_PATH = (
    DIALOGUE_WORKSTREAM
    / "build_progress_"
    "post_selector292_wave2_consolidated_delta_v1.py"
)
PROGRESS_PUBLIC_PATH = (
    DIALOGUE_WORKSTREAM
    / "progress.post_selector292_wave2_consolidated.source_free.v1.json"
)
PROGRESS_ALIAS_PATH = DIALOGUE_WORKSTREAM / "progress.source_free.v1.json"

DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_post292_wave2.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_post292_wave2.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-post292-wave2.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-post292-wave2-source-free.v1"
)
METHOD = (
    "post292_wave2_closure_checkpoint_progress_pending_reachable_0143_"
    "owned_excluded_seven_way_selector_ranking_with_pairwise_overlap"
)
WAVE_SELECTORS = (1048, 82, 214)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "5DEADB11F81897B0F6F52AD3E032CE49045FDA8557B86BA7C5E571AD9AA6AC42"
)
EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "checkpoint_builder":
        "32812D569C2F5CDF431871AB8FD0E1610776ADE8846E04A3203432AF86414F6D",
    "checkpoint_private":
        "477C57FE380B20F45F5D952ED3954DE3D1F267CA2E0EA4BC5FA6E96B36877843",
    "checkpoint_public":
        "24EC33757EB877A0025F23908305D002306359DAC277D36ED85EC45EF076E21A",
    "closure_builder":
        "9BCC703A0C5D92CB8FF6EAC7E3886AC955B11AC7D0E05263E271FF7E670DFFF3",
    "closure_coverage":
        "443BA5DFE3F997E01F99DD55C39E0C2B8CA2A778D36D3D3904B6883D11DD39AB",
    "closure_promotion":
        "331AB234848248CAAD54550ECD286C97F64F5E3C3D60422CBFB77709E8583446",
    "progress_builder":
        "0F618FC87941C575991568B74C926D25EA8B07A7688E3B07F2D562C3C79458CC",
    "progress_immutable":
        "BB153A023FDCAAE6F178DB0DCAA73096D9E6EBE5DED67BBA63ACB2F3BEE3BA3C",
    "progress_alias":
        "BB153A023FDCAAE6F178DB0DCAA73096D9E6EBE5DED67BBA63ACB2F3BEE3BA3C",
}

EXPECTED_PK_CANDIDATE_SHA256: str | None = (
    "DF91852936FFBCF0F7C9A17D4D05166A66E041F7A837E50BE600923DB8A2CA9A"
)
EXPECTED_PK_PENDING_ROWS = 6_022
EXPECTED_PK_PENDING_ROOTS: int | None = 3_987
EXPECTED_PK_PENDING_ROOT_SHA256: str | None = (
    "AFCA32847ECD958121EE1C26A5E499D3E0EEE7277DD0A76C4D42596D4F0FCCC2"
)
EXPECTED_REACHABLE_CALL_TARGETS: int | None = 146
EXPECTED_OWNED_CALL_TARGETS: int | None = 38
EXPECTED_NON_SEVEN_WAY_TARGETS: int | None = 23
EXPECTED_ELIGIBLE_FAMILIES: int | None = 85
EXPECTED_ELIGIBLE_UNION_ROWS: int | None = 492
EXPECTED_ELIGIBLE_UNION_SHA256: str | None = (
    "FB3CFF341842A300499E4E07712FB3139EEDE35E3E4FBDBDE58114881DB87F3D"
)
EXPECTED_RECOMMENDED_SELECTOR: str | None = "0:1132"
EXPECTED_RECOMMENDED_TERMINALS: tuple[str, ...] | None = (
    "0:2623",
    "0:2624",
    "0:2625",
    "0:2626",
    "0:2627",
    "0:2628",
    "0:2629",
)
EXPECTED_RECOMMENDED_PENDING_ROWS: int | None = 25
EXPECTED_RECOMMENDED_PENDING_ROOTS: int | None = 9
EXPECTED_RECOMMENDED_PENDING_SITES: int | None = 9
EXPECTED_RECOMMENDED_CANDIDATE_SITES: int | None = 19
EXPECTED_RECOMMENDED_SOURCE_SITES: int | None = 22
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES: int | None = 3
EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES: int | None = 0
EXPECTED_POINT_ESTIMATE: int | None = 16
EXPECTED_ESTIMATE_RANGE: tuple[int, int] | None = (0, 25)
EXPECTED_TOP_SIX_OVERLAP_SHA256: str | None = (
    "BE34A6997D89AF61DF62092765728063DB5173546EB29214C16B63482F730175"
)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "4BB7C8CF9735C8ADCA1ECFFADA5A669FD0B4EA7A050E9F9AE887F344A78E9782"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "FF1937BA30EC607468347BA11C3CD34C25258470AA5CBE62E3FD2A9E8FA5BE66"
)

EXPECTED_PROGRESS_TRANSITION = {
    "pending_before": 6_084,
    "pending_after": 6_022,
    "eligible_before": 46_719,
    "eligible_after": 46_781,
    "pk_promotions_before": 14_599,
    "pk_promotions_after": 14_661,
    "promoted_total_before": 30_250,
    "promoted_total_after": 30_312,
    "retranslated_before": 46_374,
    "retranslated_after": 46_436,
    "wave_promotions": 62,
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
    PREDECESSOR_BUILDER, "pk_post_post292_wave2_predecessor"
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
    require(not missing, "post292 wave2 inputs absent: " + ",".join(missing))
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
        "post-wave1 ranking predecessor drifted",
    )
    if frozen:
        for name, digest in observed.items():
            require(
                digest == EXPECTED_INPUT_SHA256[name],
                f"post292 wave2 input drifted: {name}",
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
        "wave2 closure transition drifted",
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
            "post-post292-wave2 ranking pins unresolved: "
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
        artifact["post292_wave2_inputs"] = dict(observed)
        artifact["post292_wave2_transition"] = dict(
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
