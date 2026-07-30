#!/usr/bin/env python3
"""Validate selector 538 chunk 2 and build its source-free review report.

Dialogue bodies and exact maps remain in the private handoff below ``tmp``.
The reviewed chunk-1 engine is reused with a separately frozen chunk-2
contract. This builder does not mutate shared integration, progress, or Steam.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
ENGINE_PATH = WORKSTREAM / "build_pk_selector538_chunk1_review_v1.py"
ASSIGNMENT_PATH = DIALOGUE_TMP / "family538_assignment.private.v1.json"
CHUNK0_PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP / "family538_chunk0_analysis.private.v1.json"
)
CHUNK1_PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP / "family538_chunk1_analysis.private.v1.json"
)
PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP / "family538_chunk2_analysis.private.v1.json"
)
DEFAULT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector538_chunk2_review_proposal.v1.json"
)

PRIVATE_SCHEMA = "nobu16.kr.pk-selector538-chunk2-analysis.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector538-chunk2-review-proposal.v1"
METHOD = "reversed_vm_pk_selector538_chunk2_full_caller_review"
SELECTOR = 538
TERMINALS = tuple(range(1916, 1923))
ORDINAL_START = 136
ORDINAL_END = 206

EXPECTED_SITE_COUNT = 71
EXPECTED_ROOT_COUNT = 71
EXPECTED_ASSEMBLY_COUNT = 497
EXPECTED_ACCEPTED = 33
EXPECTED_REWRITE = 30
EXPECTED_KEEP = 3
EXPECTED_REJECT = 38
EXPECTED_ACCEPTED_ROOTS = 33
EXPECTED_REJECTED_ROOTS = 38
EXPECTED_ACCEPTED_ASSEMBLIES = 231
EXPECTED_REJECTED_ASSEMBLIES = 266
EXPECTED_POTENTIAL_PROMOTION_COUNT = 44
EXPECTED_BLOCKED_PENDING_COUNT = 57
EXPECTED_PROMOTION_ROOTS = 25
EXPECTED_REJECTED_PENDING_ROOTS = 32
EXPECTED_RENEWAL_ROWS = 420
EXPECTED_RENEWAL_ROOTS = 204
EXPECTED_DECISION_ROWS = 464
EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING = 8_213
EXPECTED_PENDING_AFTER = 8_169
EXPECTED_CANDIDATE_AFFECTED_ROOTS = 340
EXPECTED_SOURCE_AFFECTED_ROOTS = 405
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 36,
    "translation_override_and_runtime_promotion": 8,
    "translation_override_and_verification_renewal": 22,
    "verification_renewal": 398,
}

EXPECTED_ASSIGNMENT_SHA256 = (
    "57FBEE8EEC3551DAD8A7F1BB77CD7B2E2CF08109CB3A912452BE8244BB0FAACF"
)
EXPECTED_BASELINE_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_LEDGER_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_CHUNK0_PRIVATE_HANDOFF_SHA256 = (
    "9A8CE09CCA100FCA9C5F9C148EDA38C043D8737218F2B4A11F3CDF2B7A7A92BF"
)
EXPECTED_CHUNK1_PRIVATE_HANDOFF_SHA256 = (
    "E598C36F210BF91D02C09C6FE0BABD995212A542CACCAD60AA89CE6F91AE3E8F"
)
EXPECTED_PRIVATE_HANDOFF_SHA256 = (
    "7B01273B3DF0042DF7BF35ABDA1751EAE7B88F6890FD38E6B4C6CF1959CC4574"
)
EXPECTED_CHUNK_SITE_SHA256 = (
    "A0FD0AC632A5D15AF4F86931F5CB9FC90B984AF7CD11426CAB2C6FCD746DC5F8"
)
EXPECTED_CHUNK_ROOT_SHA256 = (
    "47D90FF70082EF798781EAD5285A862346B4181D55047D2DCA81990074A42425"
)
EXPECTED_PENDING_COORDINATE_SHA256 = (
    "A594F8E0B2BD7D4DF322DF38FDEA994C42FEA5459D5C3F3ACD0815FC87908BA7"
)
EXPECTED_PENDING_ROW_UPPER_BOUND = 101

EXPECTED_PROPOSAL_CANDIDATE_SHA256 = (
    "E5E46F9814DF6B4DE9E9293EBAF9CF8DDD14B3D48F8D60EDA838BCD1C3FC1266"
)
EXPECTED_REWRITE_COORDINATE_SHA256 = (
    "94C92DFF823518F2156E4C807B7D3B021D8F1E8BC43D06F180B917511331971B"
)
EXPECTED_KEEP_COORDINATE_SHA256 = (
    "AE2138B0EB628CACF04CF1FB8D4E96435331CB2DA5E1597B1A796A229912A7D0"
)
EXPECTED_REJECT_COORDINATE_SHA256 = (
    "87F8E6B1D1D4F284347189A541623D168636C3633E553693BD9FB69DB2DE5289"
)
EXPECTED_ACCEPTED_SITE_SHA256 = (
    "EB277A871FDD6C9C3EA7DA4A150A35B45B4CBFEF4C5086C05E05B274E83F60CE"
)
EXPECTED_REJECTED_SITE_SHA256 = (
    "E01D6C4628787C3BC61DBEA4FABB9FB67A70F47B23F2D9634EA457A4C758A777"
)
EXPECTED_ASSEMBLY_SHA256 = (
    "20A80FA5F44BBBD3A81268B42EC629265DE543356012984121687F0F6573DDB4"
)
EXPECTED_ACCEPTED_ASSEMBLY_SHA256 = (
    "3CC609B0120DF19F604EB60798C79BAE6B6FA9C9A4C302D7FF153F3E463296E9"
)
EXPECTED_ACCEPTED_ROOT_SHA256 = (
    "DE0C65372DC24CF5A904A79B64260F8E0601CD2C5C82FBC12452C7B3230D1B7E"
)
EXPECTED_REJECTED_ROOT_SHA256 = (
    "5078C4F351DC1BE4AA17385FBD256A1ECA3A16801B0A41BBDF583F7C2B61F109"
)
EXPECTED_POTENTIAL_PROMOTION_COORDINATE_SHA256 = (
    "0C740849FBDE1F4D11543471596C8FA5D7B176E97BCD12D8A8F9A99B71C0FB97"
)
EXPECTED_BLOCKED_PENDING_COORDINATE_SHA256 = (
    "9FD9765A38202A9AFD1F25C4264BF0418C90C772CE0B19B33FA51554F8F096C4"
)
EXPECTED_PREVIOUS_OVERLAP_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_PROMOTION_ROOT_SHA256 = (
    "53909755933D03B691F3FC7CAEBC455316CC61FDF2B0753A89F81ABFF571521C"
)
EXPECTED_REJECTED_PENDING_ROOT_SHA256 = (
    "982F7CC5A3ED66A9C74CC871BC6C80AC0C1E87189D714C869025C682390AE40B"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "36058C249C73F5B42C0DC7426FA68879F4BDC515F40F9C50B6CFEC07C7FD4D59"
)
EXPECTED_RENEWAL_ROOT_SHA256 = (
    "65AB478BEE4C7F7102084ACDD7D1268C33F5FE93DDA278F69DEB7D59C502AE92"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "D7DDC358689AF3B84C63AC37174552F45A7171492F92DD229C1E7C98369D81C4"
)
EXPECTED_ACTION_SHA256 = (
    "7F76E52576E972D9C87A2B75934E51B448C79E9DDD6552BC724371DC38DD534B"
)

# Frozen after the first independent write/check cycle.
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "0EFE7C538E2A966D063400CE551F8858D3A6AC5D4C5508FAC3334731AFFB460F"
)


class ReviewError(ValueError):
    """Raised when the chunk-2 review contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(
        spec is not None and spec.loader is not None,
        f"cannot import {path}",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_module(
    ENGINE_PATH,
    "pk_selector538_chunk2_review_engine_v1",
)
sha256_bytes = ENGINE.sha256_bytes
sha256_file = ENGINE.sha256_file
canonical_bytes = ENGINE.canonical_bytes
canonical_sha256 = ENGINE.canonical_sha256
coordinate_digest = ENGINE.coordinate_digest
site_digest = ENGINE.site_digest
root_digest = ENGINE.root_digest
parse_coordinate = ENGINE.parse_coordinate
site_root = ENGINE.site_root
line_metrics = ENGINE.line_metrics
current_relative_nonexpanding = ENGINE.current_relative_nonexpanding
outer_whitespace_signature = ENGINE.outer_whitespace_signature
record_gap_sha256 = ENGINE.record_gap_sha256
adjacent_literals = ENGINE.adjacent_literals
terminal_literals = ENGINE.terminal_literals
load_json_exact = ENGINE.load_json_exact
CALLER = ENGINE.CALLER
BASE_AUDIT = ENGINE.BASE_AUDIT
CLOSURE = ENGINE.CLOSURE


def load_assignment() -> tuple[dict[str, Any], dict[str, Any]]:
    require(
        sha256_file(ASSIGNMENT_PATH) == EXPECTED_ASSIGNMENT_SHA256,
        "selector 538 assignment hash drifted",
    )
    assignment = load_json_exact(ASSIGNMENT_PATH)
    chunk = assignment["chunks"][2]
    require(
        chunk.get("chunk_id") == 2
        and chunk.get("ordinal_start") == ORDINAL_START
        and chunk.get("ordinal_end") == ORDINAL_END
        and chunk.get("site_count") == EXPECTED_SITE_COUNT
        and chunk.get("root_count") == EXPECTED_ROOT_COUNT
        and chunk.get("site_sha256") == EXPECTED_CHUNK_SITE_SHA256
        and chunk.get("root_sha256") == EXPECTED_CHUNK_ROOT_SHA256
        and chunk.get("pending_coordinate_sha256")
        == EXPECTED_PENDING_COORDINATE_SHA256
        and chunk.get("pending_row_upper_bound")
        == EXPECTED_PENDING_ROW_UPPER_BOUND,
        "selector 538 chunk-2 assignment drifted",
    )
    return assignment, chunk


def patch_engine() -> None:
    values = {
        "PRIVATE_SCHEMA": PRIVATE_SCHEMA,
        "PUBLIC_SCHEMA": PUBLIC_SCHEMA,
        "METHOD": METHOD,
        "SELECTOR": SELECTOR,
        "TERMINALS": TERMINALS,
        "ORDINAL_START": ORDINAL_START,
        "ORDINAL_END": ORDINAL_END,
        "EXPECTED_SITE_COUNT": EXPECTED_SITE_COUNT,
        "EXPECTED_ROOT_COUNT": EXPECTED_ROOT_COUNT,
        "EXPECTED_ASSEMBLY_COUNT": EXPECTED_ASSEMBLY_COUNT,
        "EXPECTED_ACCEPTED": EXPECTED_ACCEPTED,
        "EXPECTED_REWRITE": EXPECTED_REWRITE,
        "EXPECTED_KEEP": EXPECTED_KEEP,
        "EXPECTED_REJECT": EXPECTED_REJECT,
        "EXPECTED_ACCEPTED_ROOTS": EXPECTED_ACCEPTED_ROOTS,
        "EXPECTED_REJECTED_ROOTS": EXPECTED_REJECTED_ROOTS,
        "EXPECTED_ACCEPTED_ASSEMBLIES": EXPECTED_ACCEPTED_ASSEMBLIES,
        "EXPECTED_REJECTED_ASSEMBLIES": EXPECTED_REJECTED_ASSEMBLIES,
        "EXPECTED_POTENTIAL_PROMOTION_COUNT":
        EXPECTED_POTENTIAL_PROMOTION_COUNT,
        "EXPECTED_BLOCKED_PENDING_COUNT":
        EXPECTED_BLOCKED_PENDING_COUNT,
        "EXPECTED_PROMOTION_ROOTS": EXPECTED_PROMOTION_ROOTS,
        "EXPECTED_REJECTED_PENDING_ROOTS":
        EXPECTED_REJECTED_PENDING_ROOTS,
        "EXPECTED_RENEWAL_ROWS": EXPECTED_RENEWAL_ROWS,
        "EXPECTED_RENEWAL_ROOTS": EXPECTED_RENEWAL_ROOTS,
        "EXPECTED_DECISION_ROWS": EXPECTED_DECISION_ROWS,
        "EXPECTED_PREDECESSOR_ROWS": EXPECTED_PREDECESSOR_ROWS,
        "EXPECTED_PREDECESSOR_PENDING": EXPECTED_PREDECESSOR_PENDING,
        "EXPECTED_PENDING_AFTER": EXPECTED_PENDING_AFTER,
        "EXPECTED_CANDIDATE_AFFECTED_ROOTS":
        EXPECTED_CANDIDATE_AFFECTED_ROOTS,
        "EXPECTED_SOURCE_AFFECTED_ROOTS":
        EXPECTED_SOURCE_AFFECTED_ROOTS,
        "EXPECTED_ACTION_COUNTS": EXPECTED_ACTION_COUNTS,
        "EXPECTED_ASSIGNMENT_SHA256": EXPECTED_ASSIGNMENT_SHA256,
        "EXPECTED_BASELINE_CANDIDATE_SHA256":
        EXPECTED_BASELINE_CANDIDATE_SHA256,
        "EXPECTED_LEDGER_SHA256": EXPECTED_LEDGER_SHA256,
        "EXPECTED_CHUNK_SITE_SHA256": EXPECTED_CHUNK_SITE_SHA256,
        "EXPECTED_CHUNK_ROOT_SHA256": EXPECTED_CHUNK_ROOT_SHA256,
        "EXPECTED_PENDING_COORDINATE_SHA256":
        EXPECTED_PENDING_COORDINATE_SHA256,
        "EXPECTED_PENDING_ROW_UPPER_BOUND":
        EXPECTED_PENDING_ROW_UPPER_BOUND,
        "EXPECTED_CHUNK0_PRIVATE_HANDOFF_SHA256":
        EXPECTED_CHUNK1_PRIVATE_HANDOFF_SHA256,
        "EXPECTED_PRIVATE_HANDOFF_SHA256":
        EXPECTED_PRIVATE_HANDOFF_SHA256,
        "EXPECTED_PROPOSAL_CANDIDATE_SHA256":
        EXPECTED_PROPOSAL_CANDIDATE_SHA256,
        "EXPECTED_REWRITE_COORDINATE_SHA256":
        EXPECTED_REWRITE_COORDINATE_SHA256,
        "EXPECTED_KEEP_COORDINATE_SHA256":
        EXPECTED_KEEP_COORDINATE_SHA256,
        "EXPECTED_REJECT_COORDINATE_SHA256":
        EXPECTED_REJECT_COORDINATE_SHA256,
        "EXPECTED_ACCEPTED_SITE_SHA256":
        EXPECTED_ACCEPTED_SITE_SHA256,
        "EXPECTED_REJECTED_SITE_SHA256":
        EXPECTED_REJECTED_SITE_SHA256,
        "EXPECTED_ASSEMBLY_SHA256": EXPECTED_ASSEMBLY_SHA256,
        "EXPECTED_ACCEPTED_ASSEMBLY_SHA256":
        EXPECTED_ACCEPTED_ASSEMBLY_SHA256,
        "EXPECTED_ACCEPTED_ROOT_SHA256":
        EXPECTED_ACCEPTED_ROOT_SHA256,
        "EXPECTED_REJECTED_ROOT_SHA256":
        EXPECTED_REJECTED_ROOT_SHA256,
        "EXPECTED_POTENTIAL_PROMOTION_COORDINATE_SHA256":
        EXPECTED_POTENTIAL_PROMOTION_COORDINATE_SHA256,
        "EXPECTED_BLOCKED_PENDING_COORDINATE_SHA256":
        EXPECTED_BLOCKED_PENDING_COORDINATE_SHA256,
        "EXPECTED_CHUNK0_OVERLAP_SHA256":
        EXPECTED_PREVIOUS_OVERLAP_SHA256,
        "EXPECTED_PROMOTION_ROOT_SHA256":
        EXPECTED_PROMOTION_ROOT_SHA256,
        "EXPECTED_REJECTED_PENDING_ROOT_SHA256":
        EXPECTED_REJECTED_PENDING_ROOT_SHA256,
        "EXPECTED_RENEWAL_COORDINATE_SHA256":
        EXPECTED_RENEWAL_COORDINATE_SHA256,
        "EXPECTED_RENEWAL_ROOT_SHA256":
        EXPECTED_RENEWAL_ROOT_SHA256,
        "EXPECTED_DECISION_COORDINATE_SHA256":
        EXPECTED_DECISION_COORDINATE_SHA256,
        "EXPECTED_ACTION_SHA256": EXPECTED_ACTION_SHA256,
        "EXPECTED_PUBLIC_FILE_SHA256": None,
        "ASSIGNMENT_PATH": ASSIGNMENT_PATH,
        "PRIVATE_HANDOFF_PATH": PRIVATE_HANDOFF_PATH,
        "CHUNK0_PRIVATE_HANDOFF_PATH": CHUNK1_PRIVATE_HANDOFF_PATH,
        "DEFAULT_OUTPUT": DEFAULT_OUTPUT,
    }
    for name, value in values.items():
        setattr(ENGINE, name, value)
    ENGINE.load_assignment = load_assignment


patch_engine()


def build_report() -> tuple[dict[str, Any], dict[str, str]]:
    report, frozen = ENGINE.build_report()
    guards = dict(report.pop("guards"))
    report["scope"]["chunk_id"] = 2
    report["inputs"].pop("chunk0_private_handoff_sha256", None)
    report["inputs"]["previous_chunk0_private_handoff_sha256"] = (
        EXPECTED_CHUNK0_PRIVATE_HANDOFF_SHA256
    )
    report["inputs"]["previous_chunk1_private_handoff_sha256"] = (
        EXPECTED_CHUNK1_PRIVATE_HANDOFF_SHA256
    )
    overlap = report["proof"].pop("chunk0_exact_map_overlap")
    report["proof"]["previous_chunk_exact_map_overlap"] = overlap
    guards["report_payload_sha256"] = canonical_sha256(report)
    report["guards"] = guards
    frozen = dict(frozen)
    frozen["previous_overlap_sha256"] = frozen.pop(
        "chunk0_overlap_sha256"
    )
    return report, frozen


def validate_frozen(frozen: Mapping[str, str]) -> None:
    expected = {
        "accepted_assembly_sha256":
        EXPECTED_ACCEPTED_ASSEMBLY_SHA256,
        "accepted_root_sha256": EXPECTED_ACCEPTED_ROOT_SHA256,
        "accepted_site_sha256": EXPECTED_ACCEPTED_SITE_SHA256,
        "action_sha256": EXPECTED_ACTION_SHA256,
        "assembly_sha256": EXPECTED_ASSEMBLY_SHA256,
        "blocked_pending_coordinate_sha256":
        EXPECTED_BLOCKED_PENDING_COORDINATE_SHA256,
        "decision_coordinate_sha256":
        EXPECTED_DECISION_COORDINATE_SHA256,
        "keep_coordinate_sha256": EXPECTED_KEEP_COORDINATE_SHA256,
        "previous_overlap_sha256": EXPECTED_PREVIOUS_OVERLAP_SHA256,
        "private_handoff_sha256": EXPECTED_PRIVATE_HANDOFF_SHA256,
        "proposal_candidate_sha256":
        EXPECTED_PROPOSAL_CANDIDATE_SHA256,
        "potential_promotion_coordinate_sha256":
        EXPECTED_POTENTIAL_PROMOTION_COORDINATE_SHA256,
        "promotion_root_sha256": EXPECTED_PROMOTION_ROOT_SHA256,
        "reject_coordinate_sha256": EXPECTED_REJECT_COORDINATE_SHA256,
        "rejected_pending_root_sha256":
        EXPECTED_REJECTED_PENDING_ROOT_SHA256,
        "rejected_root_sha256": EXPECTED_REJECTED_ROOT_SHA256,
        "rejected_site_sha256": EXPECTED_REJECTED_SITE_SHA256,
        "renewal_coordinate_sha256":
        EXPECTED_RENEWAL_COORDINATE_SHA256,
        "renewal_root_sha256": EXPECTED_RENEWAL_ROOT_SHA256,
        "rewrite_coordinate_sha256":
        EXPECTED_REWRITE_COORDINATE_SHA256,
    }
    require(frozen == expected, "frozen chunk-2 report contract drifted")


SOURCE_TEXT_RE = re.compile(
    r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7a3]"
)
SENSITIVE_KEYS = {
    "translation",
    "translations",
    "source_text",
    "current_text",
    "candidate_text",
    "assembly",
    "assemblies",
    "exact_map",
    "records",
    "sites",
    "coordinates",
}


