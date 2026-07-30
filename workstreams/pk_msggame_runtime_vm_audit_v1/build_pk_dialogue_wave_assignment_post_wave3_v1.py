#!/usr/bin/env python3
"""Build the wave-4 PK dialogue assignment after consolidated wave 3."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
PUBLIC = WORKSTREAM / "public"

PREDECESSOR_PATH = (
    WORKSTREAM / "build_pk_dialogue_wave_assignment_post_wave2_v1.py"
)
EXPECTED_PREDECESSOR_SHA256 = (
    "76A1A4049AC57F1B0C6AE06B889CB4E374F86F0F91647C229593B46197E19D06"
)
RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_post292_wave3_v1.py"
)
RANKING_PRIVATE_PATH = (
    TMP
    / "pk_next_selector_family_ranking."
    "post_post292_wave3.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    PUBLIC
    / "pk_next_selector_family_ranking."
    "post_post292_wave3.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    TMP / "pk_dialogue_wave_assignment.post_selector292_wave4.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    PUBLIC / "pk_dialogue_wave_assignment.post_wave3.source_free.v1.json"
)
PACKET_DIR = TMP / "pk_dialogue_wave_post_selector292_v4"

METHOD = (
    "post_selector292_wave3_rank_order_greedy_three_way_"
    "root_terminal_and_atomic_independent_assignment"
)
WAVE_ID = "post_selector292_wave4"
EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "ranking_builder":
        "051640AEB5D0C554E695C16BC7EF521BACD24BDE115886A8B707FF91F356742A",
    "ranking_private":
        "4AEE497E71537DD8C2F6FECB8F0F30EB8E3009F6A601C74B774DDF6D84FAAAC6",
    "ranking_public":
        "C8C8C39CFAAB85DF737C0E09F3CED69187D5C41529296A156AAAA89C6E6EDBF7",
    "ledger":
        "3AEE8906C75A77C5808A28D3BAD62509BA2A32FF69C80AA68FAEA3C99CA72FDE",
    "checkpoint_public":
        "6B8E2A8701A0FE248909DE9FB0C6F9F448B4C37F98CBA47370A9F04259D30359",
}
EXPECTED_CANDIDATE_SHA256: str | None = (
    "4B2A09C787802B073109DE00B280FFC7FAB69FCF91C8D800EADCA3F072BE3C20"
)
EXPECTED_SELECTED_SELECTORS: tuple[int, ...] | None = (754, 310, 844)
EXPECTED_SELECTION_RANKS: tuple[int, ...] | None = (1, 2, 4)
EXPECTED_SELECTION_PROFILE_SHA256: str | None = (
    "DACB4567A3BE8D4DD5669B2EE882CA9DFB18F4034912C332FE9EDDFF68119299"
)
EXPECTED_PACKET_SHA256: tuple[str, ...] | None = (
    "AB48708C1303E2B4F1BB02C2CDAA4E4428AC20D33B264A11F53C4620831651A7",
    "8D5F849C6C16607618DE4E652073A438F40DB31BC6D6E361CD827E86EBACC7EB",
    "EA51A031B9951588F260AF88872DA0F3150BCA44E7B987B123AB0BA0F293575E",
)
EXPECTED_PRIVATE_SHA256: str | None = (
    "CA43DA634F5C3B7DC8F71817A92E38A01AA9004BFF45143D9A22C4B2128EDE57"
)
EXPECTED_PUBLIC_SHA256: str | None = (
    "24702F620691BED613E7C5DD13FA6BDEE1972A103A5CE62CFE24FF71D029084B"
)


class Wave4AssignmentError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave4AssignmentError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(PREDECESSOR_PATH, "pk_dialogue_wave4_assignment_base")
ENGINE = BASE.BASE
CORE_BUILD_OUTPUTS = BASE.CORE_BUILD_OUTPUTS

for _name, _value in {
    "RANKING_BUILDER_PATH": RANKING_BUILDER_PATH,
    "RANKING_PRIVATE_PATH": RANKING_PRIVATE_PATH,
    "RANKING_PUBLIC_PATH": RANKING_PUBLIC_PATH,
    "DEFAULT_PRIVATE_OUTPUT": DEFAULT_PRIVATE_OUTPUT,
    "DEFAULT_PUBLIC_OUTPUT": DEFAULT_PUBLIC_OUTPUT,
    "PACKET_DIR": PACKET_DIR,
    "METHOD": METHOD,
    "WAVE_ID": WAVE_ID,
    "EXPECTED_INPUT_SHA256": EXPECTED_INPUT_SHA256,
    "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
    "EXPECTED_SELECTED_SELECTORS": EXPECTED_SELECTED_SELECTORS,
    "EXPECTED_SELECTION_RANKS": EXPECTED_SELECTION_RANKS,
    "EXPECTED_SELECTION_PROFILE_SHA256": EXPECTED_SELECTION_PROFILE_SHA256,
    "EXPECTED_PACKET_SHA256": EXPECTED_PACKET_SHA256,
    "EXPECTED_PRIVATE_SHA256": EXPECTED_PRIVATE_SHA256,
    "EXPECTED_PUBLIC_SHA256": EXPECTED_PUBLIC_SHA256,
}.items():
    setattr(ENGINE, _name, _value)


def build_outputs(
    *,
    allow_unfrozen: bool = False,
) -> tuple[bytes, bytes, dict[Path, bytes], dict[str, Any], dict[str, Any]]:
    require(
        ENGINE.sha256_file(PREDECESSOR_PATH) == EXPECTED_PREDECESSOR_SHA256,
        "post-wave2 assignment predecessor drifted",
    )
    return CORE_BUILD_OUTPUTS(allow_unfrozen=allow_unfrozen)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--bootstrap", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    outputs = build_outputs(allow_unfrozen=args.bootstrap)
    private_bytes, public_bytes, packet_outputs, assignment, public = outputs
    output_map = {
        DEFAULT_PRIVATE_OUTPUT: private_bytes,
        DEFAULT_PUBLIC_OUTPUT: public_bytes,
        **packet_outputs,
    }
    if args.bootstrap or args.write:
        for path, content in output_map.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    else:
        for path, content in output_map.items():
            require(
                path.is_file() and path.read_bytes() == content,
                f"wave4 output drifted: {path}",
            )
    print(json.dumps({
        "candidate_sha256": public["guards"]["candidate_sha256"],
        "input_sha256": assignment["inputs"],
        "packet_sha256": [
            row["sha256"] for row in assignment["packet_artifacts"]
        ],
        "private_sha256":
            public["guards"]["private_assignment_sha256"],
        "public_sha256": ENGINE.sha256_bytes(public_bytes),
        "selection_profile_sha256":
            public["guards"]["selection_profile_sha256"],
        "selection_ranks": [
            row["rank"] for row in public["packets"]
        ],
        "selectors": [
            row["selector"] for row in public["packets"]
        ],
        "status": public["status"],
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
