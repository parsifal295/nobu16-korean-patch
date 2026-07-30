#!/usr/bin/env python3
"""Rank PK selector families after the consolidated post-292 wave 4."""

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
    / "build_pk_next_selector_family_ranking_post_post292_wave3_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    DIALOGUE_WORKSTREAM
    / "build_runtime_vm_"
    "post_selector292_wave4_consolidated_checkpoint_v1.py"
)
DEFAULT_LEDGER = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector292_wave4_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    DIALOGUE_WORKSTREAM
    / "runtime_vm_integration."
    "post_selector292_wave4_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_dialogue_wave_"
    "post_selector292_wave4_consolidated_closure_v1.py"
)
CLOSURE_COVERAGE_PATH = (
    WORKSTREAM
    / "public"
    / "pk_dialogue_wave_post_selector292_wave4_"
    "consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    WORKSTREAM
    / "public"
    / "pk_dialogue_wave_post_selector292_wave4_"
    "consolidated_closure_promotion.v1.json"
)
PROGRESS_BUILDER_PATH = (
    DIALOGUE_WORKSTREAM
    / "build_progress_"
    "post_selector292_wave4_consolidated_delta_v1.py"
)
PROGRESS_PUBLIC_PATH = (
    DIALOGUE_WORKSTREAM
    / "progress.post_selector292_wave4_consolidated.source_free.v1.json"
)
PROGRESS_ALIAS_PATH = DIALOGUE_WORKSTREAM / "progress.source_free.v1.json"

DEFAULT_STEAM_ROOT = (
    DIALOGUE_TMP / "development_steam_root_pre_base_runtime_apply_13a404f"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "pk_next_selector_family_ranking."
    "post_post292_wave4.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_next_selector_family_ranking."
    "post_post292_wave4.source_free.v1.json"
)

PRIVATE_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-post292-wave4.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-next-selector-family-ranking-"
    "post-post292-wave4-source-free.v1"
)
METHOD = (
    "post292_wave4_closure_checkpoint_progress_pending_reachable_0143_"
    "owned_excluded_seven_way_selector_ranking_with_pairwise_overlap"
)
WAVE_SELECTORS = (754, 310, 844)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "051640AEB5D0C554E695C16BC7EF521BACD24BDE115886A8B707FF91F356742A"
)
EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "checkpoint_builder":
        "C6BEB85B9E7CFB8B5BE395EFC9837631A806D40572151924ADBB06F62AA072F5",
    "checkpoint_private":
        "BDE252E097BB1D7531F2269E0C4C105972EAEC484961E7EEEA44C0D1414C1DAE",
    "checkpoint_public":
        "FA294DE6C6B4D26F5BE6BF352D7631AB210224D6C1B95962871275011C07CAEB",
    "closure_builder":
        "72A658503FF172195921FC42A1EEEC0981F210C61480A780DF1D7588CC25469C",
    "closure_coverage":
        "93EA8E767469DD9122D12C6A76AF09F045CC4C83153C6A0EB80991BC3BC54B19",
    "closure_promotion":
        "04689FCCB2D848400AA54E225BB6EE6CB5758F66B84738731CDAFD083AFA232F",
    "progress_builder":
        "662B3FDD9614A3468A406415BE3E97BED1C410B5219500FABE43A98F25F5B207",
    "progress_immutable":
        "7E032B6CFF3AF1D6F1B299CD2A9683E8DC880778702820D1F4308A26EBB9E20D",
    "progress_alias":
        "7E032B6CFF3AF1D6F1B299CD2A9683E8DC880778702820D1F4308A26EBB9E20D",
}

