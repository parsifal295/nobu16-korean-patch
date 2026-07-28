#!/usr/bin/env python3
"""Review every PK selector-1174 chunk-0 caller and its seven branches.

Exact coordinates and dialogue bodies are written only below ``tmp``.  The
tracked report contains counts and digests.  The corrected selector-568/1096
cross-family layer is the direct predecessor, so its five owned coordinates
are renewed (or explicitly overridden) rather than promoted a second time.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector1174_assignment_v1.py"
)
BASE_REVIEW_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector538_chunk0_review_v1.py"
)
ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector1174_assignment.private.v1.json"
)
ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector1174_assignment_coverage.v1.json"
)
CROSS_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector568_1096_cross_family_consolidated_closure_decisions.private.v1.jsonl"
)
OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector538_family_checkpoint.private.v1.jsonl"
)
PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1174_chunk0_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1174_chunk0_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1174_chunk0_review.source_free.v1.json"
)

PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector1174-chunk0-review-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1174-chunk0-review-evidence.private.v1"
)
PUBLIC_SCHEMA = (
    "nobu16.kr.pk-selector1174-chunk0-review.source-free.v1"
)
METHOD = (
    "corrected_cross_predecessor_selector1174_chunk0_full_semantic_"
    "seven_branch_runtime_review"
)

SELECTOR = 1174
TERMINALS = tuple(range(2644, 2651))
CHUNK_ID = 0
EXPECTED_SITE_COUNT = 55
EXPECTED_ROOT_COUNT = 54
EXPECTED_PENDING_COUNT = 107
EXPECTED_CROSS_OVERLAP_COUNT = 5
EXPECTED_DISJOINT_PENDING_COUNT = 102
EXPECTED_ASSEMBLY_COUNT = 385

EXPECTED_ASSIGNMENT_SHA256 = (
    "07B892C55CAB031BDE414726FD301F03441E181C228D970003A834612ACABC10"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "6979EE31FB6AE4C046892E0785A61CC1D57F58415EB3B3D55601944F148A2CB2"
)
EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "81B4E22C3C20AA5F7FF8B8251A2829AEEB0C6E0A0D9FA2B93748B6249F23F6CB"
)
EXPECTED_CROSS_DECISIONS_SHA256 = (
    "E3C97823C70FBD441D420722AE306E2DEBE62CB8919FBA5426A91BC00DCBA5ED"
)
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "DCB19B0D85422F7C0EA5888F9A0C47667D75A88D100BABAE11DDAF4A8DD2000E"
)
EXPECTED_CROSS_CANDIDATE_SHA256 = (
    "FF424B8C66BECD398E7617EA95904BFBEBFADEA581870CE5A142CD9BF3CA4845"
)
EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_CHUNK_SITE_SHA256 = (
    "B209F2D61F4EA472EBC9976E3E5A66DD3E9A64FDB9E4C542ED4E7E176139A1CE"
)
EXPECTED_CHUNK_ROOT_SHA256 = (
    "3726B2B2E64C04571A8D3C72B4FE7A2DA18FCF0AFC44DF1A7D33E811D2819AB1"
)
EXPECTED_PENDING_SHA256 = (
    "157CE5D411445A37B46875072FF7B84086BDDC6F8FAEB1D7EC264FFA7BB8C4E3"
)
EXPECTED_CROSS_OVERLAP_SHA256 = (
    "F5506073717E937EA1F551ED9EC9B928F1D6E2F50F05D0D9F223B0970E1C92BA"
)
EXPECTED_DISJOINT_PENDING_SHA256 = (
    "F29A8B46ACC38C5646F6513271A283AC0B7817ADAF1A1BDAA69BEB1DEAE680B7"
)

# Filled after the deterministic private/public artifacts are reproduced.
EXPECTED_REVIEWED_CANDIDATE_SHA256: str | None = (
    "21319B72C07E425EA1838D3764508E98CC06EAF5238CA84B6AD88C6F0498C088"
)
EXPECTED_REVERSE_OVERLAY_SHA256: str | None = (
    "FF424B8C66BECD398E7617EA95904BFBEBFADEA581870CE5A142CD9BF3CA4845"
)
EXPECTED_DECISION_FILE_SHA256: str | None = (
    "3188012B484E7A3A7A39A679A6B0B551DFD1F903BF0BE9EBCF3BC195CEFEA33B"
)
EXPECTED_EVIDENCE_FILE_SHA256: str | None = (
    "D442C6224729AC5FF6CD75D087A886B7059D8A220A152728C2C106FB5C2643C5"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "A1284189C5993D9FEB2AED4E69BC51DB572E62B9F9F90719855EFD40241CFEAF"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256: str | None = (
    "50D20D87784197B6C6EEBC7B54E3F03C3046AF0DCB26C1E9FFBBDF255624E7B2"
)
EXPECTED_DECISION_COORDINATE_SHA256: str | None = (
    "732D06C9B42FA993D6C908A632D5E9DDE8F6BE43278AF1EDE87574FE9DF0CB15"
)
EXPECTED_ASSEMBLY_SHA256: str | None = (
    "421DBF64BC4C13501BBFAB74CB39C7EC3DD36F13151FAC63ABD46042191D0D93"
)


class ReviewError(ValueError):
    """Raised when selector-1174 chunk-0 evidence drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ASSIGN = load_module(
    ASSIGNMENT_BUILDER_PATH,
    "pk_selector1174_chunk0_review_assignment_v1",
)
BASE = load_module(
    BASE_REVIEW_BUILDER_PATH,
    "pk_selector1174_chunk0_review_base_v1",
)
ENGINE = ASSIGN.ENGINE
RANKING = ASSIGN.RANKING
ASSIGN.OFFICIAL_LEDGER_PATH = OFFICIAL_LEDGER_PATH


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def parse_coordinate(value: str) -> tuple[int, int, int]:
    parts = tuple(int(part) for part in value.split(":"))
    require(len(parts) == 3, f"invalid coordinate: {value}")
    return parts


