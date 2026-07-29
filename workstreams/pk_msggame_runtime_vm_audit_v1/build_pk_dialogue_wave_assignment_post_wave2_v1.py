#!/usr/bin/env python3
"""Build the wave-3 PK dialogue assignment after consolidated wave 2."""

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
    WORKSTREAM / "build_pk_dialogue_wave_assignment_post_wave1_v1.py"
)
EXPECTED_PREDECESSOR_SHA256 = (
    "AA05EEF00333DE90F86ED650E3CA77F164C3307C946FBD852CFF87F6695959E6"
)
RANKING_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_next_selector_family_ranking_post_post292_wave2_v1.py"
)
RANKING_PRIVATE_PATH = (
    TMP
    / "pk_next_selector_family_ranking."
    "post_post292_wave2.private.v1.json"
)
RANKING_PUBLIC_PATH = (
    PUBLIC
    / "pk_next_selector_family_ranking."
    "post_post292_wave2.source_free.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    TMP / "pk_dialogue_wave_assignment.post_selector292_wave3.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    PUBLIC / "pk_dialogue_wave_assignment.post_wave2.source_free.v1.json"
)
PACKET_DIR = TMP / "pk_dialogue_wave_post_selector292_v3"

METHOD = (
    "post_selector292_wave2_rank_order_greedy_three_way_"
    "root_terminal_and_atomic_independent_assignment"
)
WAVE_ID = "post_selector292_wave3"
EXPECTED_INPUT_SHA256: dict[str, str | None] = {
    "ranking_builder":
        "D1AEEB02BD36BB95BC1408BB3AAEDE59F4F6F04C95C90AF589600152E5F1FF8A",
    "ranking_private":
        "4BB7C8CF9735C8ADCA1ECFFADA5A669FD0B4EA7A050E9F9AE887F344A78E9782",
    "ranking_public":
        "FF1937BA30EC607468347BA11C3CD34C25258470AA5CBE62E3FD2A9E8FA5BE66",
    "ledger":
        "477C57FE380B20F45F5D952ED3954DE3D1F267CA2E0EA4BC5FA6E96B36877843",
    "checkpoint_public":
        "24EC33757EB877A0025F23908305D002306359DAC277D36ED85EC45EF076E21A",
}
EXPECTED_CANDIDATE_SHA256: str | None = (
    "DF91852936FFBCF0F7C9A17D4D05166A66E041F7A837E50BE600923DB8A2CA9A"
)
EXPECTED_SELECTED_SELECTORS: tuple[int, ...] | None = (1132, 1042, 274)
EXPECTED_SELECTION_RANKS: tuple[int, ...] | None = (1, 2, 5)
EXPECTED_SELECTION_PROFILE_SHA256: str | None = (
    "2BD8FBEBF92DBB9E28EC839E04A8A965A596D50F5F5D698AC79AA7D1C41D8622"
)
EXPECTED_PACKET_SHA256: tuple[str, ...] | None = (
    "19B1794A598A89858049D9E84BD481106927D8C37790FA2E179781DBB845D78A",
    "E2A0F294D96DF779805F248C5DE833BCA82D6354D57B8AD832876E5E4753BD17",
    "2035581BD25FB9473F64AC32554DE25814BF7BEB619CB7C51F57E4FA1D3BD5B4",
)
EXPECTED_PRIVATE_SHA256: str | None = (
    "DF06C2C9D0E23F4713FCD981BD2C6F757ACDAE3E2B454E5213434061DEB45909"
)
EXPECTED_PUBLIC_SHA256: str | None = (
    "969CEB961720DD36CCF0FA1F9C8182751C3B06342D7869779C6DC212B20624E1"
)


class Wave3AssignmentError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave3AssignmentError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(PREDECESSOR_PATH, "pk_dialogue_wave3_assignment_base")
CORE_BUILD_OUTPUTS = BASE.build_outputs

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
    setattr(BASE, _name, _value)


def build_outputs(
    *,
    allow_unfrozen: bool = False,
) -> tuple[bytes, bytes, dict[Path, bytes], dict[str, Any], dict[str, Any]]:
    require(
        BASE.sha256_file(PREDECESSOR_PATH) == EXPECTED_PREDECESSOR_SHA256,
        "post-wave1 assignment predecessor drifted",
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
                f"wave3 output drifted: {path}",
            )
    print(json.dumps({
        "candidate_sha256": public["guards"]["candidate_sha256"],
        "input_sha256": assignment["inputs"],
        "packet_sha256": [
            row["sha256"] for row in assignment["packet_artifacts"]
        ],
        "private_sha256":
            public["guards"]["private_assignment_sha256"],
        "public_sha256": BASE.sha256_bytes(public_bytes),
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
