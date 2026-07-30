#!/usr/bin/env python3
"""Freeze the 8,213-pending checkpoint after selector-1066 closure.

This checkpoint includes every prior Base/PK runtime-VM layer plus the
selector-1066 / terminal-2546--2552 full-caller closure. Dialogue-bearing
JSONL remains below ``tmp/``; only its source-free report is tracked. Steam
remains read only.
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
    / (
        "runtime_vm_integrated."
        "post_bound_terminal_2546_checkpoint.private.v1.jsonl"
    )
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / (
        "runtime_vm_integration."
        "post_bound_terminal_2546_checkpoint.source_free.v1.json"
    )
)

EXPECTED_ROWS = 52_803
EXPECTED_PENDING = 8_213
EXPECTED_PK_PROMOTIONS = 12_470
EXPECTED_PROMOTED_TOTAL = 28_121
EXPECTED_PRIVATE_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_INTEGRATION_BUILDER_SHA256 = (
    "66EEC3FAD6AFCB26737BC8ECD339129B8464D734085C5DFE26A5CFD9A0331C68"
)
EXPECTED_INTEGRATION_REPORT_SHA256 = (
    "838D162126925ECF706577688D35570853CDA68226AF3C8FFB7FE14C3943D072"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "54B4255C29F256B84E1CA4EE8A9B5D21FE254100A2A71CA28657F7EF6EB34E45"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)


class CheckpointError(ValueError):
    """Raised when the post-selector-1066 checkpoint contract drifts."""


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
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


INTEGRATION = load_module(
    "pc_dialogue_runtime_vm_post_bound_terminal_2546_checkpoint_integration",
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
    resolved_public = args.public_output.resolve(strict=False)
    require(
        resolved_private != private_root
        and private_root in resolved_private.parents,
        f"private output must remain below {private_root}",
    )
    require(
        resolved_public == DEFAULT_PUBLIC_OUTPUT.resolve(strict=False),
        "public checkpoint output must use its tracked source-free path",
    )
    require(
        resolved_private != resolved_public,
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
    layer = pk.get("bound_terminal_2546_full_caller", {})
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
        and pk.get("dynamic_honorific_spacing_layer_included") is True
        and pk.get("bound_terminal_family_layer_included") is True
        and pk.get("thought_predicate_family_layer_included") is True
        and pk.get("bound_terminal_caller_layer_included") is True
        and pk.get("bound_terminal_2546_full_caller_layer_included")
        is True
        and pk.get(
            "rebuilt_post_bound_terminal_caller_integrated_private_sha256"
        )
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and isinstance(layer, dict)
        and layer.get("promotion_count") == 364
        and layer.get("verification_renewal_count") == 292
        and layer.get("translation_override_count") == 216
        and layer.get("updated_row_count") == 656
        and layer.get("rejected_pending_count") == 74
        and layer.get("pk_candidate_packed_sha256")
        == EXPECTED_PK_CANDIDATE_SHA256
        and validation.get(
            "pk_only_predecessor_checkpoint_rebuilt_and_matched"
        )
        is True
        and validation.get(
            "cross_resource_predecessor_checkpoint_rebuilt_and_matched"
        )
        is True
        and validation.get(
            "post_cross_predecessor_checkpoint_rebuilt_and_matched"
        )
        is True
        and validation.get(
            "post_dynamic_predecessor_checkpoint_rebuilt_and_matched"
        )
        is True
        and validation.get(
            "post_bound_predecessor_checkpoint_rebuilt_and_matched"
        )
        is True
        and validation.get(
            "post_thought_predecessor_checkpoint_rebuilt_and_matched"
        )
        is True
        and validation.get(
            "post_bound_terminal_caller_predecessor_checkpoint_"
            "rebuilt_and_matched"
        )
        is True
        and validation.get(
            "bound_terminal_2546_full_caller_layer_included"
        )
        is True
        and validation.get(
            "selector_1066_terminal_2546_full_closure_rechecked"
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
        "post-bound-terminal-2546 checkpoint result drifted",
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
    )
    validate_checkpoint_report(report)
    require(
        sha256_bytes(private_content.encode("utf-8"))
        == EXPECTED_PRIVATE_SHA256,
        "private post-bound-terminal-2546 checkpoint digest drifted",
    )
    require(
        sha256_bytes(public_content.encode("utf-8"))
        == EXPECTED_INTEGRATION_REPORT_SHA256
        and INTEGRATION_REPORT_PATH.read_text(encoding="utf-8")
        == public_content,
        "public post-bound-terminal-2546 checkpoint binding drifted",
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
            "private post-bound-terminal-2546 checkpoint drifted",
        )
        require(
            args.public_output.is_file()
            and args.public_output.read_text(encoding="utf-8")
            == public_content,
            (
                "source-free post-bound-terminal-2546 checkpoint "
                "report drifted"
            ),
        )
    print(
        "PASS "
        f"rows={report['result']['semantic_review_approved']} "
        f"pk_promoted={report['promotions']['pk_msggame']['promotion_count']} "
        f"pending={report['result']['runtime_review_pending']} "
        "bound_terminal_2546=true steam_write=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        ValueError,
        CheckpointError,
        INTEGRATION.IntegrationError,
        INTEGRATION.ENGINE.RetranslationError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
