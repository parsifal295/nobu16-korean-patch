#!/usr/bin/env python3
"""Freeze the 7,896-pending checkpoint after D5/selector-538-family closure.

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
INTEGRATION_REPORT_PATH = (
    WORKSTREAM / "runtime_vm_integration.source_free.v1.json"
)
OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name
DEFAULT_PRIVATE_OUTPUT = (
    OUTPUT_ROOT
    / "runtime_vm_integrated."
    "post_selector538_family_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration."
    "post_selector538_family_checkpoint.source_free.v1.json"
)

EXPECTED_ROWS = 52_803
EXPECTED_PENDING = 7_896
EXPECTED_PK_PROMOTIONS = 12_787
EXPECTED_PROMOTED_TOTAL = 28_438
EXPECTED_PRIVATE_SHA256 = (
    "81B4E22C3C20AA5F7FF8B8251A2829AEEB0C6E0A0D9FA2B93748B6249F23F6CB"
)
EXPECTED_INTEGRATION_BUILDER_SHA256 = (
    "8DEDEED85915D85FD49D1092B5571E49EDCDD3FEDFD08E1EBD16AD3B459221BA"
)
EXPECTED_INTEGRATION_REPORT_SHA256 = (
    "46270F70A019484EFB1F99851D436467C8FD2DE32EB222BDC048DA1B5BC080FA"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "DCB19B0D85422F7C0EA5888F9A0C47667D75A88D100BABAE11DDAF4A8DD2000E"
)
EXPECTED_D5_DECISION_SHA256 = (
    "54343C398C7D8E22A957AE47CA9B8AA5C11DD7F64C6BEF4EFF50DFA4EF466095"
)
EXPECTED_D5_EVIDENCE_SHA256 = (
    "C328430233A81E4457BD253844D65622B7305AEB20FACB30E011C2EEF7B58BD0"
)
EXPECTED_SELECTOR538_DECISION_SHA256 = (
    "5640EB7FB7E4EA9B32309B7FA280637DA9F26F96CA500BCD4FA9847D997456C0"
)
EXPECTED_SELECTOR538_EVIDENCE_SHA256 = (
    "910C0A59823C2B6B083F58257D6203053738EFEFC2E49E6271D553FF44CAB940"
)


class CheckpointError(ValueError):
    """Raised when the post-selector-538-family contract drifts."""


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
    "pc_dialogue_runtime_vm_post_selector538_family_checkpoint_integration",
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
        args.public_output.resolve(strict=False)
        == DEFAULT_PUBLIC_OUTPUT.resolve(strict=False),
        "public checkpoint must use its tracked source-free path",
    )
    require(
        resolved_private
        != args.public_output.resolve(strict=False),
        "private and public checkpoint outputs must be distinct",
    )


def validate_frozen_inputs() -> None:
    require(
        sha256_file(INTEGRATION_PATH)
        == EXPECTED_INTEGRATION_BUILDER_SHA256,
        "integrated decision builder digest drifted",
    )
    require(
        sha256_file(INTEGRATION_REPORT_PATH)
        == EXPECTED_INTEGRATION_REPORT_SHA256,
        "integrated source-free report digest drifted",
    )


def validate_checkpoint_report(report: dict[str, Any]) -> None:
    pk = report.get("promotions", {}).get("pk_msggame", {})
    result = report.get("result", {})
    validation = report.get("validation", {})
    d5 = pk.get("bound_terminal_2546_category_b_deferred", {})
    family = pk.get("selector538_family", {})
    distribution = report.get("distribution_policy", {})
    require(
        result.get("semantic_review_approved") == EXPECTED_ROWS
        and result.get("runtime_review_pending") == EXPECTED_PENDING
        and result.get("fully_candidate_eligible")
        == EXPECTED_ROWS - EXPECTED_PENDING
        and result.get("private_integrated_decision_sha256")
        == EXPECTED_PRIVATE_SHA256
        and report.get("promotions", {}).get("promoted_total")
        == EXPECTED_PROMOTED_TOTAL
        and pk.get("promotion_count") == EXPECTED_PK_PROMOTIONS
        and pk.get(
            "bound_terminal_2546_category_b_deferred_layer_included"
        )
        is True
        and pk.get("selector538_family_layer_included") is True
        and pk.get(
            "rebuilt_post_bound_terminal_2546_full_caller_"
            "integrated_private_sha256"
        )
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and d5.get("private_source_update_sha256")
        == EXPECTED_D5_DECISION_SHA256
        and d5.get("private_source_evidence_sha256")
        == EXPECTED_D5_EVIDENCE_SHA256
        and d5.get("promotion_count") == 5
        and d5.get("verification_renewal_count") == 2
        and d5.get("translation_override_count") == 6
        and d5.get("updated_row_count") == 7
        and family.get("private_source_update_sha256")
        == EXPECTED_SELECTOR538_DECISION_SHA256
        and family.get("private_source_evidence_sha256")
        == EXPECTED_SELECTOR538_EVIDENCE_SHA256
        and family.get("promotion_count") == 212
        and family.get("total_family_promotion_count") == 277
        and family.get("verification_renewal_count") == 420
        and family.get("translation_override_count") == 142
        and family.get("updated_row_count") == 697
        and family.get("combined_candidate_packed_sha256")
        == EXPECTED_PK_CANDIDATE_SHA256
        and validation.get(
            "official_a19_predecessor_rebuilt_and_matched"
        )
        is True
        and validation.get(
            "d5_selector538_family_disjointness_rechecked"
        )
        is True
        and validation.get("all_1057_register_assemblies_rechecked")
        is True
        and validation.get(
            "unique_renewal_override_owner_union_preserved"
        )
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
        "post-selector538-family checkpoint result drifted",
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
    )
    validate_checkpoint_report(report)
    require(
        sha256_bytes(private_content.encode("utf-8"))
        == EXPECTED_PRIVATE_SHA256,
        "private post-selector538-family checkpoint digest drifted",
    )
    require(
        sha256_bytes(public_content.encode("utf-8"))
        == EXPECTED_INTEGRATION_REPORT_SHA256
        and INTEGRATION_REPORT_PATH.read_text(encoding="utf-8")
        == public_content,
        "public post-selector538-family checkpoint binding drifted",
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
            "private post-selector538-family checkpoint drifted",
        )
        require(
            args.public_output.is_file()
            and args.public_output.read_text(encoding="utf-8")
            == public_content,
            "public post-selector538-family checkpoint drifted",
        )
    print(
        "PASS "
        f"rows={report['result']['semantic_review_approved']} "
        f"pk_promoted={report['promotions']['pk_msggame']['promotion_count']} "
        f"pending={report['result']['runtime_review_pending']} "
        "selector538_family=true steam_write=false"
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