EXPECTED_PK_CANDIDATE_SHA256: str | None = (
    "6D60AEEDBD22843B9AEC1DC4B1DDC3509106D6C8FC8F74FE79E4C1E3CE037836"
)
EXPECTED_PK_PENDING_ROWS: int | None = 5_970
EXPECTED_PK_PENDING_ROOTS: int | None = 3_967
EXPECTED_PK_PENDING_ROOT_SHA256: str | None = (
    "66BEF9E6EACE4FAD57640EEFBDE4514A8E927C3671DC7B25A9FE01D608B9EE33"
)
EXPECTED_REACHABLE_CALL_TARGETS: int | None = 145
EXPECTED_OWNED_CALL_TARGETS: int | None = 44
EXPECTED_NON_SEVEN_WAY_TARGETS: int | None = 23
EXPECTED_ELIGIBLE_FAMILIES: int | None = 78
EXPECTED_ELIGIBLE_UNION_ROWS: int | None = 406
EXPECTED_ELIGIBLE_UNION_SHA256: str | None = (
    "DDB066304B74F682AF84CFF67A48CC28E41D2B13BDDB87C1C87E282AFD02B4F2"
)
EXPECTED_RECOMMENDED_SELECTOR: str | None = "0:148"
EXPECTED_RECOMMENDED_TERMINALS: tuple[str, ...] | None = (
    "0:1447",
    "0:1448",
    "0:1449",
    "0:1450",
    "0:1451",
    "0:1452",
    "0:1453",
)
EXPECTED_RECOMMENDED_PENDING_ROWS: int | None = 17
EXPECTED_RECOMMENDED_PENDING_ROOTS: int | None = 10
EXPECTED_RECOMMENDED_PENDING_SITES: int | None = 10
EXPECTED_RECOMMENDED_CANDIDATE_SITES: int | None = 61
EXPECTED_RECOMMENDED_SOURCE_SITES: int | None = 70
EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES: int | None = 9
EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES: int | None = 0
EXPECTED_POINT_ESTIMATE: int | None = 11
EXPECTED_ESTIMATE_RANGE: tuple[int, int] | None = (0, 17)
EXPECTED_TOP_SIX_OVERLAP_SHA256: str | None = (
    "A9B3369D47C00FDAC66108EE0CCC24E8591C2339FB0622287C8D61B8FC108CC8"
)
EXPECTED_PRIVATE_FILE_SHA256: str | None = (
    "F3F4C736EA138883D9795E6B8AFB5079FF866179AE6026002AFCDFD12B67B7FE"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "8031A39CC75AE935FCEAD31EBFFF7F9897776AE75A4F560F36599862C3D41797"
)

EXPECTED_PROGRESS_TRANSITION: dict[str, int | None] = {
    "pending_before": 5_999,
    "pending_after": 5_970,
    "eligible_before": 46_804,
    "eligible_after": 46_833,
    "pk_promotions_before": 14_684,
    "pk_promotions_after": 14_713,
    "promoted_total_before": 30_335,
    "promoted_total_after": 30_364,
    "retranslated_before": 46_459,
    "retranslated_after": 46_488,
    "wave_promotions": 29,
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


class PostWave4RankingError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PostWave4RankingError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREDECESSOR = load_module(
    PREDECESSOR_BUILDER, "pk_post_post292_wave4_predecessor"
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
    require(not missing, "post292 wave4 inputs absent: " + ",".join(missing))
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
        "post-wave3 ranking predecessor drifted",
    )
    if frozen:
        for name, digest in observed.items():
            require(
                digest == EXPECTED_INPUT_SHA256[name],
                f"post292 wave4 input drifted: {name}",
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
        "wave4 checkpoint/closure/progress transition drifted",
    )
    if frozen:
        require(
            transition == EXPECTED_PROGRESS_TRANSITION,
            "wave4 frozen transition pins drifted",
        )
    return transition


def relaxed_core_outputs() -> tuple[dict[str, Any], dict[str, Any]]:
    configure_predecessor_module()
    PREDECESSOR.configure_ranking()
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
        PREDECESSOR.configure_ranking()


def build_outputs(
    *, allow_unfrozen: bool = False
) -> tuple[dict[str, Any], dict[str, Any], dict[str, str]]:
    if not allow_unfrozen:
        require(
            not unresolved_pins(),
            "post-post292-wave4 ranking pins unresolved: "
            + ",".join(unresolved_pins()),
        )
    observed = observed_input_hashes()
    transition = validate_handoffs(
        observed, frozen=not allow_unfrozen
    )
    configure_predecessor_module()
    PREDECESSOR.configure_ranking()
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
        artifact["post292_wave4_inputs"] = dict(observed)
        artifact["post292_wave4_transition"] = transition
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