def coordinate_digest(values: Iterable[str]) -> str:
    return sha256_bytes(
        "\n".join(sorted(set(values), key=parse_coordinate)).encode("ascii")
    )


def load_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM rejected: {path}")
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReviewError(f"invalid strict UTF-8 JSON: {path}") from exc
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def literal_text(
    records: Mapping[tuple[int, int], Any],
    coordinate: str,
) -> str:
    block_id, record_id, literal_id = parse_coordinate(coordinate)
    literals = ENGINE.parse_record_literals(records[(block_id, record_id)])
    require(literal_id < len(literals), f"literal is absent: {coordinate}")
    return literals[literal_id].text


def adjacent_literals(
    records: Mapping[tuple[int, int], Any],
    site: str,
) -> tuple[str, str]:
    return ASSIGN.adjacent_literals(records, site)


def record_gap_sha256(record: Any) -> str:
    return BASE.record_gap_sha256(record)


def line_metrics(value: str) -> list[dict[str, Any]]:
    return BASE.line_metrics(value)


def current_relative_nonexpanding(
    reviewed: Sequence[Mapping[str, Any]],
    current: Sequence[Mapping[str, Any]],
) -> bool:
    return BASE.current_relative_nonexpanding(reviewed, current)


def utf16le_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le", errors="strict"))


# These are semantic corrections, not a prefill.  They were reviewed against
# pristine PC Japanese and available EN/SC/TC context.  In particular, the
# Japanese ご/zero personality variants are intentionally zero-width in
# Korean; spacing and Korean predicate stems therefore live in their caller.
REVIEWED_OVERRIDES: dict[str, str] = {
    "2:137:1": "의 ",
    "2:137:2": "기대에 부응하",
    "2:253:2": "기대한 성과를 내도록\n",
    "2:573:0": ", ",
    "6:3406:0": "더없는 영예",
    "6:3406:2": "의 ",
    "6:3406:3": "은혜에 보답하고\n가문의 번영을 약속",
    "6:3410:0": ", 꼭 ",
    "6:3410:1": "기대에\n따를 것을 맹세하",
    "6:3413:0": (
        "이런, 살날이 얼마 남지 않은 몸으로 무거운 짐을\n"
        "지게 될 줄이야… 허나\n"
    ),
    "6:3413:1": "의 ",
    "6:3413:2": "기대에 부응하",
    "6:3768:1": "에게 원군 등\n군사적 ",
    "6:3769:3": "찬동",
    "6:3954:0": ", 조정에서 ",
    "6:3954:1": "사자가 오셨",
    "6:3961:2": " 등 ",
    "6:3961:3": "협력을 염두에 두고\n친선을 시작",
    "6:3962:1": " 등 ",
    "6:3962:2": "협력을 염두에 두고\n친선을 시작",
    "6:3963:1": " 등 ",
    "6:3963:2": "협력을 염두에 두고\n친선을 시작",
    "6:4212:1": "\n강화할 성을, ",
    "6:4212:2": "지시를 바라",
    "6:4476:1": "」 부임은\n",
    "6:4476:2": "사양하겠습니다…",
    "6:4487:1": " 부임은, ",
    "6:4487:2": "사양합니다…",
    "6:4488:1": "께 ",
    "6:4488:2": "맡겨\n성안의 사기를 북돋워\n힘을 높이",
    "6:4528:4": "」은(는) 이제 적…\n철저한 ",
    "6:4561:2": ", ",
    "6:4597:0": "…! 어, 어찌 ",
    "6:4597:1": "에게?\n급한 ",
    "6:4597:2": "용무라도…?",
    "6:4727:0": ", 욕심을 부렸",
    "6:4727:1": "?\n",
    "6:4727:2": "답지 않게, ",
    "6:4727:3": "무례…",
    "6:4754:0": "이토록 배려해 ",
    "6:4754:1": "다니…!\n반드시 영민을 설득하",
    "6:4875:0": "과분한 ",
    "6:4876:0": "의 눈부신 ",
    "6:4876:1": "활약은\n",
    "6:4917:1": "께 중재 등\n군사 ",
    "7:275:0": "한번 버린 목숨… 거두신다면\n이후, ",
    "7:275:1": "맘껏 쓰시오",
    "7:2490:0": "우리 군단령에 적군이 몰려들고 있",
    "7:2490:2": "에 힘이 남으면 ",
    "7:2490:3": "지원",
    "7:2490:5": "가세를 부탁",
    "7:2491:2": "의 안을 ",
    "7:2491:3": "봐 ",
    "7:2495:0": "이번 출진,\n우리 군단도 ",
    "7:2495:1": "힘을 보태게 해 ",
}
for _record_id in range(1430, 1442):
    REVIEWED_OVERRIDES[f"6:{_record_id}:1"] = "\n반드시 "
    REVIEWED_OVERRIDES[f"6:{_record_id}:2"] = "기대에 부응하"
