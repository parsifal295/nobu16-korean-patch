#!/usr/bin/env python3
"""Freeze the 7,268-pending checkpoint after selector568/1096/1174 closure.

Dialogue-bearing JSONL remains below ``tmp``.  The tracked checkpoint report
is source-free, and live Steam remains read only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Any, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
INTEGRATION_PATH = WORKSTREAM / "build_runtime_vm_integrated_decisions_v1.py"
OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name
PREDECESSOR_PRIVATE_PATH = (
    OUTPUT_ROOT
    / "runtime_vm_integrated."
    "post_selector538_family_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration."
    "post_selector538_family_checkpoint.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    OUTPUT_ROOT
    / "runtime_vm_integrated."
    "post_selector568_1096_1174_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration."
    "post_selector568_1096_1174_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_ROWS = 52_803
EXPECTED_PENDING = 7_268
EXPECTED_ELIGIBLE = 45_535
EXPECTED_PK_PROMOTIONS = 13_415
EXPECTED_PROMOTED_TOTAL = 29_066
EXPECTED_UPDATED_ROWS = 1_173
EXPECTED_LAYER_PROMOTIONS = 628
EXPECTED_LAYER_RENEWALS = 545
EXPECTED_LAYER_OVERRIDES = 440
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 413,
    "translation_override_and_runtime_promotion": 215,
    "translation_override_and_verification_renewal": 225,
    "verification_renewal": 320,
}
EXPECTED_PRIVATE_SHA256 = (
    "FC157A9907686D0EA6DC6C61C7785E81AC7F750100F2E1CDDE02DBF4F09F2DCA"
)
EXPECTED_PUBLIC_SHA256 = (
    "1FCF033F1F75FC43473152CFB7115D170657519952C19D563C36C3F9BAB4CBD1"
)
EXPECTED_INTEGRATION_BUILDER_SHA256 = (
    "8DEDEED85915D85FD49D1092B5571E49EDCDD3FEDFD08E1EBD16AD3B459221BA"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "81B4E22C3C20AA5F7FF8B8251A2829AEEB0C6E0A0D9FA2B93748B6249F23F6CB"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "46270F70A019484EFB1F99851D436467C8FD2DE32EB222BDC048DA1B5BC080FA"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "07E65E6338D32C1FD13F17408F82A4133E55541C722874632948C7B36C909805"
)
EXPECTED_DECISION_SHA256 = (
    "3260FCF12561EE116228907E1619FDB368DBDF9D0BA8565C03CD014440669B38"
)
EXPECTED_EVIDENCE_SHA256 = (
    "3AA3CB05106CA921F22B96D26B8FA74A4F7C7D15A4D3AE122738F92E10A34C25"
)
EXPECTED_AUDIT_SHA256 = (
    "1C70A12C107DB79B1402F5879364F5AAEA31F34B3933F4C53524C89B570F9990"
)
EXPECTED_PROMOTION_SHA256 = (
    "E16B597EF856822350D3FD0E0FAB7A9737E3D40D6FE156ED39EA778E5DE85AA0"
)


class CheckpointError(ValueError):
    """Raised when the consolidated checkpoint contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckpointError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    require(path.is_file(), f"required file is absent: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(
        spec is not None and spec.loader is not None,
        f"cannot import {path}",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


INTEGRATION = load_module(
    "pc_dialogue_runtime_vm_post_selector568_1096_1174_checkpoint_integration",
    INTEGRATION_PATH,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--steam-root",
        type=Path,
        default=INTEGRATION.ENGINE.DEFAULT_STEAM_ROOT,
    )
    parser.add_argument(
        "--base-pristine",
        type=Path,
        default=INTEGRATION.ENGINE.DEFAULT_BASE_PRISTINE,
    )
    parser.add_argument(
        "--pk-pristine",
        type=Path,
        default=INTEGRATION.ENGINE.DEFAULT_PK_PRISTINE,
    )
    parser.add_argument(
        "--private-output",
        type=Path,
        default=DEFAULT_PRIVATE_OUTPUT,
    )
    parser.add_argument(
        "--public-output",
        type=Path,
        default=DEFAULT_PUBLIC_OUTPUT,
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    return parser


def validate_output_paths(args: argparse.Namespace) -> None:
    private_root = OUTPUT_ROOT.resolve(strict=False)
    resolved_private = args.private_output.resolve(strict=False)
    require(
        resolved_private != private_root
        and private_root in resolved_private.parents,
        f"private output must remain below {private_root}",
    )
    require(
        resolved_private == DEFAULT_PRIVATE_OUTPUT.resolve(strict=False),
        "private checkpoint must use its immutable consolidated path",
    )
    require(
        args.public_output.resolve(strict=False)
        == DEFAULT_PUBLIC_OUTPUT.resolve(strict=False),
        "public checkpoint must use its tracked source-free path",
    )
    require(
        resolved_private != args.public_output.resolve(strict=False),
        "private and public checkpoint outputs must be distinct",
    )


def validate_frozen_inputs() -> None:
    require(
        sha256_file(INTEGRATION_PATH)
        == EXPECTED_INTEGRATION_BUILDER_SHA256,
        "integrated decision builder digest drifted",
    )
    require(
        sha256_file(PREDECESSOR_PRIVATE_PATH)
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        "post-selector538 predecessor private digest drifted",
    )
    require(
        sha256_file(PREDECESSOR_PUBLIC_PATH)
        == EXPECTED_PREDECESSOR_PUBLIC_SHA256,
        "post-selector538 predecessor public digest drifted",
    )


def validate_checkpoint_report(report: dict[str, Any]) -> None:
    pk = report.get("promotions", {}).get("pk_msggame", {})
    result = report.get("result", {})
    validation = report.get("validation", {})
    layer = pk.get("selector568_1096_1174_consolidated", {})
    distribution = report.get("distribution_policy", {})
    require(
        result.get("semantic_review_approved") == EXPECTED_ROWS
        and result.get("runtime_review_pending") == EXPECTED_PENDING
        and result.get("fully_candidate_eligible") == EXPECTED_ELIGIBLE
        and result.get("private_integrated_decision_sha256")
        == EXPECTED_PRIVATE_SHA256
        and report.get("promotions", {}).get("promoted_total")
        == EXPECTED_PROMOTED_TOTAL
        and pk.get("promotion_count") == EXPECTED_PK_PROMOTIONS
        and pk.get(
            "selector568_1096_1174_consolidated_layer_included"
        )
        is True
        and pk.get(
            "rebuilt_post_selector538_family_integrated_private_sha256"
        )
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and layer.get("private_source_update_sha256")
        == EXPECTED_DECISION_SHA256
        and layer.get("private_source_evidence_sha256")
        == EXPECTED_EVIDENCE_SHA256
        and layer.get("audit_report_sha256") == EXPECTED_AUDIT_SHA256
        and layer.get("promotion_report_sha256")
        == EXPECTED_PROMOTION_SHA256
        and layer.get("combined_candidate_packed_sha256")
        == EXPECTED_PK_CANDIDATE_SHA256
        and layer.get("updated_row_count") == EXPECTED_UPDATED_ROWS
        and layer.get("promotion_count") == EXPECTED_LAYER_PROMOTIONS
        and layer.get("verification_renewal_count")
        == EXPECTED_LAYER_RENEWALS
        and layer.get("semantic_override_count")
        == EXPECTED_LAYER_OVERRIDES
        and layer.get("action_counts") == EXPECTED_ACTION_COUNTS
        and layer.get("steam_write_performed") is False
        and validation.get(
            "selector568_1096_1174_consolidated_layer_included"
        )
        is True
        and validation.get("single_combined_coordinate_union_used")
        is True
        and validation.get("sequential_cross_and_selector1174_overlays_used")
        is False
        and validation.get("actual_628_pending_promotions_rechecked")
        is True
        and validation.get(
            "affected_545_verified_pk_runtime_evidence_renewed"
        )
        is True
        and validation.get("exact_440_semantic_overrides_rechecked")
        is True
        and distribution.get(
            "tracked_report_contains_commercial_source_text"
        )
        is False
        and distribution.get(
            "tracked_report_contains_translated_dialogue_text"
        )
        is False
        and report.get("steam_write_performed") is False,
        "post-selector568/1096/1174 checkpoint result drifted",
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    require(args.write or args.check, "choose --write, --check, or both")
    validate_output_paths(args)
    validate_frozen_inputs()
    private_content, public_content, report = INTEGRATION.build_outputs(
        steam_root=args.steam_root,
        base_pristine=args.base_pristine,
        pk_pristine=args.pk_pristine,
        private_output=args.private_output,
        include_pk_only=True,
        include_cross_resource=True,
        include_dynamic_honorific_spacing=True,
        include_bound_terminal_family=True,
        include_thought_predicate_family=True,
        include_bound_terminal_caller=True,
        include_bound_terminal_2546_full_caller=True,
        include_bound_terminal_2546_simple_caller=True,
        include_bound_terminal_2546_category_b_immediate=True,
        include_selector538_chunk0=True,
        include_bound_terminal_2546_category_b_deferred=True,
        include_selector538_family=True,
        include_selector568_1096_1174_consolidated=True,
    )
    validate_checkpoint_report(report)
    require(
        sha256_bytes(private_content.encode("utf-8"))
        == EXPECTED_PRIVATE_SHA256,
        "private consolidated checkpoint digest drifted",
    )
    require(
        sha256_bytes(public_content.encode("utf-8"))
        == EXPECTED_PUBLIC_SHA256,
        "public consolidated checkpoint digest drifted",
    )
    if args.write:
        INTEGRATION.ENGINE.atomic_write(
            args.private_output,
            private_content,
        )
        INTEGRATION.ENGINE.atomic_write(
            args.public_output,
            public_content,
        )
    if args.check:
        require(
            args.private_output.is_file()
            and args.private_output.read_text(encoding="utf-8")
            == private_content,
            "private consolidated checkpoint drifted",
        )
        require(
            args.public_output.is_file()
            and args.public_output.read_text(encoding="utf-8")
            == public_content,
            "public consolidated checkpoint drifted",
        )
    print(
        "PASS "
        f"rows={report['result']['semantic_review_approved']} "
        f"pk_promoted={report['promotions']['pk_msggame']['promotion_count']} "
        f"pending={report['result']['runtime_review_pending']} "
        "selector568_1096_1174_consolidated=true steam_write=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        CheckpointError,
        INTEGRATION.IntegrationError,
    ) as error:
        raise SystemExit(f"ERROR: {error}") from error