def body_key_count(value: Any) -> int:
    if isinstance(value, Mapping):
        return sum(
            int(key in SENSITIVE_KEYS) + body_key_count(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return sum(body_key_count(child) for child in value)
    return 0


def assert_source_free(value: Any) -> None:
    require(body_key_count(value) == 0, "public report contains body key")
    if isinstance(value, Mapping):
        for child in value.values():
            assert_source_free(child)
    elif isinstance(value, list):
        for child in value:
            assert_source_free(child)
    elif isinstance(value, str):
        require(
            SOURCE_TEXT_RE.search(value) is None,
            "public report contains dialogue text",
        )


def serialized_report() -> tuple[bytes, dict[str, str]]:
    report, frozen = build_report()
    validate_frozen(frozen)
    assert_source_free(report)
    content = canonical_bytes(report) + b"\n"
    if EXPECTED_PUBLIC_FILE_SHA256 is not None:
        require(
            sha256_bytes(content) == EXPECTED_PUBLIC_FILE_SHA256,
            "public proposal file hash drifted",
        )
    return content, frozen


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    require(
        args.output.resolve() == DEFAULT_OUTPUT.resolve(),
        "custom tracked output is not allowed",
    )
    content, frozen = serialized_report()
    file_sha256 = sha256_bytes(content)
    if args.check:
        require(args.output.is_file(), f"proposal is absent: {args.output}")
        require(
            args.output.read_bytes() == content,
            "public proposal content drifted",
        )
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(content)
    print(
        json.dumps(
            {
                "file_sha256": file_sha256,
                "frozen": frozen,
                "output": str(args.output),
                "status": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