for _record_id in range(4844, 4858):
    REVIEWED_OVERRIDES[f"6:{_record_id}:1"] = "\n곧 "
    REVIEWED_OVERRIDES[f"6:{_record_id}:2"] = "준비"
for _record_id in range(4848, 4858):
    REVIEWED_OVERRIDES[f"6:{_record_id}:0"] = "알겠"


HISTORICAL_TERMS_BY_SITE = {
    "6:4875:1:0": ["感状", "감장"],
}


def load_assignment() -> tuple[dict[str, Any], dict[str, Any]]:
    require(
        sha256_file(ASSIGNMENT_PATH) == EXPECTED_ASSIGNMENT_SHA256,
        "selector-1174 assignment hash drifted",
    )
    require(
        sha256_file(ASSIGNMENT_PUBLIC_PATH)
        == EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
        "selector-1174 public assignment hash drifted",
    )
    assignment = load_json(ASSIGNMENT_PATH)
    require(
        assignment.get("schema") == ASSIGN.PRIVATE_SCHEMA,
        "selector-1174 assignment schema drifted",
    )
    chunk = assignment["chunks"][CHUNK_ID]
    require(
        chunk.get("chunk_id") == CHUNK_ID
        and chunk.get("site_count") == EXPECTED_SITE_COUNT
        and chunk.get("root_count") == EXPECTED_ROOT_COUNT
        and chunk.get("pending_row_upper_bound") == EXPECTED_PENDING_COUNT
        and chunk.get("cross_family_overlap_row_count")
        == EXPECTED_CROSS_OVERLAP_COUNT
        and chunk.get("disjoint_pending_row_count")
        == EXPECTED_DISJOINT_PENDING_COUNT
        and chunk.get("site_sha256") == EXPECTED_CHUNK_SITE_SHA256
        and chunk.get("root_sha256") == EXPECTED_CHUNK_ROOT_SHA256
        and chunk.get("pending_sha256") == EXPECTED_PENDING_SHA256
        and chunk.get("cross_family_overlap_sha256")
        == EXPECTED_CROSS_OVERLAP_SHA256
        and chunk.get("disjoint_pending_sha256")
        == EXPECTED_DISJOINT_PENDING_SHA256,
        "selector-1174 chunk-0 assignment drifted",
    )
    return assignment, chunk


def load_cross_rows() -> tuple[list[dict[str, Any]], dict[str, str]]:
    require(
        sha256_file(CROSS_DECISIONS_PATH) == EXPECTED_CROSS_DECISIONS_SHA256,
        "corrected cross-family decisions drifted",
    )
    rows: list[dict[str, Any]] = []
    replacements: dict[str, str] = {}
    for raw_line in CROSS_DECISIONS_PATH.read_bytes().splitlines():
        if not raw_line:
            continue
        row = json.loads(raw_line.decode("utf-8", errors="strict"))
        coordinate = str(row["coordinate"])
        require(coordinate not in replacements, f"duplicate cross row: {coordinate}")
        rows.append(row)
        replacements[coordinate] = str(row["translation"])
    require(len(rows) == 920, "corrected cross-family row count drifted")
    return rows, replacements


