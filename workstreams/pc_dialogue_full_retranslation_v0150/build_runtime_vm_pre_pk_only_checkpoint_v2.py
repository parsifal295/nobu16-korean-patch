#!/usr/bin/env python3
"""Build the immutable runtime-VM checkpoint before PK-only promotions.

The checkpoint contains the Base, PK exact, and PK residual promotions after
the semantic and relative-reflow overrides.  It deliberately excludes the
PK-only exact-blocked closure so that closure can bind to a non-circular
predecessor ledger.
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
    OUTPUT_ROOT / "runtime_vm_integrated.pre_pk_only_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.pre_pk_only_checkpoint.source_free.v1.json"
)


class CheckpointError(ValueError):
    """Raised when the pre-PK-only checkpoint contract drifts."""


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
    "pc_dialogue_runtime_vm_pre_pk_only_checkpoint_integration",
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


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    require(args.write or args.check, "choose --write, --check, or both")
    private_root = OUTPUT_ROOT.resolve(strict=False)
    resolved_private = args.private_output.resolve(strict=False)
    require(
        resolved_private != private_root and private_root in resolved_private.parents,
        f"private output must remain below {private_root}",
    )
    private_content, public_content, report = INTEGRATION.build_outputs(
        steam_root=args.steam_root,
        base_pristine=args.base_pristine,
        pk_pristine=args.pk_pristine,
        private_output=args.private_output,
        include_pk_only=False,
    )
    require(
        report["promotions"]["pk_msggame"]["promotion_count"]
        == INTEGRATION.EXPECTED_PK_PREDECESSOR_PROMOTIONS
        and report["promotions"]["pk_msggame"]["pk_only_layer_included"] is False
        and report["result"]["runtime_review_pending"]
        == INTEGRATION.EXPECTED_PREDECESSOR_PENDING_AFTER
        and report["validation"][
            "pk_only_predecessor_checkpoint_rebuilt_and_matched"
        ]
        is False
        and report["steam_write_performed"] is False,
        "pre-PK-only checkpoint result drifted",
    )
    if args.write:
        INTEGRATION.ENGINE.atomic_write(args.private_output, private_content)
        INTEGRATION.ENGINE.atomic_write(args.public_output, public_content)
    if args.check:
        require(
            args.private_output.is_file()
            and args.private_output.read_text(encoding="utf-8") == private_content,
            "private pre-PK-only checkpoint drifted",
        )
        require(
            args.public_output.is_file()
            and args.public_output.read_text(encoding="utf-8") == public_content,
            "source-free pre-PK-only checkpoint report drifted",
        )
    print(
        "PASS "
        f"rows={report['result']['semantic_review_approved']} "
        f"promoted={report['promotions']['promoted_total']} "
        f"pending={report['result']['runtime_review_pending']} "
        "pk_only=false steam_write=false"
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
