#!/usr/bin/env python3
"""Freeze the 8,645-pending checkpoint after dynamic honorific repair.

The checkpoint includes every prior Base/PK runtime-VM promotion plus the
four literal-owned honorific-space overrides, all affected evidence renewals,
and the 57 newly proved PK rows.  Later closure layers bind to this
non-circular predecessor.  Steam remains read only.
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
    / "runtime_vm_integrated.post_dynamic_honorific_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_dynamic_honorific_checkpoint.source_free.v1.json"
)


class CheckpointError(ValueError):
    """Raised when the post-honorific checkpoint contract drifts."""


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
    "pc_dialogue_runtime_vm_post_dynamic_honorific_checkpoint_integration",
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
    )
    require(
        report["promotions"]["pk_msggame"]["promotion_count"]
        == INTEGRATION.EXPECTED_PK_FINAL_PROMOTIONS
        and report["promotions"]["pk_msggame"][
            "dynamic_honorific_spacing_layer_included"
        ]
        is True
        and report["result"]["runtime_review_pending"]
        == INTEGRATION.EXPECTED_FINAL_PENDING_AFTER
        and report["validation"][
            "post_cross_predecessor_checkpoint_rebuilt_and_matched"
        ]
        is True
        and report["steam_write_performed"] is False,
        "post-dynamic-honorific checkpoint result drifted",
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
            "private post-dynamic-honorific checkpoint drifted",
        )
        require(
            args.public_output.is_file()
            and args.public_output.read_text(encoding="utf-8")
            == public_content,
            "source-free post-dynamic-honorific checkpoint report drifted",
        )
    print(
        "PASS "
        f"rows={report['result']['semantic_review_approved']} "
        f"promoted={report['promotions']['promoted_total']} "
        f"pending={report['result']['runtime_review_pending']} "
        "dynamic_honorific=true steam_write=false"
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