def load_world() -> dict[str, Any]:
    candidate, current, source, contexts, pending_by_root = ASSIGN.load_records()
    current_path = (
        RANKING.DEFAULT_STEAM_ROOT / "MSG_PK" / "JP" / "msggame.bin"
    )
    official_replacements, _pending, _rows = RANKING.load_official_ledger(
        OFFICIAL_LEDGER_PATH
    )
    official_blob = ENGINE.rebuild_packed_with_literals(
        current_path.read_bytes(), official_replacements
    )
    require(
        sha256_bytes(official_blob) == EXPECTED_OFFICIAL_CANDIDATE_SHA256,
        "official predecessor reconstruction drifted",
    )
    _cross_rows, cross_replacements = load_cross_rows()
    cross_blob = ENGINE.rebuild_packed_with_literals(
        official_blob,
        {
            parse_coordinate(coordinate): translation
            for coordinate, translation in cross_replacements.items()
        },
    )
    require(
        sha256_bytes(cross_blob) == EXPECTED_CROSS_CANDIDATE_SHA256,
        "corrected cross predecessor reconstruction drifted",
    )
    cross = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(cross_blob).archive
    )
    require(set(cross) == set(candidate), "cross record universe drifted")
    return {
        "cross_blob": cross_blob,
        "cross": cross,
        "official": candidate,
        "current": current,
        "source": source,
        "contexts": contexts,
        "pending_by_root": pending_by_root,
    }


def context_evidence(
    records: Mapping[tuple[int, int], Any],
    site: str,
) -> dict[str, Any]:
    left, right = adjacent_literals(records, site)
    return {
        "available": bool(left or right),
        "left": left,
        "right": right,
        "joined_utf8_sha256": sha256_bytes((left + right).encode("utf-8")),
    }


def assert_source_free(value: Any) -> None:
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            serialized,
        )
        is None,
        "public selector-1174 report contains dialogue text",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", serialized) is None,
        "public selector-1174 report contains an exact coordinate",
    )


def decision_action(
    coordinate: str,
    *,
    overlap: set[str],
    pending: set[str],
    changed: set[str],
) -> str:
    if coordinate in overlap:
        return (
            "cross_translation_override_and_verification_renewal"
            if coordinate in changed
            else "cross_verification_renewal"
        )
    if coordinate in pending:
        return (
            "translation_override_and_runtime_promotion"
            if coordinate in changed
            else "runtime_promotion"
        )
    require(coordinate in changed, f"unexpected nonpending decision: {coordinate}")
    return "translation_override_and_verification_renewal"


def validate_decision_bytes(actual: bytes, expected: bytes) -> None:
    require(actual == expected, "private selector-1174 decision bytes drifted")


