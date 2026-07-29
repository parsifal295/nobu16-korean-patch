#!/usr/bin/env python3
"""Build the wave-5 PK dialogue assignment after consolidated wave 4."""

from __future__ import annotations

import argparse
import hashlib
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
    WORKSTREAM / "build_pk_dialogue_wave_assignment_post_wave3_v1.py"
)
EXPECTED_PREDECESSOR_SHA256 = (
    "A0D5DBC6289C44E8DE88EBDE27161C7A68ED729E947E892E99B643740CE2F264"
)
RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_post292_wave4_v1.py"
)
RANKING_PRIVATE_PATH = (
    TMP
    / "pk_next_selector_family_ranking."
    "post_post292_wave4.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    PUBLIC
    / "pk_next_selector_family_ranking."
    "post_post292_wave4.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    TMP / "pk_dialogue_wave_assignment.post_selector292_wave5.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    PUBLIC / "pk_dialogue_wave_assignment.post_wave4.source_free.v1.json"
)
PACKET_DIR = TMP / "pk_dialogue_wave_post_selector292_v5"

METHOD = (
    "post_selector292_wave4_rank_order_greedy_three_way_"
    "root_terminal_and_atomic_independent_assignment"
)
WAVE_ID = "post_selector292_wave5"
EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "ranking_builder":
        "C9C283FB540888BE8897167B930FEB64552428C4BD0236EA1DE54467E67C76B6",
    "ranking_private":
        "F3F4C736EA138883D9795E6B8AFB5079FF866179AE6026002AFCDFD12B67B7FE",
    "ranking_public":
        "8031A39CC75AE935FCEAD31EBFFF7F9897776AE75A4F560F36599862C3D41797",
    "ledger":
        "BDE252E097BB1D7531F2269E0C4C105972EAEC484961E7EEEA44C0D1414C1DAE",
    "checkpoint_public":
        "FA294DE6C6B4D26F5BE6BF352D7631AB210224D6C1B95962871275011C07CAEB",
}
EXPECTED_CANDIDATE_SHA256: str | None = (
    "6D60AEEDBD22843B9AEC1DC4B1DDC3509106D6C8FC8F74FE79E4C1E3CE037836"
)
EXPECTED_SELECTED_SELECTORS: tuple[int, ...] | None = (148, 904, 724)
EXPECTED_SELECTION_RANKS: tuple[int, ...] | None = (1, 2, 3)
EXPECTED_SELECTION_PROFILE_SHA256: str | None = (
    "7EE03AA173753784828A970A2B231D779160B56935BE35F4FCE5F6F7B6B01B85"
)
EXPECTED_PACKET_SHA256: tuple[str, ...] | None = (
    "8E8D97D35CED59554381EBE3389E4340C3CBAE320C0444A96490C65A31670494",
    "40EA3DF24C4700724862A98AE485E13E4E8830E1E5663482284CAAB8026DB9AD",
    "2CE0E7562EBC9480E58F702E19FF41CB04A8F96040B6784DF01EA828D455F06F",
)
EXPECTED_PRIVATE_SHA256: str | None = (
    "B3C636F6DE8631CB72CCFA077719BD13B86339C3D3C848F50F2DBE1EF644E257"
)
EXPECTED_PUBLIC_SHA256: str | None = (
    "BB553F9EEA72EEF78F39DCD45AA792ACADE86C6E7D38C18FCAB5DE02F5BDDFD8"
)


class Wave5AssignmentError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave5AssignmentError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(PREDECESSOR_PATH, "pk_dialogue_wave5_assignment_base")
ENGINE = BASE.ENGINE
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
        hashlib.sha256(PREDECESSOR_PATH.read_bytes()).hexdigest().upper()
        == EXPECTED_PREDECESSOR_SHA256,
        "post-wave3 assignment predecessor drifted",
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
                f"wave5 output drifted: {path}",
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
