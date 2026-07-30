#!/usr/bin/env python3
"""Freeze the 8,577-pending checkpoint after bound-terminal caller closure.

The checkpoint includes every prior Base/PK runtime-VM promotion, dynamic
honorific spacing, bound-terminal and thought-predicate closure, and the final
bound-terminal caller layer.  The dialogue-bearing JSONL remains below
``tmp/``; only its source-free report is tracked.  Steam remains read only.
"""

from __future__ import annotations

import argparse
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
DEFAULT_PRIVATE_OUTPUT = (
    OUTPUT_ROOT
    / (
        "runtime_vm_integrated."
        "post_bound_terminal_caller_checkpoint.private.v1.jsonl"
    )
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / (
        "runtime_vm_integration."
        "post_bound_terminal_caller_checkpoint.source_free.v1.json"
    )
)

EXPECTED_ROWS = 52_803
EXPECTED_PENDING = 8_577
EXPECTED_PK_PROMOTIONS = 12_106
EXPECTED_PROMOTED_TOTAL = 27_757
EXPECTED_PRIVATE_SHA256 = (
    "54B4255C29F256B84E1CA4EE8A9B5D21FE254100A2A71CA28657F7EF6EB34E45"
)


class CheckpointError(ValueError):
    """Raised when the post-caller checkpoint contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckpointError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


INTEGRATION = load_module(
    "pc_dialogue_runtime_vm_post_bound_terminal_caller_checkpoint_integration",
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


def validate_checkpoint_report(report: dict[str, Any]) -> None:
    pk = report.get("promotions", {}).get("pk_msggame", {})
    result = report.get("result", {})
    validation = report.get("validation", {})
    require(
        result.get("semantic_review_approved") == EXPECTED_ROWS
        and result.get("runtime_review_pending") == EXPECTED_PENDING
        and result.get("private_integrated_decision_sha256")
        == EXPECTED_PRIVATE_SHA256
        and report.get("promotions", {}).get("promoted_total")
        == EXPECTED_PROMOTED_TOTAL
        and pk.get("promotion_count") == EXPECTED_PK_PROMOTIONS
        and pk.get("dynamic_honorific_spacing_layer_included") is True
        and pk.get("bound_terminal_family_layer_included") is True
        and pk.get("thought_predicate_family_layer_included") is True
        and pk.get("bound_terminal_caller_layer_included") is True
        and pk.get("rebuilt_post_thought_integrated_private_sha256")
        == INTEGRATION.EXPECTED_THOUGHT_PREDICATE_FINAL_PRIVATE_SHA256
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
        and report.get("steam_write_performed") is False,
        "post-bound-terminal-caller checkpoint result drifted",
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    require(args.write or args.check, "choose --write, --check, or both")
    validate_output_paths(args)
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
    )
    validate_checkpoint_report(report)
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
            "private post-bound-terminal-caller checkpoint drifted",
        )
        require(
            args.public_output.is_file()
            and args.public_output.read_text(encoding="utf-8")
            == public_content,
            (
                "source-free post-bound-terminal-caller checkpoint "
                "report drifted"
            ),
        )
    print(
        "PASS "
        f"rows={report['result']['semantic_review_approved']} "
        f"pk_promoted={report['promotions']['pk_msggame']['promotion_count']} "
        f"pending={report['result']['runtime_review_pending']} "
        "bound_terminal_caller=true steam_write=false"
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