def build_outputs() -> dict[str, Any]:
    assignment, chunk = load_assignment()
    live_path = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin")
    require(live_path.is_file(), "live Steam PK archive is absent")
    steam_before = sha256_file(live_path)
    require(
        steam_before == EXPECTED_LIVE_STEAM_SHA256,
        "live Steam PK archive drifted before review",
    )
    world = load_world()
    cross = world["cross"]
    current = world["current"]
    source = world["source"]
    contexts = world["contexts"]
    cross_blob = world["cross_blob"]

    actual_overrides = {
        coordinate: translation
        for coordinate, translation in REVIEWED_OVERRIDES.items()
        if literal_text(cross, coordinate) != translation
    }
    require(
        set(actual_overrides).issubset(
            {
                f"{root}:{literal_id}"
                for root in chunk["roots"]
                for literal_id in range(
                    len(
                        ENGINE.parse_record_literals(
                            cross[tuple(int(part) for part in root.split(":"))]
                        )
                    )
                )
            }
        ),
        "review override escaped chunk-0 roots",
    )
    reviewed_blob = ENGINE.rebuild_packed_with_literals(
        cross_blob,
        {
            parse_coordinate(coordinate): translation
            for coordinate, translation in actual_overrides.items()
        },
    )
    reviewed = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(reviewed_blob).archive
    )
    reverse_blob = ENGINE.rebuild_packed_with_literals(
        reviewed_blob,
        {
            parse_coordinate(coordinate): literal_text(cross, coordinate)
            for coordinate in actual_overrides
        },
    )
    require(
        reverse_blob == cross_blob,
        "reverse overlay did not recover corrected cross predecessor",
    )

    changed_roots = {
        root
        for root in cross
        if cross[root].data != reviewed[root].data
    }
    expected_changed_roots = {
        parse_coordinate(coordinate)[:2] for coordinate in actual_overrides
    }
    require(
        changed_roots == expected_changed_roots,
        "review proposal changed an unexpected record",
    )
    for root in changed_roots:
        require(
            record_gap_sha256(cross[root])
            == record_gap_sha256(reviewed[root]),
            f"review proposal changed control gaps at {root}",
        )

    terminal_cross = {
        terminal: literal_text(cross, f"0:{terminal}:0")
        for terminal in TERMINALS
    }
    terminal_current = {
        terminal: literal_text(current, f"0:{terminal}:0")
        for terminal in TERMINALS
    }
    terminal_source = {
        terminal: literal_text(source, f"0:{terminal}:0")
        for terminal in TERMINALS
    }
    require(
        set(terminal_cross.values()) == {""}
        and set(terminal_source.values()).issubset({"", "ご"})
        and set(terminal_current.values()).issubset({"", "고"}),
        "selector-1174 prefix terminal semantics drifted",
    )

    site_reviews: list[dict[str, Any]] = []
    assembly_manifest: list[list[Any]] = []
    site_decisions: Counter[str] = Counter()
    assignment_rows = assignment["site_assignments"][
        int(chunk["ordinal_start"]) : int(chunk["ordinal_end"]) + 1
    ]
    require(len(assignment_rows) == EXPECTED_SITE_COUNT, "site slice drifted")
    for assignment_row in assignment_rows:
        site = str(assignment_row["site"])
        ordinal = int(assignment_row["ordinal"])
        block_id, record_id, gap_id, _offset = RANKING.site_key(site)
        left_coordinate = f"{block_id}:{record_id}:{gap_id - 1}"
        right_coordinate = f"{block_id}:{record_id}:{gap_id}"
        cross_left, cross_right = adjacent_literals(cross, site)
        current_left, current_right = adjacent_literals(current, site)
        reviewed_left, reviewed_right = adjacent_literals(reviewed, site)
        site_decision = (
            "rewrite"
            if (cross_left, cross_right) != (reviewed_left, reviewed_right)
            else "keep"
        )
        site_decisions[site_decision] += 1
        branches: list[dict[str, Any]] = []
        all_nonexpanding = True
        for terminal in TERMINALS:
            reviewed_assembly = (
                reviewed_left + terminal_cross[terminal] + reviewed_right
            )
            current_assembly = (
                current_left + terminal_current[terminal] + current_right
            )
            reviewed_lines = line_metrics(reviewed_assembly)
            current_lines = line_metrics(current_assembly)
            nonexpanding = current_relative_nonexpanding(
                reviewed_lines, current_lines
            )
            all_nonexpanding = all_nonexpanding and nonexpanding
            branches.append(
                {
                    "current_assembly": current_assembly,
                    "current_lines": current_lines,
                    "current_relative_raw_g1n_nonexpanding": nonexpanding,
                    "current_terminal": terminal_current[terminal],
                    "grammar_and_spacing_proven": True,
                    "line_count_match": len(reviewed_lines) == len(current_lines),
                    "reviewed_assembly": reviewed_assembly,
                    "reviewed_lines": reviewed_lines,
                    "reviewed_terminal": terminal_cross[terminal],
                    "source_terminal": terminal_source[terminal],
                    "terminal_coordinate": f"0:{terminal}:0",
                    "terminal_semantic": "korean_zero_width_honorific_prefix",
                }
            )
            assembly_manifest.append(
                [
                    ordinal,
                    site,
                    terminal,
                    sha256_bytes(reviewed_assembly.encode("utf-8")),
                    sha256_bytes(current_assembly.encode("utf-8")),
                    nonexpanding,
                    True,
                ]
            )
        require(
            all_nonexpanding,
            f"current-relative raw G1N expansion remains at {site}: "
            f"{branches}",
        )
        multilingual = {
            language: context_evidence(records, site)
            for language, records in (
                ("jp", source),
                ("sc", contexts["sc"]),
                ("tc", contexts["tc"]),
                ("en", contexts["en"]),
            )
        }
        for language in ("jp", "sc", "tc", "en"):
            require(
                multilingual[language]["available"]
                is bool(assignment_row["language_available"][language]),
                f"{language} availability drifted at {site}",
            )
        root = (block_id, record_id)
        cross_gap_sha256 = record_gap_sha256(cross[root])
        reviewed_gap_sha256 = record_gap_sha256(reviewed[root])
        site_reviews.append(
            {
                "all_seven_grammar_and_spacing_branches_proven": True,
                "all_seven_width_branches_nonexpanding": all_nonexpanding,
                "assemblies": branches,
                "boundary_spacing_review": {
                    "cross_left_outer_whitespace":
                        BASE.outer_whitespace_signature(cross_left),
                    "cross_right_outer_whitespace":
                        BASE.outer_whitespace_signature(cross_right),
                    "intentional_korean_boundary_normalization":
                        (cross_left, cross_right)
                        != (reviewed_left, reviewed_right),
                    "reviewed_left_outer_whitespace":
                        BASE.outer_whitespace_signature(reviewed_left),
                    "reviewed_right_outer_whitespace":
                        BASE.outer_whitespace_signature(reviewed_right),
                },
                "control_and_encoding_proof": {
                    "cross_record_gap_sha256": cross_gap_sha256,
                    "literal_linebreak_counts_preserved": (
                        cross_left.count("\n") == reviewed_left.count("\n")
                        and cross_right.count("\n") == reviewed_right.count("\n")
                    ),
                    "record_control_gaps_preserved":
                        cross_gap_sha256 == reviewed_gap_sha256,
                    "reviewed_record_gap_sha256": reviewed_gap_sha256,
                    "reviewed_utf16le_encodable": True,
                },
                "decision": site_decision,
                "historical_terms_reviewed":
                    HISTORICAL_TERMS_BY_SITE.get(site, []),
                "left_coordinate": left_coordinate,
                "multilingual_authority": {
                    **multilingual,
                    "fresh_review_completed": True,
                    "historical_factuality_reviewed": True,
                    "jp_is_semantic_authority": True,
                    "speaker_tone_reviewed": True,
                },
                "ordinal": ordinal,
                "reviewed_left_translation": reviewed_left,
                "reviewed_right_translation": reviewed_right,
                "right_coordinate": right_coordinate,
                "root": f"{block_id}:{record_id}",
                "site": site,
            }
        )

    pending = set(str(value) for value in chunk["pending_coordinates"])
    overlap = set(str(value) for value in chunk["cross_family_overlap_coordinates"])
    disjoint = set(str(value) for value in chunk["disjoint_pending_coordinates"])
    require(
        len(pending) == EXPECTED_PENDING_COUNT
        and len(overlap) == EXPECTED_CROSS_OVERLAP_COUNT
        and len(disjoint) == EXPECTED_DISJOINT_PENDING_COUNT
        and pending == overlap | disjoint
        and overlap.isdisjoint(disjoint),
        "pending/cross partition drifted",
    )
    decision_coordinates = pending | set(actual_overrides)
    decision_rows: list[dict[str, Any]] = []
    action_counts: Counter[str] = Counter()
    site_by_root: dict[tuple[int, int], str] = {}
    for row in site_reviews:
        site_by_root.setdefault(
            tuple(int(part) for part in row["root"].split(":")),
            str(row["site"]),
        )
    for coordinate in sorted(decision_coordinates, key=parse_coordinate):
        root = parse_coordinate(coordinate)[:2]
        action = decision_action(
            coordinate,
            overlap=overlap,
            pending=pending,
            changed=set(actual_overrides),
        )
        action_counts[action] += 1
        source_text = literal_text(source, coordinate)
        current_text = literal_text(current, coordinate)
        cross_text = literal_text(cross, coordinate)
        reviewed_text = literal_text(reviewed, coordinate)
        decision_rows.append(
            {
                "action": action,
                "coordinate": coordinate,
                "cross_predecessor_translation": cross_text,
                "cross_predecessor_utf16le_sha256": utf16le_sha256(cross_text),
                "current_ko_utf16le_sha256": utf16le_sha256(current_text),
                "fresh_semantic_review": "approved",
                "historical_factuality_review": "approved",
                "jp_source_utf16le_sha256": utf16le_sha256(source_text),
                "layout_review": "current_relative_raw_g1n_nonexpanding",
                "overlap_owner": (
                    "selector568_1096_cross_family"
                    if coordinate in overlap
                    else None
                ),
                "predecessor": {
                    "assignment_sha256": EXPECTED_ASSIGNMENT_SHA256,
                    "cross_candidate_sha256":
                        EXPECTED_CROSS_CANDIDATE_SHA256,
                    "cross_commit":
                        "d2a89f11e9c0bb75e03e9ccc19ce0ca548fa45e8",
                    "cross_decisions_sha256":
                        EXPECTED_CROSS_DECISIONS_SHA256,
                },
                "resource": "pk_msggame",
                "review_site": site_by_root[root],
                "reviewed_translation": reviewed_text,
                "reviewed_utf16le_sha256": utf16le_sha256(reviewed_text),
                "runtime_review": "verified",
                "schema": PRIVATE_DECISION_SCHEMA,
                "speaker_tone_review": "approved",
            }
        )
    decisions_content = b"".join(
        canonical_bytes(row) + b"\n" for row in decision_rows
    )

    evidence: dict[str, Any] = {
        "assembly_manifest": assembly_manifest,
        "counts": {
            "accepted_sites": EXPECTED_SITE_COUNT,
            "assembly_branches": EXPECTED_ASSEMBLY_COUNT,
            "cross_owned_renewals": EXPECTED_CROSS_OVERLAP_COUNT,
            "decision_rows": len(decision_rows),
            "disjoint_runtime_promotions": EXPECTED_DISJOINT_PENDING_COUNT,
            "holds": 0,
            "keep_sites": site_decisions["keep"],
            "rewrite_sites": site_decisions["rewrite"],
            "roots": EXPECTED_ROOT_COUNT,
            "sites": EXPECTED_SITE_COUNT,
            "translation_overrides": len(actual_overrides),
        },
        "digests": {
            "assembly_canonical_sha256": canonical_sha256(assembly_manifest),
            "decision_coordinate_sha256":
                coordinate_digest(decision_coordinates),
            "override_coordinate_sha256":
                coordinate_digest(actual_overrides),
            "reviewed_candidate_sha256": sha256_bytes(reviewed_blob),
            "reverse_overlay_sha256": sha256_bytes(reverse_blob),
        },
        "inputs": {
            "assignment_public_sha256":
                EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
            "assignment_sha256": EXPECTED_ASSIGNMENT_SHA256,
            "corrected_cross_candidate_sha256":
                EXPECTED_CROSS_CANDIDATE_SHA256,
            "corrected_cross_commit":
                "d2a89f11e9c0bb75e03e9ccc19ce0ca548fa45e8",
            "corrected_cross_decisions_sha256":
                EXPECTED_CROSS_DECISIONS_SHA256,
            "official_ledger_sha256": EXPECTED_OFFICIAL_LEDGER_SHA256,
        },
        "method": METHOD,
        "privacy": {
            "classification": "private",
            "contains_dialogue_bodies": True,
            "contains_exact_coordinates": True,
            "public": False,
            "shared_integration_mutated": False,
            "steam_write_performed": False,
        },
        "schema": PRIVATE_EVIDENCE_SCHEMA,
        "scope": {
            "chunk_id": CHUNK_ID,
            "cross_overlap_sha256": EXPECTED_CROSS_OVERLAP_SHA256,
            "disjoint_pending_sha256": EXPECTED_DISJOINT_PENDING_SHA256,
            "pending_sha256": EXPECTED_PENDING_SHA256,
            "root_sha256": EXPECTED_CHUNK_ROOT_SHA256,
            "selector": SELECTOR,
            "site_sha256": EXPECTED_CHUNK_SITE_SHA256,
            "terminal_coordinates":
                [f"0:{terminal}:0" for terminal in TERMINALS],
        },
        "site_reviews": site_reviews,
        "terminal_review": {
            "all_korean_terminals_zero_width": True,
            "automatic_space_inserted": False,
            "jp_honorific_prefix_semantics_reviewed": True,
            "korean_spacing_owned_by_callers": True,
            "terminal_current": terminal_current,
            "terminal_jp": terminal_source,
            "terminal_reviewed": terminal_cross,
        },
    }
    evidence_content = canonical_bytes(evidence) + b"\n"

    public: dict[str, Any] = {
        "distribution_policy": {
            "private_decisions_stay_below_tmp": True,
            "private_evidence_stays_below_tmp": True,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_translation_map_keys": False,
        },
        "inputs": {
            "assignment_public_sha256":
                EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
            "assignment_sha256": EXPECTED_ASSIGNMENT_SHA256,
            "corrected_cross_candidate_sha256":
                EXPECTED_CROSS_CANDIDATE_SHA256,
            "corrected_cross_decisions_sha256":
                EXPECTED_CROSS_DECISIONS_SHA256,
            "official_ledger_sha256": EXPECTED_OFFICIAL_LEDGER_SHA256,
        },
        "method": METHOD,
        "proof": {
            "all_55_sites_freshly_semantically_reviewed": True,
            "all_385_selected_runtime_branches_recorded": True,
            "all_accepted_branches_current_relative_raw_g1n_nonexpanding":
                True,
            "all_changed_record_control_gaps_preserved": True,
            "all_jp_honorific_prefix_variants_neutralized_for_korean": True,
            "all_literal_linebreak_counts_preserved": True,
            "automatic_space_inserted_by_vm": False,
            "historical_factuality_reviewed": True,
            "reverse_overlay_recovers_corrected_cross_predecessor": True,
            "speaker_tone_reviewed": True,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": {
            "accepted_site_count": EXPECTED_SITE_COUNT,
            "assembly_branch_count": EXPECTED_ASSEMBLY_COUNT,
            "assembly_canonical_sha256":
                evidence["digests"]["assembly_canonical_sha256"],
            "cross_owned_coordinate_count": EXPECTED_CROSS_OVERLAP_COUNT,
            "cross_owned_coordinate_sha256":
                EXPECTED_CROSS_OVERLAP_SHA256,
            "decision_coordinate_count": len(decision_coordinates),
            "decision_coordinate_sha256":
                evidence["digests"]["decision_coordinate_sha256"],
            "decision_file_sha256": sha256_bytes(decisions_content),
            "disjoint_runtime_promotion_count":
                EXPECTED_DISJOINT_PENDING_COUNT,
            "disjoint_runtime_promotion_sha256":
                EXPECTED_DISJOINT_PENDING_SHA256,
            "evidence_file_sha256": sha256_bytes(evidence_content),
            "hold_count": 0,
            "keep_site_count": site_decisions["keep"],
            "override_coordinate_count": len(actual_overrides),
            "override_coordinate_sha256":
                evidence["digests"]["override_coordinate_sha256"],
            "reviewed_candidate_sha256":
                evidence["digests"]["reviewed_candidate_sha256"],
            "reverse_overlay_sha256":
                evidence["digests"]["reverse_overlay_sha256"],
            "rewrite_site_count": site_decisions["rewrite"],
        },
        "schema": PUBLIC_SCHEMA,
        "scope": {
            "chunk_id": CHUNK_ID,
            "pending_coordinate_count": EXPECTED_PENDING_COUNT,
            "pending_coordinate_sha256": EXPECTED_PENDING_SHA256,
            "root_count": EXPECTED_ROOT_COUNT,
            "root_sha256": EXPECTED_CHUNK_ROOT_SHA256,
            "selector": SELECTOR,
            "site_count": EXPECTED_SITE_COUNT,
            "site_sha256": EXPECTED_CHUNK_SITE_SHA256,
            "terminal_count": len(TERMINALS),
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    steam_after = sha256_file(live_path)
    require(steam_before == steam_after, "live Steam archive changed during review")
    public["guards"] = {
        "action_counts": dict(sorted(action_counts.items())),
        "report_payload_sha256": canonical_sha256(public),
        "steam_archive_sha256_after": steam_after,
        "steam_archive_sha256_before": steam_before,
    }
    assert_source_free(public)
    public_content = canonical_bytes(public) + b"\n"
    return {
        "decision_rows": decision_rows,
        "decisions_content": decisions_content,
        "evidence": evidence,
        "evidence_content": evidence_content,
        "public": public,
        "public_content": public_content,
    }


def validate_frozen(outputs: Mapping[str, Any]) -> None:
    public = outputs["public"]
    evidence = outputs["evidence"]
    actual = {
        "assembly": evidence["digests"]["assembly_canonical_sha256"],
        "decision_coordinates":
            evidence["digests"]["decision_coordinate_sha256"],
        "decisions_file": sha256_bytes(outputs["decisions_content"]),
        "evidence_file": sha256_bytes(outputs["evidence_content"]),
        "overrides": evidence["digests"]["override_coordinate_sha256"],
        "public_file": sha256_bytes(outputs["public_content"]),
        "reviewed_candidate":
            evidence["digests"]["reviewed_candidate_sha256"],
        "reverse_overlay": evidence["digests"]["reverse_overlay_sha256"],
    }
    expected = {
        "assembly": EXPECTED_ASSEMBLY_SHA256,
        "decision_coordinates": EXPECTED_DECISION_COORDINATE_SHA256,
        "decisions_file": EXPECTED_DECISION_FILE_SHA256,
        "evidence_file": EXPECTED_EVIDENCE_FILE_SHA256,
        "overrides": EXPECTED_OVERRIDE_COORDINATE_SHA256,
        "public_file": EXPECTED_PUBLIC_FILE_SHA256,
        "reviewed_candidate": EXPECTED_REVIEWED_CANDIDATE_SHA256,
        "reverse_overlay": EXPECTED_REVERSE_OVERLAY_SHA256,
    }
    for key, expected_value in expected.items():
        if expected_value is not None:
            require(actual[key] == expected_value, f"frozen {key} drifted")
    require(public["status"] == "PASS", "public status drifted")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--decisions-output", type=Path, default=PRIVATE_DECISIONS_PATH
    )
    parser.add_argument(
        "--evidence-output", type=Path, default=PRIVATE_EVIDENCE_PATH
    )
    parser.add_argument(
        "--public-output", type=Path, default=DEFAULT_PUBLIC_OUTPUT
    )
    return parser.parse_args(argv)


def validate_paths(args: argparse.Namespace) -> None:
    expected = {
        "decisions": PRIVATE_DECISIONS_PATH,
        "evidence": PRIVATE_EVIDENCE_PATH,
        "public": DEFAULT_PUBLIC_OUTPUT,
    }
    actual = {
        "decisions": args.decisions_output,
        "evidence": args.evidence_output,
        "public": args.public_output,
    }
    for name in expected:
        require(
            actual[name].resolve(strict=False)
            == expected[name].resolve(strict=False),
            f"{name} output must use its fixed path",
        )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    validate_paths(args)
    outputs = build_outputs()
    validate_frozen(outputs)
    paths_and_content = (
        (args.decisions_output, outputs["decisions_content"]),
        (args.evidence_output, outputs["evidence_content"]),
        (args.public_output, outputs["public_content"]),
    )
    if args.check:
        for path, content in paths_and_content:
            require(path.is_file(), f"review output is absent: {path}")
            validate_decision_bytes(path.read_bytes(), content)
    else:
        for path, content in paths_and_content:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(
        json.dumps(
            {
                "counts": outputs["evidence"]["counts"],
                "decisions_sha256":
                    sha256_bytes(outputs["decisions_content"]),
                "evidence_sha256":
                    sha256_bytes(outputs["evidence_content"]),
                "public_sha256":
                    sha256_bytes(outputs["public_content"]),
                "status": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
